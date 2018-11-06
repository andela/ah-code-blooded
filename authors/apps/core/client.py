import os


def get_domain():
    return os.getenv("CLIENT_DOMAIN")


def get_password_reset_link(token):
    return "{}/{}?token={}".format(get_domain(), os.getenv("CLIENT_RESET_PASSWORD_ROUTE"), token)
