# Copyright 2015 Tecnativa - Sergio Teruel
# Copyright 2015 Tecnativa - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_default_picking_type(self):
        return (
            self.env["stock.picking.type"]
            .search(
                [
                    ("code", "=", "ptm_operation"),
                    ("warehouse_id.company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            .id
        )

    @api.model
    def _get_default_location_source_id(self):
        location = False
        if self.env.context.get("default_picking_type_id"):
            picking_type = self.env["stock.picking.type"].browse(
                self.env.context.get("default_picking_type_id")
            )
            location = picking_type.default_location_src_id
        if not location:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )
            location = warehouse.lot_stock_id
        return location.id if location else False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self.env.context.get("default_picking_type_id"):
            picking_type = self.env["stock.picking.type"].browse(
                self.env.context.get("default_picking_type_id")
            )
            location = picking_type.default_location_dest_id
        if not location:
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", self.env.company.id)], limit=1
            )
            location = warehouse.lot_stock_id
        return location.id if location else location

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
        default=_get_default_location_source_id,
        domain="[('usage','=','internal')]",
        check_company=True,
        index=True,
        help="Default location from which materials are consumed.",
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        default=_get_default_location_dest_id,
        domain="[('usage','=','internal')]",
        index=True,
        check_company=True,
        help="Default location to which materials are consumed.",
    )
