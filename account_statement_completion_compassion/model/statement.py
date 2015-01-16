# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools import mod10r
from openerp.tools.translate import _
from openerp import netsvc


class AccountStatement(orm.Model):

    """ Adds a relation to a recurring invoicer. """

    _inherit = 'account.bank.statement'

    _columns = {
        'recurring_invoicer_id': fields.many2one(
            'recurring.invoicer', 'Invoicer'),
    }

    def button_auto_completion(self, cr, uid, ids, context=None):
        invoicer = self.browse(cr, uid, ids[0], context).recurring_invoicer_id
        invoicer_obj = self.pool.get('recurring.invoicer')
        if invoicer:
            invoicer_id = invoicer.id
        else:
            invoicer_id = invoicer_obj.create(cr, uid, {}, context=context)
            self.write(
                cr, uid, ids, {'recurring_invoicer_id': invoicer_id},
                context=context)
            invoicer = invoicer_obj.browse(
                cr, uid, invoicer_id, context=context)

        super(AccountStatement, self).button_auto_completion(
            cr, uid, ids, context=context)

        if not invoicer.invoice_ids:
            invoicer_obj.unlink(cr, uid, invoicer_id, context=context)

    def button_invoices(self, cr, uid, ids, context=None):
        invoicer_id = self.browse(
            cr, uid, ids[0], context=context).recurring_invoicer_id.id

        return {
            'name': 'Generated Invoices',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.invoice',
            'domain': [('recurring_invoicer_id', '=', invoicer_id)],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'form_view_ref': 'account.invoice_form',
                        'journal_type': 'sale'},
        }

    def button_confirm_bank(self, cr, uid, ids, context=None):
        """Confirm invoices generated by statment lines."""
        res = super(AccountStatement, self).button_confirm_bank(cr, uid, ids,
                                                                context)
        wf_service = netsvc.LocalService('workflow')
        for statement in self.browse(cr, uid, ids, context):
            for line in statement.line_ids:
                if line.invoice_id:
                    # Validate the invoice
                    wf_service.trg_validate(
                        uid, 'account.invoice', line.invoice_id.id,
                        'invoice_open', cr)
        return res


class AccountStatementLine(orm.Model):
    """ Adds products to statement lines to generate invoices. """

    _inherit = 'account.bank.statement.line'

    _columns = {
        'product_id': fields.many2one('product.product', _('Product')),
        'contract_id': fields.many2one('recurring.contract', _('Sponsorship')),
        'invoice_id': fields.many2one('account.invoice', 'Invoice')
    }

    def write(self, cr, uid, ids, vals, context=None):
        """Generate invoice if a product is selected."""
        if 'product_id' in vals or 'contract_id' in vals:
            for line in self.browse(cr, uid, ids, context):
                # Remove old invoice
                if line.invoice_id:
                    line.invoice_id.unlink()
        res = super(AccountStatementLine, self).write(cr, uid, ids, vals,
                                                      context)
        if 'product_id' in vals or 'contract_id' in vals:
            # Generate new invoices
            [self._create_invoice_from_line(cr, uid, line, context)
             for line in self.browse(cr, uid, ids, {'lang': 'en_US'})]
        return res

    def _create_invoice_from_line(self, cr, uid, b_line, context=None):
        if not b_line.product_id:
            raise orm.except_orm(_('Missing product'),
                                 _('Please select a product'))
        # Get the attached recurring invoicer
        invoicer = b_line.statement_id.recurring_invoicer_id
        invoice_obj = self.pool.get('account.invoice')
        if not invoicer:
            invoicer_obj = self.pool.get('recurring.invoicer')
            invoicer_id = invoicer_obj.create(cr, uid, {}, context)
            b_line.statement_id.write(
                {'recurring_invoicer_id': invoicer_id})
            invoicer = invoicer_obj.browse(cr, uid, invoicer_id, context)
        # Generate a unique bvr_reference
        ref = mod10r((b_line.date.replace('-', '') + str(
            b_line.statement_id.id) + str(b_line.id)).ljust(26, '0'))
        journal_ids = self.pool.get('account.journal').search(
            cr, uid, [('type', '=', 'sale')], limit=1)

        inv_data = {
            'account_id': b_line.partner_id.property_account_receivable.id,
            'type': 'out_invoice',
            'partner_id': b_line.partner_id.id,
            'journal_id': journal_ids[0] if journal_ids else False,
            'date_invoice': b_line.date,
            'payment_term': 1,  # Immediate payment
            'bvr_reference': ref,
            'recurring_invoicer_id': invoicer.id,
        }
        if b_line.product_id.name == 'Birthday Gift' and b_line.contract_id \
                and b_line.contract_id.child_id and \
                b_line.contract_id.child_id.birthdate:
            inv_data['date_invoice'] = self.pool.get(
                'account.statement.'
                'completion.rule').compute_date_birthday_invoice(
                b_line.contract_id.child_id.birthdate, b_line.date)
        invoice_id = invoice_obj.create(cr, uid, inv_data, context)

        inv_line_data = {
            'name': b_line.name,
            'account_id': b_line.product_id.property_account_income.id,
            'price_unit': b_line.amount,
            'price_subtotal': b_line.amount,
            'contract_id': b_line.contract_id and
            b_line.contract_id.id or False,
            'quantity': 1,
            'uos_id': False,
            'product_id': b_line.product_id.id,
            'invoice_id': invoice_id,
        }
        self.pool.get('account.invoice.line').create(
            cr, uid, inv_line_data, context)

        invoice_obj.button_compute(cr, uid, [invoice_id], context)
        b_line.write({
            'ref': ref,
            'invoice_id': invoice_id})

        return True
