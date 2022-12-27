from datetime import date, timedelta
from odoo.tests.common import TransactionCase

today = date.today()
one_day_delta = timedelta(days=1)
yesterday = today - one_day_delta
tomorrow = today + one_day_delta


class DealTestCase(TransactionCase):

  def setUp(self):
    ret = super().setUp()
    self.Deal = self.env['website.deals']
    return ret

  def _create_deal(self, start_date, end_date, **kwargs):
    props = {
      'name': "Test Deal",
      'title': "Test Deal",
      'start_date': start_date,
      'end_date': end_date,
    }
    props.update(kwargs)
    return self.Deal.create(props)


class TestExpirationStatus(DealTestCase):

  def test_starting_tomorrow_has_planned_status(self):
    test_deal = self._create_deal(tomorrow, tomorrow + one_day_delta)

    self.assertEqual(test_deal.expiration_status, 'planned')

  def test_started_yesterday_will_end_tomorrow_has_inprogress_status(self):
    test_deal = self._create_deal(yesterday, tomorrow)

    self.assertEqual(test_deal.expiration_status, 'inprogress')

  def test_started_today_will_end_today_has_inprogress_status(self):
    test_deal = self._create_deal(today, today)

    self.assertEqual(test_deal.expiration_status, 'inprogress')

  def test_ended_yesterday_has_expired_status(self):
    test_deal = self._create_deal(yesterday - one_day_delta, yesterday)

    self.assertEqual(test_deal.expiration_status, 'expired')


class TestSearchByExpirationStatus(DealTestCase):

  def setUp(self):
    ret = super().setUp()
    self.yesterday_deal = self._create_deal(yesterday, yesterday)
    self.ongoing_deal = self._create_deal(yesterday, tomorrow)
    self.tomorrow_deal = self._create_deal(tomorrow, tomorrow)
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


class TestQueryValidDeals(DealTestCase):

  def setUp(self):
    ret = super().setUp()
    self.expired_deal = self._create_deal(yesterday, yesterday, state='validated')
    self.expired_homepage_deal = self._create_deal(yesterday, yesterday, state='validated', display_on_homepage=True)
    self.expired_but_blur_deal = self._create_deal(yesterday, yesterday, state='validated', d_state_after_expire='blur')
    self.ongoing_deal = self._create_deal(yesterday, tomorrow, state='validated')
    self.ongoing_homepage_deal = self._create_deal(yesterday, tomorrow, state='validated', display_on_homepage=True)
    self.ongoing_but_not_validated_deal = self._create_deal(yesterday, tomorrow, state='pending')
    self.planned_deal = self._create_deal(tomorrow, tomorrow, state='validated')
    return ret

  def test_query_valid_deals(self):
    valid_deals = self.Deal.get_valid_deals()
    self.assertNotIn(self.expired_deal, valid_deals)
    self.assertIn(self.expired_but_blur_deal, valid_deals)
    self.assertIn(self.ongoing_deal, valid_deals)
    self.assertIn(self.ongoing_homepage_deal, valid_deals)
    self.assertNotIn(self.ongoing_but_not_validated_deal, valid_deals)
    self.assertNotIn(self.planned_deal, valid_deals)

  def test_query_homepage_deals(self):
    homepage_deals = self.Deal.get_homepage_deals()
    self.assertNotIn(self.ongoing_deal, homepage_deals)
    self.assertIn(self.ongoing_homepage_deal, homepage_deals)
    self.assertNotIn(self.expired_deal, homepage_deals)
    self.assertNotIn(self.expired_homepage_deal, homepage_deals)
