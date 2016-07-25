# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    task_materials_location_src_id = fields.Many2one(
        comodel_name='stock.location',
        string="Task Materials Location Source")
    task_materials_location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string="Task Materials Location Destine")
    task_materials_analytic_journal_id = fields.Many2one(
        comodel_name='account.analytic.journal',
        string="Task Materials Analytic Journal")


class ProjectConfigSettings(models.TransientModel):
    _inherit = 'project.config.settings'

    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'project.project'))
    task_materials_location_src_id = fields.Many2one(
        related='company_id.task_materials_location_src_id')
    task_materials_location_dest_id = fields.Many2one(
        related='company_id.task_materials_location_dest_id')
    task_materials_analytic_journal_id = fields.Many2one(
        related='company_id.task_materials_analytic_journal_id')
