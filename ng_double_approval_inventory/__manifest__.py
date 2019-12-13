# -*- coding: utf-8 -*-

{
    'name': 'Double Level Approval Inventory',
    'version': '1.0',
    'category': '',
    'description': """ """,
    'website': 'https://www.mattobell.com',
    'summary': 'This module adds double level of approval to inventory module',
    'sequence': 1,
    'depends': ['stock'],
    'data': [
        'security/new_security.xml',
        'views/inventory_workflow.xml'],
    'demo': [ ],
    'test': [ ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
