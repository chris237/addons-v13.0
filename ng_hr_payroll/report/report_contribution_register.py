import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models


class contribution_register_report(models.AbstractModel):
    _name = "report.ng_hr_payroll.contribution_register_mod_report"

    def set_context(self, objects, data, ids, report_type=None):
        self.date_from = data['form'].get(
            'date_from', time.strftime('%Y-%m-%d'))
        self.date_to = data['form'].get('date_to', str(
            datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
        self.employee = data['form'].get('employee_ids', [])
        if not self.employee:
            self.employee = self.env['hr.employee'].search([])
        return super(contribution_register_report, self).set_context(objects, data, ids, report_type=report_type)

    def sum_total(self):
        return self.regi_total

    def _get_objects(self):
        return self.env['hr.contribution.register'].browse(self.localcontext['data']['ids'])

    def _get_payslip_lines(self, obj, data):
        payslip_obj = self.env['hr.payslip']
        payslip_line = self.env['hr.payslip.line']
        payslip_lines = []
        res = []
        self.regi_total = 0.0
        self._cr.execute("SELECT pl.id from hr_payslip_line as pl "
                         "LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id) "
                         "WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "
                         "AND pl.register_id = %s "
                         "AND hp.state = 'done' "
                         "AND hp.employee_id in %s "
                         "ORDER BY pl.slip_id, pl.sequence",
                         (data['date_from'], data['date_to'], obj.id, tuple(data['employee_ids'])))
        payslip_lines = [x[0] for x in self._cr.fetchall()]
        for line in payslip_line.browse(payslip_lines):
            #            if not line.total == 0.0:
            res.append({
                'payslip_name': line.slip_id.employee_id.name,
                'name': line.name,
                'code': line.code,
                'quantity': line.slip_id.number,
                'amount': line.amount,
                'total': line.total,
            })
            self.regi_total += line.total
        return res

    @api.model
    def render_html(self, docids, data=None):
        docids = data['ids']
        docs = self.env[data['model']].browse(docids)
        docargs = {
            'get_payslip_lines': self._get_payslip_lines,
            'sum_total': self.sum_total,
            'get_objects': self._get_objects,
            'doc_ids': docids,
            'doc_model': data['model'],
            'docs': docs,
            'data': data,
            'company': self.env.user.company_id
        }
        return self.env['report'].render('ng_hr_payroll.contribution_register_mod_report', values=docargs)