# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.scrap"

    task_id = fields.Many2one(
        comodel_name="project.task", string="Task", check_company=True
    )

    @api.onchange("task_id")
    def _onchange_task_id(self):
        if self.task_id:
            self.location_id = self.task_id.move_raw_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            ) and (
                self.task_id.location_source_id.id or self.task_id.location_dest_id.id
            )

    def _prepare_move_values(self):
        vals = super()._prepare_move_values()
        if self.task_id:
            vals["origin"] = vals["origin"] or self.task_id.name
            if self.product_id in self.task_id.move_finished_ids.mapped("product_id"):
                vals.update({"task_id": self.task_id.id})
            else:
                vals.update({"raw_material_task_id": self.task_id.id})
        return vals

    def _get_origin_moves(self):
        return super()._get_origin_moves() or (
            self.task_id
            and self.task_id.move_raw_ids.filtered(
                lambda x: x.product_id == self.product_id
            )
        )
