from odoo import api, models, fields, tools, _


class SellerPaymentReport(models.Model):
    _name = 'seller.payment.report'
    _description = 'Seller Payment Report'
    _order = 'date desc'
    _auto = False

    id = fields.Integer('ID')
    seller_id = fields.Many2one('res.partner', 'Seller', ondelete='cascade')
    date = fields.Date('Payment Date')
    memo = fields.Char('Memo')
    payable_amount = fields.Float('Amount')
    currency_id = fields.Many2one('res.currency', 'Currency', ondelete='cascade')    

    def init(self):
        print("Connected")
        tools.drop_view_if_exists(self._cr, 'seller_payment_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW seller_payment_report AS (
                SELECT sp.id as id,
                sp.seller_id as seller_id,
                sp.date as date,
                sp.memo as memo,
                sp.payable_amount as payable_amount,
                sp.currency_id as currency_id
                FROM seller_payment sp
            )""")

