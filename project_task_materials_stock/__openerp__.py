# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Task Materials Stock',
    'summary': 'Create stock and analytic moves from '
               'record products spent in a Task',
    'version': '8.0.1.1.0',
    'category': "Project Management",
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['stock_account', 'project_task_materials'],
    'data': [
        'data/project_task_materials_data.xml',
        'views/project_view.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
