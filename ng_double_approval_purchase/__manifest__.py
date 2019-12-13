# -*- coding: utf-8 -*-

{
    'name': 'Double Level Approval Purchase',
    'version': '1.0',
    'category': '',
    'description': """ """,
    'website': 'https://www.mattobell.com',
    'summary': 'This module adds double level of approval to purchase module',
    'sequence': 1,
    'depends': ['purchase','stock'],
    'data': [
        'new_security.xml',
        'views/purchase_workflow.xml','email_template.xml'],
    'demo': [ ],
    'test': [ ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
