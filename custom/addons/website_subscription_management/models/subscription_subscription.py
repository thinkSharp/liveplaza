# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import models,api,fields
import logging
_logger=logging.getLogger(__name__)
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import exceptions


class subscription_subscription(models.Model):
    _inherit='subscription.subscription'

    source=fields.Selection(selection_add=[('website','Website')])
    date=datetime.today()

    date_table=None

    def get_expiry_date(self):
        Notification_day = self.sub_plan_id.notification_days #No. of days before you get notification
        if self.end_date:
            date_list = list(map(int,self.end_date.strftime("%Y-%m-%d").split("-")))
            date_N_days_ago = datetime(date_list[0],date_list[1],date_list[2]) - timedelta(days=Notification_day)
            date_table = date_N_days_ago.strftime ('%Y-%m-%d')

            condition = date_table<=datetime.now().strftime('%Y-%m-%d')
            return condition

