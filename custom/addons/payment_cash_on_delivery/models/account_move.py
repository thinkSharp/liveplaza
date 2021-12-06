
from odoo import api, models
import logging
_logger = logging.getLogger(__name__)

class CodAccountMove(models.Model):
    _inherit = "account.move"
    
    def _compute_amount(self):
        super(CodAccountMove,self)._compute_amount()
        for move in self.filtered(lambda  move: move.is_invoice() and move.invoice_payment_state == "paid"):
            orders = self.env["sale.order"].search([("invoice_status",'=','invoiced'),("partner_id", "=", self.partner_id.id)]).filtered(lambda order: order.name in move.invoice_origin)
            for order in orders:
                for inv in order.invoice_ids:
                    if all([inv.invoice_payment_state == "paid" for inv in order.invoice_ids]):
                        payment_transections = order.transaction_ids.filtered(
                            lambda txn: txn.state == "pending" and txn.provider == "cash_on_delivery")
                        if payment_transections:
                            payment_transections[0].state = "done"
