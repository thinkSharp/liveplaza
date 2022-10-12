{
    'name': 'Report Customization',
    'version': '1.0',
    'category': 'Report',
    'summary': 'Report Customization',
    'description': """
Report Customization Module.
    """,
    'depends': [
                'web',
                'sale',
                'stock'
                ],
    'data': [
        # 'views/report_templates.xml',
        # 'views/sale_report_templates.xml'
        # 'views/sale_report_template_inherit.xml',
        'views/new_sale_report_template.xml',
        'views/new_sale_report_template_A5.xml',
        'views/new_sale_report_template_A6.xml',
        'views/delivery_slip_inherit.xml',
        'views/external_layout.xml'


    ],
    "external_dependencies": {},
    'installable': True,
    'auto_install': False
}
