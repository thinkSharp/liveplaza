{
    'name': 'Sale Custom',
    'category': 'Sale',
    'summary': 'Sale Customization',
    'author': "SSP Venture Co.ltd",
    
    
    'version': '1',

    'depends': [
        'sale',
        'website_sale',
        'base',
        'customizations_by_livep'
        
    ],
    'data': [
        
        'views/sale_views.xml',
        'views/res_partner_view.xml'
       
        
    ],
    'installable': True,
    'auto_install': False,
}
