# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('issue_id')
    def onchange_issue_id(self):
        if self.issue_id.project_id:
            self.account_id = self.issue_id.project_id.analytic_account_id.id
