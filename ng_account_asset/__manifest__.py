{
    'name': 'Improvements on Assets Management',
    'version': '1.0',
    'depends': ['om_account_asset', 'purchase', 'account', 'account_accountant'],
    'author': 'Mattobell',
    'website': 'http://www.mattobell.com',
    'description': '''
More Asset Management Features
==============================
This module is developed for asset management in terms of Additions, Maintenance, Disposals, Repairs management for assets.

    ''',
    'category': 'Accounting & Finance',
    'sequence': 70,
    'data': [
        # 'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'report/disposal_report_reg.xml',
        'report/disposal_report_view.xml',
        'wizard/invoice_disposal_view.xml',
        'wizard/ng_disposal_report_wiz_view.xml',
        # 'views/ng_account_asset_view.xml',
        # 'views/ng_account_asset_disposal_view.xml',
        # 'views/ng_account_asset_maintanance_view.xml',
        # 'views/account_asset_po_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
