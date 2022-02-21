# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    consume_material = fields.Boolean(
        help="If you mark this check, when a task goes to this state, "
        "it will consume the associated materials",
    )


class Task(models.Model):
    _inherit = "project.task"

    @api.model
    def _get_default_picking_type(self):
        picking_type = False
        if self.env.context.get("default_project_id"):
            project = self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
            picking_type = project.picking_type_id
        if not picking_type:
            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "ptm_operation"),
                    ("warehouse_id.company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
        return picking_type.id if picking_type else False

    @api.model
    def _get_default_location_source_id(self):
        location = False
        if self.env.context.get("default_project_id"):
            project = self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
            location = project.location_source_id
        if not location:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )
            location = warehouse.lot_stock_id
        return location.id if location else False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self.env.context.get("default_project_id"):
            project = self.env["project.project"].browse(
                self.env.context.get("default_project_id")
            )
            location = project.location_dest_id
        if not location:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )
            location = warehouse.lot_stock_id
        return location.id if location else False

    move_raw_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="raw_material_task_id",
        string="Stock Moves",
        copy=False,
        domain=[("scrapped", "=", False)],
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Move Analytic Account",
        help="Move created will be assigned to this analytic account",
    )
    analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        compute="_compute_analytic_line",
        string="Analytic Lines",
    )
    consume_material = fields.Boolean(related="stage_id.consume_material",)
    stock_state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("assigned", "Assigned"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_stock_state",
    )
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        domain="[('code', '=', 'ptm_operation'), ('company_id', '=', company_id)]",
        default=_get_default_picking_type,
        index=True,
        check_company=True,
    )
    location_source_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        domain="[('usage','=','internal')]",
        default=_get_default_location_source_id,
        index=True,
        check_company=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        domain="[('usage','=','internal')]",
        default=_get_default_location_dest_id,
        index=True,
        check_company=True,
    )
    unreserve_visible = fields.Boolean(
        string="Allowed to Unreserve Inventory",
        compute="_compute_unreserve_visible",
        help="Technical field to check when we can unreserve",
    )

    @api.depends("material_ids.analytic_line_id")
    def _compute_analytic_line(self):
        for task in self:
            task.analytic_line_ids = task.mapped("material_ids.analytic_line_id")

    @api.depends("move_raw_ids.state")
    def _compute_stock_state(self):
        for task in self:
            task.stock_state = "pending"
            if task.move_raw_ids:
                states = task.mapped("move_raw_ids.state")
                for state in ("confirmed", "assigned", "done", "cancel"):
                    if state in states:
                        task.stock_state = state
                        break

    @api.depends("move_raw_ids", "move_raw_ids.quantity_done")
    def _compute_unreserve_visible(self):
        for item in self:
            already_reserved = item.mapped("move_raw_ids.move_line_ids")
            any_quantity_done = any([m.quantity_done > 0 for m in item.move_raw_ids])
            item.unreserve_visible = not any_quantity_done and already_reserved

    def write(self, vals):
        res = super().write(vals)
        for task in self:
            if "stage_id" in vals or "material_ids" in vals:
                if task.consume_material:
                    todo_lines = task.material_ids.filtered(
                        lambda m: not m.stock_move_id
                    )
                    if todo_lines:
                        todo_lines.create_stock_move()
                        todo_lines.create_analytic_line()
                else:
                    if task.material_ids.mapped("analytic_line_id"):
                        raise exceptions.Warning(
                            _(
                                "You can't move to a not consume stage if "
                                "there are already analytic lines"
                            )
                        )
                    task.material_ids.mapped("analytic_line_id").unlink()
        return res

    def unlink(self):
        self.mapped("analytic_line_ids").unlink()
        return super().unlink()

    def action_assign(self):
        self.mapped("move_raw_ids")._action_assign()

    def button_scrap(self):
        self.ensure_one()
        move_items = self.move_raw_ids.filtered(
            lambda x: x.state not in ("done", "cancel")
        )
        finished_items = self.move_finished_ids.filtered(lambda x: x.state == "done")
        return {
            "name": _("Scrap"),
            "view_mode": "form",
            "res_model": "stock.scrap",
            "view_id": self.env.ref("stock.stock_scrap_form_view2").id,
            "type": "ir.actions.act_window",
            "context": {
                "default_task_id": self.id,
                "product_ids": (move_items | finished_items).mapped("product_id").ids,
                "default_company_id": self.company_id.id,
            },
            "target": "new",
        }

    def do_unreserve(self):
        for item in self:
            item.move_raw_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )._do_unreserve()
        return True

    def button_unreserve(self):
        self.ensure_one()
        self.do_unreserve()
        return True

    def action_cancel(self):
        self.move_raw_ids.write({"state": "cancel"})
        return True

    def action_done(self):
        for move in self.mapped("move_raw_ids"):
            move.quantity_done = move.reserved_availability
        self.mapped("move_raw_ids")._action_done()


