def parse_subscriber_number_mm(number: str) -> str:
  """
  Subscriber number means number without '0' prefix or 'country code' (eg. +95)
  IMPORTANT: only works for number from Myanmar

  :param number: number may or may not include prefix or country code
  :return: Subscriber number

  TODO: we might want to recosider is '95' without plus valid or not,
    '95' could've become a start of valid subscriber number, even though, have not yet
    eg. ooredoo - 099
        telenor - 097
  """
  if number.startswith("0"):
    return number[1:]
  elif number.startswith("95"):
    return number[2:]
  elif number.startswith("+95"):
    return number[3:]
