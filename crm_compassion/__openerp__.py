# -*- encoding: utf-8 -*-
##############################################################################
#
#       ______ Releasing children from poverty      _
#      / ____/___  ____ ___  ____  ____ ___________(_)___  ____
#     / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ ___/ / __ \/ __ \
#    / /___/ /_/ / / / / / / /_/ / /_/ (__  |__  ) / /_/ / / / /
#    \____/\____/_/ /_/ /_/ .___/\__,_/____/____/_/\____/_/ /_/
#                        /_/
#                            in Jesus' name
#
#    Copyright (C) 2014 Compassion CH (http://www.compassion.ch)
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Compassion CH - Events',
    'version': '1.1',
    'category': 'CRM',
    'sequence': 150,
    'description': """Compassion CRM - Events and Projects
==============================================================================

This module helps Compassion CH to manage its planned events, by creating a
new model for tracking upcoming events.

 * Won opportunities create automatically a new event
 * Each event is linked to a project and its analytic account
 * Each event creates a sponsorship origin
 * Portal users have an analytic account to track sponsorships gained by them
""",
    'author': 'Compassion CH',
    'website': 'http://www.compassion.ch',
    'depends': ['mail', 'base_location', 'sponsorship_compassion', 'project',
                'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_analytic_data.xml',
        'view/event_compassion_view.xml',
        'view/contract_origin_view.xml',
        'view/crm_lead_view.xml',
        'view/move_line_view.xml',
        'view/project_view.xml',
        'view/hr_timesheet_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
