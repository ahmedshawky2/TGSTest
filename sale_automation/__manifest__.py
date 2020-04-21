# -*- coding: utf-8 -*-
{
    'name': "sale_automation",

    'summary': """
        Automate full cycle of creating sales orders, validate delivery, creating invoices & register payment""",

    'description': """
        - Creating quotation orders
        - Confirm sales orders
        - Validate delivery
        - Create invoices
        - Validate invoices
        - Register Payment
    """,

    'author': "Minds Solutions",
    'website': "http://www.mindseg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/ir_actions_act_window.xml',
        'views/ir_ui_menu.xml',
        'views/log_sale_automation.xml',
        'views/sale_automation.xml',
        'views/ir_model_access.xml',
        'data/sequence.xml',
    ],
    'installable':True,
    'application': True,
    # only loaded in demonstration mode
}