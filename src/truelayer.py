"""TrueLayer Open Banking client — auth, token exchange, and transaction fetch."""
from __future__ import annotations

import secrets
import urllib.parse

import httpx
import pandas as pd

from src import config

# TrueLayer transaction_category → (category, broad)
_CATEGORY_MAP: dict[str, tuple[str, str]] = {
    "PURCHASE":       ("shopping",       "spending"),
    "ATM":            ("cash",           "spending"),
    "TRANSFER":       ("transfer",       "transfer"),
    "DIRECT_DEBIT":   ("direct debit",  "bills"),
    "STANDING_ORDER": ("standing order", "bills"),
    "CREDIT":         ("income",         "income"),
    "INTEREST":       ("interest",       "savings"),
    "CASHBACK":       ("cashback",       "income"),
    "CHEQUE":         ("cheque",         "spending"),
    "BANK_FEE":       ("bank fee",       "bills"),
    "CASH":           ("cash",           "spending"),
    "OTHER":          ("other",          "other"),
}


def _auth_domain() -> str:
    return "truelayer-sandbox.com" if config.TRUELAYER_SANDBOX else "truelayer.com"


def _api_domain() -> str:
    return "truelayer-sandbox.com" if config.TRUELAYER_SANDBOX else "truelayer.com"


def auth_url() -> str:
    providers = "uk-ob-all uk-oauth-all"
    if config.TRUELAYER_SANDBOX:
        providers += " uk-cs-mock"  # mock bank for sandbox testing

    params = {
        "response_type": "code",
        "client_id":     config.TRUELAYER_CLIENT_ID,
        "scope":         "accounts transactions offline_access",
        "redirect_uri":  config.TRUELAYER_REDIRECT_URI,
        "providers":     providers,
        "nonce":         secrets.token_urlsafe(16),
    }
    return f"https://auth.{_auth_domain()}/?{urllib.parse.urlencode(params)}"


def exchange_code(code: str) -> str:
    resp = httpx.post(
        f"https://auth.{_auth_domain()}/connect/token",
        data={
            "grant_type":    "authorization_code",
            "client_id":     config.TRUELAYER_CLIENT_ID,
            "client_secret": config.TRUELAYER_CLIENT_SECRET,
            "redirect_uri":  config.TRUELAYER_REDIRECT_URI,
            "code":          code,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_transactions(access_token: str) -> pd.DataFrame:
    api  = f"https://api.{_api_domain()}/data/v1"
    hdrs = {"Authorization": f"Bearer {access_token}"}

    accounts_resp = httpx.get(f"{api}/accounts", headers=hdrs, timeout=30)
    accounts_resp.raise_for_status()
    accounts = accounts_resp.json()["results"]

    rows: list[dict] = []
    for account in accounts:
        txn_resp = httpx.get(
            f"{api}/accounts/{account['account_id']}/transactions",
            headers=hdrs,
            timeout=30,
        )
        txn_resp.raise_for_status()
        for t in txn_resp.json()["results"]:
            category, broad = _CATEGORY_MAP.get(
                t.get("transaction_category", "OTHER"), ("other", "other")
            )
            rows.append({
                "transaction_date": pd.to_datetime(t["timestamp"]).normalize(),
                "description":      t.get("description", ""),
                "amount":           float(t["amount"]),
                "category":         category,
                "broad":            broad,
                "merchant":         t.get("merchant_name"),
                "currency":         t.get("currency", "GBP"),
            })

    if not rows:
        raise ValueError("No transactions returned from TrueLayer")

    return pd.DataFrame(rows)
