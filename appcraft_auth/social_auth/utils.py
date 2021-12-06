__all__ = ['map_vk_gender']

from appcraft_auth.social_auth.enums import VKGenderEnum


def map_vk_gender(vk_gender_enum_value, Genders):
    '''
    maps gender enum value from VK to gender enum value of AuthUserModel.

    `Genders` must be AuthUserModel.Gender!
    '''
    map = {
        VKGenderEnum.NOT_SPECIFIED: Genders.OTHER,
        VKGenderEnum.FEMALE: Genders.WOMAN,
        VKGenderEnum.MALE: Genders.MAN,
    }
    return map[vk_gender_enum_value]
