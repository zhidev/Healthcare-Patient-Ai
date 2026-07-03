"""Tests for phone-number safety guard."""

import pytest

from app.safety import UnsafePhoneNumberError, assert_allowed_number

APPROVED_TEST_NUMBER_FAKE = "+18001231234"


def test_approved_number_is_allowed():
    """Approved assessment number should be allowed."""
    result = assert_allowed_number("+1-805-439-8008")

    assert result == "+18054398008"
    # result = assert_allowed_number("+1-800-123-1234")

    # assert result == "+18001231234"


def test_approved_number_without_country_code_is_allowed():
    """Approved number without +1 should still normalize correctly."""
    result = assert_allowed_number("805-439-8008")

    assert result == "+18054398008"
    # result = assert_allowed_number("800-123-1234")

    # assert result == "+18001231234"


def test_unapproved_number_is_blocked():
    """Any number other than the approved assessment number should be blocked."""
    with pytest.raises(UnsafePhoneNumberError):
        assert_allowed_number("+1-415-555-1234")


def test_unapproved_number_without_country_code_is_blocked():
    """Any number other than the approved assessment number should be blocked."""
    with pytest.raises(UnsafePhoneNumberError):
        assert_allowed_number("415-555-1234")
