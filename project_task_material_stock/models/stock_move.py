# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task for finished products",
        check_company=True,
    )
    raw_material_task_id = fields.Many2one(
        comodel_name="project.task", string="Task for components", check_company=True
    )
    is_done = fields.Boolean(
        string="Done",
        compute="_compute_is_done",
        store=True,
        help="Technical Field to order moves",
    )

    @api.depends("state")
    def _compute_is_done(self):
        for move in self:
            move.is_done = move.state in ("done", "cancel")
