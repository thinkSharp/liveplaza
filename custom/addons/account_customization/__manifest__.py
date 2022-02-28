{
    'name': 'Account Custom',
    'category': 'Account',
    'summary': 'Accounting Customization',
    'author': "SSP Venture Co.ltd",
    
    
    'version': '1',

    'depends': [
        'account',
        
    ],
    'data': [
        
        'views/account_move_view.xml',
        'views/account_payment_view.xml'
        
    ],
    'installable': True,
    'auto_install': False,
}
