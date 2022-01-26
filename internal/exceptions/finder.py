from .api_exception import APIException
from .objects.email_not_registered import EmailNotRegistered
from .objects.invalid_email import InvalidEmail
from .objects.incorrect_password import IncorrectPassword
from .objects.incorrect_verification_code import IncorrectVerificationCode
from .objects.bad_device_id import BadDeviceId
from .objects.unsupported_service import UnsupportedService
from .objects.you_cant_register_now import YouCantRegisterNow
from .objects.captcha_caught import CaptchaCaught

codes = {
    2009: EmailNotRegistered,
    2022: InvalidEmail,
    2010: IncorrectPassword,
    2005: IncorrectVerificationCode,
    2007: BadDeviceId,
    1006: UnsupportedService,
    2063: YouCantRegisterNow,
    1008: CaptchaCaught
}


def get_exception(response: dict) -> Exception:
    if response["apiCode"] in codes:
        exception = codes[response["apiCode"]]
        if exception is CaptchaCaught:
            return exception(
                code=response["apiCode"],
                message=response["apiMsg"],
                url=response["redirectUrl"]
            )
        return exception(
            code=response["apiCode"],
            message=response["apiMsg"]
        )
    return APIException(
        response["apiCode"],
        response["apiMsg"]
    )
