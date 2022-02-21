# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ("project.task", "project_task", "stock_move_ids", "move_raw_ids"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
    openupgrade.logged_query(
        env.cr,
        """UPDATE stock_move
        SET raw_material_task_id = ptm.task_id
        FROM project_task_material AS ptm
        JOIN stock_move AS sm ON ptm.stock_move_id = sm.id
        WHERE ptm.stock_move_id IS NOT NULL""",
    )
