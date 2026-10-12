"""Weak test: checks that exact duplicates are removed.

It passes with the correct code... and also when the email normalization is broken.
"""
from clean_customers import deduplicate_customers


def test_removes_exact_duplicates():
    customers = [
        {"customer_id": "1", "email": "ana@mail.com"},
        {"customer_id": "2", "email": "ana@mail.com"},
        {"customer_id": "3", "email": "luis@mail.com"},
    ]
    assert len(deduplicate_customers(customers)) == 2
