# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    ptm_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Project Task Material Operation Type",
        domain="[('code', '=', 'ptm_operation'), ('company_id', '=', company_id)]",
        check_company=True,
    )

    def _get_sequence_values(self):
        values = super()._get_sequence_values()
        values.update(
            {
                "ptm_type_id": {
                    "name": self.name + " " + _("Sequence production"),
                    "prefix": self.code + "/PTMO/",
                    "padding": 5,
                    "company_id": self.company_id.id,
                },
            }
        )
        return values

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super()._get_picking_type_create_values(max_sequence)
        data.update(
            {
                "ptm_type_id": {
                    "name": _("Project Task Material"),
                    "code": "ptm_operation",
                    "use_create_lots": True,
                    "use_existing_lots": True,
                    "sequence": next_sequence + 2,
                    "sequence_code": "PTMO",
                    "company_id": self.company_id.id,
                },
            }
        )
        return data, max_sequence + 2

    def _get_picking_type_update_values(self):
        data = super()._get_picking_type_update_values()
        data.update(
            {
                "manu_type_id": {
                    "active": self.active,
                    "default_location_src_id": self.lot_stock_id.id,
                    "default_location_dest_id": self.lot_stock_id.id,
                },
            }
        )
        return data
