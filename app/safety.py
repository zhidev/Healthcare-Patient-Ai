"""Phone-number safety guard for outbound calls."""

import re


"""PGAI phone approved number"""
APPROVED_TEST_NUMBER = "+18054398008"


class UnsafePhoneNumberError(ValueError):
    """Raised when an outbound phone number is not approved."""


def normalize_phone_number(phone_number: str) -> str:
    """Normalize a phone number into E.164-like format. Use phonenumbers library later"""
    digits = re.sub(r"\D", "", phone_number)

    if len(digits) == 10:
        digits = "1" + digits

    return f"+{digits}"


def assert_allowed_number(phone_number: str) -> str:
    """Allow only the approved assessment test number."""
    normalized_number = normalize_phone_number(phone_number)

    if normalized_number != APPROVED_TEST_NUMBER:
        raise UnsafePhoneNumberError(
            f"Blocked outbound call to {normalized_number}. "
            f"Only {APPROVED_TEST_NUMBER} is allowed."
        )

    return normalized_number