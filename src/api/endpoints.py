BASE_V1 = "/v1"
BASE_V2 = "/v2"

CURRENCIES_V2 = f"{BASE_V2}/exchange/currencies"
EXCHANGE_V1 = f"{BASE_V1}/exchange"
EXCHANGES_V2 = f"{BASE_V2}/exchanges"


def CURRENCIES_TO_V1(ticker: str) -> str:
    return f"{BASE_V1}/currencies-to/{ticker}"


def EXCHANGE_AMOUNT_V1(send_amount: str, from_t: str, to_t: str) -> str:
    """/v1/exchange-amount/:send_amount/:from_to"""
    pair = f"{from_t}_{to_t}"
    return f"{BASE_V1}/exchange-amount/{send_amount}/{pair}"
