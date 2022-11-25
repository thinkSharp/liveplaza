import random
from odoo.tests.common import TransactionCase

def random_letters(length=10):
  return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))

def random_digits(length=10):
  return ''.join(random.choice('0123456789') for _ in range(length))

def random_email():
  return '%s@email.com' % random_letters()

def random_phone():
  return '09%s' % random_digits()


class TestAssociableToken_MultiPartner(TransactionCase):
  
  def test_00_consolidation_has_no_most_three_partner_limit(self):
    email = random_email()
    phone = random_phone()
    Partner = self.env['res.partner']
    Partner.create({
      'name': "John Doe",
      'email': email
    })
    Partner.create({
      'name': "John Doe Duplicate 1",
      'email': email,
      'phone': phone
    })
    Partner.create({
      'name': "John Doe Duplicate 2",
      'email': email,
      'phone': phone
    })
    Partner.create({
      'name': "John Doe Duplicate 3",
      'email': email,
      'phone': phone
    })

    token = Partner.get_consolidated_token(email)

    new_john_doe = Partner.search([('email', '=', email)])
    self.assertEqual(len(new_john_doe), 1)
    self.assertEqual(new_john_doe.name, "John Doe")
    self.assertEqual(new_john_doe.phone, phone)
    self.assertEqual(token, new_john_doe.signup_token)

  def test_01_consolidate_only_if_non_of_them_is_associable(self):
    email = random_email()
    Partner = self.env['res.partner']
    User = self.env['res.users']
    p_john_doe = Partner.create({
      'name': "John Doe",
      'email': email 
    })
    Partner.create({
      'name': "John Doe Duplicate",
      'email': email,
      'phone': "09457844415"
    })
    User.create({
      'name': "John Doe",
      'login': "johndoe",
      'partner_id': p_john_doe.id
    })

    token = Partner.get_consolidated_token(email)

    new_john_doe = Partner.search([('email', '=', email)])
    self.assertEqual(len(new_john_doe), 2)
    self.assertFalse(p_john_doe.phone)
    self.assertEqual(token, '')

  def test_02_empty_token_if_no_parter_matched(self):
    email = random_email()
    non_exists_email = random_email()
    Partner = self.env['res.partner']
    Partner.create({
      'name': "John Doe",
      'email': email
    })

    token = Partner.get_consolidated_token(non_exists_email)

    self.assertEqual(token, '')

  def test_03_consolidation_is_okay_for_exactly_one_match_partner(self):
    email = random_email()
    Partner = self.env['res.partner']
    p_john_doe = Partner.create({
      'name': "John Doe",
      'email': email
    })

    token = Partner.get_consolidated_token(email)

    self.assertEqual(token, p_john_doe.signup_token)

  def test_04_check_if_it_works_with_phone_number(self):
    phone = random_phone()
    Partner = self.env['res.partner']
    p_john_doe = Partner.create({
      'name': "John Doe",
      'phone': phone
    })

    token = Partner.get_consolidated_token(phone)

    self.assertEqual(token, p_john_doe.signup_token)

  def test_05_no_side_effect_for_falsy_login(self):
    email = random_email()
    Partner = self.env['res.partner']
    Partner.create({
      'name': "John Doe",
      'email': email 
    })
    Partner.create({
      'name': "John Doe Duplicate",
      'email': email,
      'phone': "09457844415"
    })

    token_1 = Partner.get_consolidated_token('')
    token_2 = Partner.get_consolidated_token(None)
    token_3 = Partner.get_consolidated_token(False)

    new_john_doe = Partner.search([('email', '=', email)])
    self.assertEqual(len(new_john_doe), 2)
    self.assertEqual(token_1, '')
    self.assertEqual(token_2, '')
    self.assertEqual(token_3, '')