class ProjectTaskMaterial(models.Model):
    _inherit = "project.task.material"

    stock_move_id = fields.Many2one(comodel_name="stock.move", string="Stock Move",)
    analytic_line_id = fields.Many2one(
        comodel_name="account.analytic.line", string="Analytic Line",
    )
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure",)
    product_id = fields.Many2one(domain="[('type', 'in', ('consu', 'product'))]")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id
        return {
            "domain": {
                "product_uom_id": [
                    ("category_id", "=", self.product_id.uom_id.category_id.id)
                ]
            }
        }

    def _prepare_stock_move(self):
        product = self.product_id
        res = {
            "raw_material_task_id": self.task_id.id,
            "picking_type_id": self.task_id.picking_type_id.id,
            "product_id": product.id,
            "name": product.partner_ref,
            "state": "confirmed",
            "product_uom": self.product_uom_id.id or product.uom_id.id,
            "product_uom_qty": self.quantity,
            "origin": self.task_id.name,
            "location_id": self.task_id.location_source_id.id,
            "location_dest_id": self.task_id.location_dest_id.id,
        }
        return res

    def create_stock_move(self):
        for line in self:
            move_id = self.env["stock.move"].create(line._prepare_stock_move())
            line.stock_move_id = move_id.id

    def _prepare_analytic_line(self):
        product = self.product_id
        company_id = self.env.company
        analytic_account = getattr(
            self.task_id, "analytic_account_id", False
        ) or getattr(self.task_id.project_id, "analytic_account_id", False)
        if not analytic_account:
            raise exceptions.Warning(
                _("You must assign an analytic account for this task/project.")
            )
        res = {
            "name": self.task_id.name + ": " + product.name,
            "ref": self.task_id.name,
            "product_id": product.id,
            "unit_amount": self.quantity,
            "account_id": analytic_account.id,
            "user_id": self._uid,
            "product_uom_id": self.product_uom_id.id,
            "company_id": analytic_account.company_id.id or self.env.company.id,
            "partner_id": self.task_id.partner_id.id
            or self.task_id.project_id.partner_id.id
            or None,
            "task_material_id": [(6, 0, [self.id])],
        }
        amount_unit = self.product_id.with_context(
            uom=self.product_uom_id.id
        ).price_compute("standard_price")[self.product_id.id]
        amount = amount_unit * self.quantity or 0.0
        result = round(amount, company_id.currency_id.decimal_places) * -1
        vals = {"amount": result}
        if "employee_id" in self.env["account.analytic.line"]._fields:
            vals["employee_id"] = (
                self.env["hr.employee"]
                .search([("user_id", "=", self.task_id.user_id.id)], limit=1)
                .id
            )
        # distributions
        distributions = self.env["account.analytic.distribution"].search(
            [("account_id", "=", analytic_account.id)]
        )
        if distributions:
            vals["tag_ids"] = [(6, 0, distributions.mapped("tag_id").ids)]
        res.update(vals)
        return res

    def create_analytic_line(self):
        for line in self:
            self.env["account.analytic.line"].create(line._prepare_analytic_line())

    def _update_unit_amount(self):
        # The analytical amount is updated with the value of the
        # stock movement, because if the product has a tracking by
        # lot / serial number, the cost when creating the
        # analytical line is not correct.
        for sel in self.filtered(
            lambda x: x.stock_move_id.state == "done"
            and x.analytic_line_id.amount != x.stock_move_id.product_id.standard_price
        ):
            sel.analytic_line_id.amount = sel.stock_move_id.product_id.standard_price

    def unlink(self):
        if self.stock_move_id:
            raise exceptions.Warning(
                _(
                    "You can't delete a consumed material if already "
                    "have stock movements done."
                )
            )
        self.analytic_line_id.unlink()
        return super().unlink()
