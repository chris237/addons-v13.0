# -*- coding: utf-8 -*-

{
    'name': 'Double Level Approval Sale',
    'version': '1.0',
    'category': '',
    'description': """ """,
    'website': 'https://www.mattobell.com',
    'summary': 'This module adds double level of approval to sale module',
    'sequence': 1,
    'depends': ['sale','stock'],
    'data': [
        'views/sale_workflow.xml',
        'new_security.xml','email_template.xml'],

    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
