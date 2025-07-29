# -*- coding: utf-8 -*-
{
    'name': "sale_custom",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/res_partner_views_new.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/quotation_report.xml',
        'reports/quotation_report_template.xml',
    ],
    'installable': True,
    'application': True,
}
