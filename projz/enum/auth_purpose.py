from enum import Enum


class AuthPurpose(Enum):
    LOGIN = 1
    CHANGE_EMAIL = 3
    CHANGE_PHONE_NUMBER = 4
    ACTIVATE_WALLET = 5
    RECOVERY_PAYMENT_PASSWORD = 7
