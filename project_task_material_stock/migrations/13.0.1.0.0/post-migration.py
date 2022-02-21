# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    picking_type = env.ref(
        "project_task_material_stock.project_task_material_picking_type"
    )
    picking_type.write({"code": "project_task_material_operation"})
    picking_type.warehouse_id.write({"ptm_type_id": picking_type.id})
