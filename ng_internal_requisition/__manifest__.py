{
    "name": "Internal Requisition",
    "summary": """
    This module allow user to make a request for products from the stock.""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Matt O'Bell",
    "website": "http://www.mattobell.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Productivity",
    "version": "1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "hr", "product", "stock", "purchase", "purchase_requisition"],
    # always loaded
    "data": [
        "security/internal_requisition_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/sequence.xml",
        "views/hr_department.xml",
        "views/ir_request.xml",
        "wizards/ir_request.xml",
    ],
}
