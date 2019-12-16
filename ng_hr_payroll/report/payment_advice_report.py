from odoo import tools
from odoo import models, fields


class payment_advice_report(models.AbstractModel):
    _name = "payment.advice.report"

    name = fields.Char(string='Name', readonly=True)
    date = fields.Date(string='Date', readonly=True,)
    year = fields.Char(string='Year', readonly=True)
    month = fields.Selection(selection=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                                        ('05', 'May'), ('06', 'June'), ('07',
                                                                        'July'), ('08', 'August'), ('09', 'September'),
                                        ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month', readonly=True)
    day = fields.Char(string='Day', readonly=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='State', index=True, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', readonly=True)
    nbr = fields.Integer(string='# Payment Lines', readonly=True)
    number = fields.Char(string='Number', readonly=True)
    bysal = fields.Float(string='By Salary', readonly=True)
    bank_id = fields.Many2one('res.bank', string='Bank', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True)
    cheque_nos = fields.Char(string='Cheque Numbers', readonly=True)
    neft = fields.Boolean(string='NEFT Transaction', readonly=True)
    ifsc_code = fields.Char(string='IFSC Code', readonly=True)
    employee_bank_no = fields.Char('Employee Bank Account', required=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'payment_advice_report')
        self._cr.execute("""
            create or replace view payment_advice_report as (
                select
                    min(l.id) as id,
                    sum(l.bysal) as bysal,
                    p.name,
                    p.state,
                    p.date,
                    p.number,
                    p.company_id,
                    p.bank_id,
                    p.chaque_nos as cheque_nos,
                    p.neft,
                    l.employee_id,
                    l.ifsc_code,
                    l.name as employee_bank_no,
                    to_char(p.date, 'YYYY') as year,
                    to_char(p.date, 'MM') as month,
                    to_char(p.date, 'YYYY-MM-DD') as day,
                    1 as nbr
                from
                    hr_payroll_advice as p
                    left join hr_payroll_advice_line as l on (p.id=l.advice_id)
                where 
                    l.employee_id IS NOT NULL
                group by
                    p.number,p.name,p.date,p.state,p.company_id,p.bank_id,p.chaque_nos,p.neft,
                    l.employee_id,l.advice_id,l.bysal,l.ifsc_code, l.name
            )
        """)