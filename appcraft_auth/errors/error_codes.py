from enum import IntEnum


class AuthRelatedErrorCodes(IntEnum):
    INVALID_CREDENTIALS = 551
    ACCESS_TOKEN_IS_IN_BLACK_LIST = 552
    INVALID_ACCESS_TOKEN = 553
    INVALID_REFRESH_TOKEN = 554

    FAILED_TO_SEND_EMAIL = 555
    TOO_FREQUENT_ATTEMPTS = 556

    SMS_INVALID_CODE_OR_KEY = 557
    SMS_LIFETIME_EXPIRED = 558
    ONLY_INTEGERS_ARE_ALLOWED_IN_PHONE_NUMBER = 559
    FAILED_SEND_SMS = 560

    INVALID_VK_ACCESS_TOKEN = 561

    # UNAUTHORIZED_AUTH_PROVIDER = 555
