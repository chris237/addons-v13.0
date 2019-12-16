{
    'name': "Leave Approval Management Module",

    'summary': """
        Manages the application and approval of leave requests""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Matt O'Bell",
    'website': "https://www.mattobell.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_holidays',
    ],

    # always loaded
    'data': [
        'security/hr_holiday_rule.xml',
        'views/views.xml',
        'data/approve_email.xml',
    ],

    'installable': True,

    'auto_install': False,
}
