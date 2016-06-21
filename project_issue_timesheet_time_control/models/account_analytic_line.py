# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('account_id')
    def onchange_account_id(self):
        res = super(AccountAnalyticLine, self).onchange_account_id()
        domain = res.get('domain', {'issue_id': []})
        if self.issue_id.project_id.analytic_account_id != self.account_id:
            self.issue_id = False
        if self.account_id:
            project = self.env['project.project'].search(
                [('analytic_account_id', '=', self.account_id.id)], limit=1)
            domain = {'issue_id': [('project_id', '=', project.id),
                                   ('stage_id.fold', '=', False)]}
        return {'domain': domain}

    @api.onchange('issue_id')
    def onchange_issue_id(self):
        self.account_id = self.issue_id.project_id.analytic_account_id.id
