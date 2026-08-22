import unittest

from modules.core.common.phone_number import PhoneNumber
from modules.core.common.types import PhoneNumberErrorCode
from modules.core.errors import MalformedPhoneNumberError


class TestPhoneNumber(unittest.TestCase):
    def test_from_dict_builds_a_phone_number(self) -> None:
        phone_number = PhoneNumber.from_dict({"country_code": "+91", "phone_number": "9999999999"})

        assert phone_number == PhoneNumber(country_code="+91", phone_number="9999999999")

    def test_str_joins_the_country_code_and_the_number(self) -> None:
        assert str(PhoneNumber(country_code="+91", phone_number="9999999999")) == "+91 9999999999"

    def test_from_dict_rejects_a_non_object(self) -> None:
        with self.assertRaises(MalformedPhoneNumberError) as context:
            PhoneNumber.from_dict("not_an_object")

        assert context.exception.code == PhoneNumberErrorCode.MALFORMED
        assert context.exception.http_code == 400

    def test_from_dict_rejects_a_missing_country_code(self) -> None:
        with self.assertRaises(MalformedPhoneNumberError) as context:
            PhoneNumber.from_dict({"phone_number": "9999999999"})

        assert context.exception.code == PhoneNumberErrorCode.MALFORMED

    def test_from_dict_rejects_a_non_string_number(self) -> None:
        with self.assertRaises(MalformedPhoneNumberError) as context:
            PhoneNumber.from_dict({"country_code": "+91", "phone_number": 9999999999})

        assert context.exception.code == PhoneNumberErrorCode.MALFORMED
