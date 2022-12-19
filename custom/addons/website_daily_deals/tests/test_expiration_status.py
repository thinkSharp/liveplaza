from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase

today = datetime.today()
one_hour_delta = timedelta(hours=1)
one_day_delta = timedelta(days=1)
yesterday = today - one_day_delta
tomorrow = today + one_day_delta


class DealTestCase(TransactionCase):

  def setUp(self):
    ret = super().setUp()
    self.Deal = self.env['website.deals']
    return ret

  def _create_deal(self, start_date, end_date):
    return self.Deal.create({
      'name': "Test Deal",
      'title': "Test Deal",
      'start_date': start_date,
      'end_date': end_date,
    })


class TestExpirationStatus(DealTestCase):

  def test_starting_tomorrow_has_planned_status(self):
    test_deal = self._create_deal(tomorrow, tomorrow + one_day_delta)

    self.assertEqual(test_deal.expiration_status, 'planned')

  def test_started_yesterday_will_end_tomorrow_has_inprogress_status(self):
    test_deal = self._create_deal(yesterday, tomorrow)

    self.assertEqual(test_deal.expiration_status, 'inprogress')

  def test_ended_yesterday_has_expired_status(self):
    test_deal = self._create_deal(yesterday - one_day_delta, yesterday)

    self.assertEqual(test_deal.expiration_status, 'expired')


class TestSearchByExpirationStatus(DealTestCase):

  def setUp(self):
    ret = super().setUp()
    self.yesterday_deal = self._create_deal(yesterday, yesterday + one_hour_delta)
    self.ongoing_deal = self._create_deal(yesterday, tomorrow)
    self.tomorrow_deal = self._create_deal(tomorrow, tomorrow + one_hour_delta)
    return ret

  def test_search_planned_deals(self):
    search_result = self.Deal.search([('expiration_status', '=', 'planned')])
    self.assertNotIn(self.yesterday_deal, search_result)
    self.assertNotIn(self.ongoing_deal, search_result)
    self.assertIn(self.tomorrow_deal, search_result)

  def test_search_not_planned_deals(self):
    search_result = self.Deal.search([('expiration_status', '!=', 'planned')])
    self.assertIn(self.yesterday_deal, search_result)
    self.assertIn(self.ongoing_deal, search_result)
    self.assertNotIn(self.tomorrow_deal, search_result)

  def test_search_inprogress_deals(self):
    search_result = self.Deal.search([('expiration_status', '=', 'inprogress')])
    self.assertNotIn(self.yesterday_deal, search_result)
    self.assertIn(self.ongoing_deal, search_result)
    self.assertNotIn(self.tomorrow_deal, search_result)

  def test_search_non_inprogress_deals(self):
    search_result = self.Deal.search([('expiration_status', '!=', 'inprogress')])
    self.assertIn(self.yesterday_deal, search_result)
    self.assertNotIn(self.ongoing_deal, search_result)
    self.assertIn(self.tomorrow_deal, search_result)

  def test_search_expired_deals(self):
    search_result = self.Deal.search([('expiration_status', '=', 'expired')])
    self.assertIn(self.yesterday_deal, search_result)
    self.assertNotIn(self.ongoing_deal, search_result)
    self.assertNotIn(self.tomorrow_deal, search_result)

  def test_search_non_expired_deals(self):
    search_result = self.Deal.search([('expiration_status', '!=', 'expired')])
    self.assertNotIn(self.yesterday_deal, search_result)
    self.assertIn(self.ongoing_deal, search_result)
    self.assertIn(self.tomorrow_deal, search_result)
