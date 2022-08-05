# -*- coding: utf-8 -*-

{
    "name":  "Picking and Delivery Vendor",
    "summary":  """Picking and delivery vendor manangement.""",
    "category":  "Contact",
    "version":  "1.0.0",
    "sequence":  100,
    "author":  "LivePlaza",
    "description":  """Vendor for Picking and Delivery
                               """,
    "depends":  [
        
        'base', 
        'resource',
        'sale', 
        'customizations_by_livep',
        'odoo_marketplace',
        'sale_stock',
        'web_domain_field'
    ],
    "data":  [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'data/scheduled_action.xml',
        'views/picking.xml',
        'views/mp_sale_order.xml',
        'views/township.xml',
        'views/delivery.xml',
        'views/mp_delivery_order.xml',
        'views/res_partner.xml',
        'views/delivery_payment.xml',
        'reports/pickup_report.xml',
        'reports/delivery_report.xml',
        'reports/report.xml',
        'reports/pickup_move_report.xml',
        'reports/delivery_move_report.xml',
        'wizards/pickup_report_wizard.xml',
        'wizards/mp_order_report_wizard_view.xml',
        'wizards/mp_delivery_collection_report_view.xml',
        'wizards/mp_delivery_vendor_receivable_view.xml',
        'wizards/mp_commission_report_wizard_view.xml',
        'wizards/mp_delivery_report_wizard_view.xml',
        'views/setting.xml'
        # Temporarily Removed
        # 'views/vendor_delivery.xml',
        # 'views/res_config.xml',
        # 'wizards/delivery_vendor_assign.xml',


    ],
    "application":  False,
    "installable":  True,
}
