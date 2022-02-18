# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    analytic_line_id = fields.Many2one(comodel_name="account.analytic.line",)

    def _prepare_account_analytic_line(self, vals):
        task = self.env["project.task"].browse(vals.get("task_id"))
        product = self.env["product.product"].browse(vals.get("product_id"))
        return {
            "name": "{} - {}".format(task.name, product.name),
            "account_id": task.project_id.analytic_account_id.id,
            "partner_id": task.partner_id.id or False,
            "date": fields.date.today(),
            "product_id": product.id,
            "unit_amount": vals.get("quantity", 1),
        }

    def _sync_account_analytic_lines(self):
        for item in self.filtered("analytic_line_id"):
            item.analytic_line_id.update(
                {"product_id": item.product_id, "unit_amount": item.quantity}
            )
            item.analytic_line_id.on_change_unit_amount()

    @api.model_create_multi
    def create(self, vals_list):
        analytic_line_model = self.env["account.analytic.line"]
        for vals in vals_list:
            if not vals.get("analytic_line_id"):
                task = self.env["project.task"].browse(vals.get("task_id"))
                if task.project_id.analytic_account_id:
                    analytic_line = analytic_line_model.create(
                        self._prepare_account_analytic_line(vals)
                    )
                    analytic_line.on_change_unit_amount()
                    vals["analytic_line_id"] = analytic_line.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if vals.get("product_id") or vals.get("quantity"):
            self._sync_account_analytic_lines()
        return res

    def unlink(self):
        self.mapped("analytic_line_id").unlink()
        return super().unlink()
