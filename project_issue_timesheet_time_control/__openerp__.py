# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project issue timesheet time control',
    'version': '9.0.1.0.0',
    'category': 'Project Management',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'project_timesheet_time_control',
        'project_issue_sheet',
    ],
    'data': [
        'views/project_issue_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
}
