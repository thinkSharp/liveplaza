import pyotp


class OTP:

    def __init__(self, secret):
        self.secret = secret
        self.totp = pyotp.TOTP(self.secret)

    def verify(self, code):
        return self.totp.verify(str(code))

    def uri(self, name, issuer_name="Live Plaza"):
        return self.totp.provisioning_uri(name=name, issuer_name=issuer_name)

    @classmethod
    def new(cls):
        return cls(pyotp.random_base32())