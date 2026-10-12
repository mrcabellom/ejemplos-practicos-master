"""Strong tests: protect the core property.

The same email with different case or spaces is the same customer.
"""
import pytest

from clean_customers import deduplicate_customers, normalize_email


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Ana@Mail.com", "ana@mail.com"),
        ("  ana@mail.com ", "ana@mail.com"),
        ("LUIS@MAIL.COM", "luis@mail.com"),
    ],
)
def test_normalize_email(raw, expected):
    assert normalize_email(raw) == expected


def test_four_known_emails_become_two_customers():
    emails = ["Ana@Mail.com", "ana@mail.com ", "luis@mail.com", " LUIS@MAIL.COM"]
    customers = [{"customer_id": str(i), "email": e} for i, e in enumerate(emails, start=1)]
    assert len(deduplicate_customers(customers)) == 2
