# tests/test_api.py
import os

import pytest
import allure

from src.api import endpoints as ep

pytestmark = pytest.mark.api


@pytest.fixture(scope="session")
def cfg():
    return {
        "base": os.getenv("API_BASE", "https://api.changenow.io"),
        "from": os.getenv("FROM", "btc"),
        "to": os.getenv("TO", "eth"),
        "amount": os.getenv("AMOUNT", "0.01"),
        "payout": os.getenv("PAYOUT_ADDRESS", ""),
        "api_key": (
            os.getenv("API_KEY")
            or os.getenv("X_CHANGENOW_API_KEY")
            or ""
        ),
    }


@pytest.fixture(scope="session")
def api(cfg):
    from src.api.client import ChangeNowClient
    return ChangeNowClient(cfg["base"], api_key=cfg["api_key"])


@allure.title("Currencies v2: список не пуст, есть ключевые поля")
def test_currencies_list_ok(api):
    r = api.get(ep.CURRENCIES_V2)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and data
    assert {"ticker", "name"}.issubset(data[0].keys())


@allure.title(
    "Estimate v1 (/exchange-amount): >0 и есть ключевые поля"
)
def test_estimate_ok(api, cfg):
    if not (cfg["from"] and cfg["to"] and cfg["amount"]):
        pytest.skip("Нужны FROM/TO/AMOUNT в .env")
    path = ep.EXCHANGE_AMOUNT_V1(cfg["amount"], cfg["from"], cfg["to"])
    r = api.get(path)
    if r.status_code in (401, 403):
        pytest.skip("Для /v1/exchange-amount нужен API_KEY")
    assert r.status_code == 200, r.text
    js = r.json()
    assert "estimatedAmount" in js
    est = float(js.get("estimatedAmount") or 0)
    assert est > 0


@allure.title("Create exchange v1: есть id и payinAddress")
def test_create_exchange_ok(api, cfg):
    if not (cfg["from"] and cfg["to"] and cfg["amount"] and cfg["payout"]):
        pytest.skip("Нужны FROM/TO/AMOUNT/PAYOUT_ADDRESS в .env")
    body = {
        "from": cfg["from"],
        "to": cfg["to"],
        "amount": cfg["amount"],
        "address": cfg["payout"],
    }
    r = api.post(ep.EXCHANGE_V1, json=body)
    assert r.status_code in (200, 201), r.text
    js = r.json()
    assert {"id", "payinAddress"}.issubset(js.keys())


@allure.title(
    "Exchanges v2: требует API-ключ; при наличии — структура валидна"
)
def test_exchange_status_list(api, cfg):
    if not cfg["api_key"]:
        pytest.skip("Нужен API_KEY для /v2/exchanges")
    r = api.get(ep.EXCHANGES_V2, params={"limit": 1})
    assert r.status_code == 200, r.text
    arr = r.json()
    assert isinstance(arr, list)


@allure.title(
    "Негатив: /exchange-amount для несуществующей пары → 4xx "
    "и текст/JSON с ошибкой"
)
def test_estimate_invalid_pair(api):
    path = ep.EXCHANGE_AMOUNT_V1("1", "zzz", "yyy")
    r = api.get(path)
    assert 400 <= r.status_code < 500, r.text
    try:
        js = r.json()
        ok = ("error" in js) or ("message" in js)
    except Exception:
        ok = bool(r.text)
    assert ok, f"Нет тела ошибки: {r.text!r}"


@allure.title(
    "POSTMAN/Positive: /v1/currencies-to/btc → 200 "
    "и непустой список"
)
def test_currencies_to_btc(api):
    r = api.get(ep.CURRENCIES_TO_V1("btc"))
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and data


@allure.title(
    "POSTMAN/Positive: /v1/currencies-to/ton → 200 "
    "и непустой список"
)
def test_currencies_to_ton(api):
    r = api.get(ep.CURRENCIES_TO_V1("ton"))
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and data


@allure.title("POSTMAN/Negative: /v1/currencies-to/invalid → 404")
def test_currencies_to_invalid(api):
    r = api.get(ep.CURRENCIES_TO_V1("invalid"))
    assert r.status_code == 404, (
        f"{r.status_code} != 404; body={r.text!r}"
    )
