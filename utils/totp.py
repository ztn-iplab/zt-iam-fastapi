import pyotp

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, email, issuer="ZTN_MOMO_SIM"):
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

def verify_totp_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
