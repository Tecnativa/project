# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import Form, common


class TestProjectTaskMaterialAnalytic(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "standard_price": 100}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test account"}
        )
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "analytic_account_id": cls.analytic_account.id}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.analytic_line_model = cls.env["account.analytic.line"]

    def _create_task(self):
        task_form = Form(self.env["project.task"])
        task_form.name = "Test task"
        task_form.project_id = self.project
        task_form.partner_id = self.partner
        with task_form.material_ids.new() as material_form:
            material_form.product_id = self.product
            material_form.quantity = 2
        return task_form.save()

    def test_project_task_analytic_misc(self):
        task = self._create_task()
        material_task = fields.first(task.material_ids)
        self.assertEqual(material_task.analytic_line_id.product_id, self.product)
        self.assertEqual(material_task.analytic_line_id.partner_id, self.partner)
        self.assertEqual(
            material_task.analytic_line_id.account_id, self.analytic_account
        )
        self.assertEqual(material_task.analytic_line_id.unit_amount, 2)
        self.assertEqual(material_task.analytic_line_id.amount, -200)
        material_task.write({"quantity": 3})
        self.assertEqual(material_task.analytic_line_id.unit_amount, 3)
        self.assertEqual(material_task.analytic_line_id.amount, -300)

    def test_project_task_material_unlink(self):
        self.analytic_line_model.search([]).unlink()
        task = self._create_task()
        self.assertAlmostEqual(self.analytic_line_model.search_count([]), 1)
        task.material_ids.unlink()
        self.assertAlmostEqual(self.analytic_line_model.search_count([]), 0)
