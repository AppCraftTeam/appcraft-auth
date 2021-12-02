from enum import IntEnum

from rest_framework.exceptions import APIException


class CustomAPIException(APIException):

    def __init__(self, error: IntEnum):
        self.detail, self.status_code = self.convert_enum(error=error)
        super(CustomAPIException, self).__init__(self.detail, self.status_code)

    @staticmethod
    def convert_enum(error: IntEnum):
        detail = error.name.lower().replace('_', ' ')
        status_code = error.value
        return detail, status_code
