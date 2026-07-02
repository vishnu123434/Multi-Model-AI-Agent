"""
tools/currency.py

Universal Currency Conversion Tool

Supports:
- ISO currency codes: USD, INR, EUR, GBP, JPY, AED, etc.
- Currency names: euro, rupee, yen, thai baht, kuwaiti dinar, etc.
- Common aliases: dollars, rupees, pounds, dirhams, yuan, won, etc.

Uses ExchangeRate-API Open Access endpoint:
https://open.er-api.com/v6/latest/{BASE}
"""

import re
import requests
import pycountry


BASE_URL = "https://open.er-api.com/v6/latest"


# ------------------------------------
# Common Currency Aliases
# ------------------------------------

COMMON_ALIASES = {
    # US Dollar
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",
    "us dollar": "USD",
    "us dollars": "USD",
    "american dollar": "USD",
    "american dollars": "USD",

    # Indian Rupee
    "inr": "INR",
    "rupee": "INR",
    "rupees": "INR",
    "indian rupee": "INR",
    "indian rupees": "INR",

    # Euro
    "eur": "EUR",
    "euro": "EUR",
    "euros": "EUR",

    # British Pound
    "gbp": "GBP",
    "pound": "GBP",
    "pounds": "GBP",
    "british pound": "GBP",
    "british pounds": "GBP",
    "pound sterling": "GBP",

    # Japanese Yen
    "jpy": "JPY",
    "yen": "JPY",
    "japanese yen": "JPY",

    # UAE Dirham
    "aed": "AED",
    "dirham": "AED",
    "dirhams": "AED",
    "uae dirham": "AED",
    "uae dirhams": "AED",
    "emirati dirham": "AED",

    # Saudi Riyal
    "sar": "SAR",
    "riyal": "SAR",
    "riyals": "SAR",
    "saudi riyal": "SAR",
    "saudi riyals": "SAR",

    # Chinese Yuan
    "cny": "CNY",
    "yuan": "CNY",
    "chinese yuan": "CNY",
    "renminbi": "CNY",
    "rmb": "CNY",

    # Korean Won
    "krw": "KRW",
    "won": "KRW",
    "korean won": "KRW",
    "south korean won": "KRW",

    # Other common currencies
    "aud": "AUD",
    "australian dollar": "AUD",
    "australian dollars": "AUD",

    "cad": "CAD",
    "canadian dollar": "CAD",
    "canadian dollars": "CAD",

    "sgd": "SGD",
    "singapore dollar": "SGD",
    "singapore dollars": "SGD",

    "chf": "CHF",
    "swiss franc": "CHF",
    "swiss francs": "CHF",

    "thb": "THB",
    "thai baht": "THB",
    "baht": "THB",

    "kwd": "KWD",
    "kuwaiti dinar": "KWD",
    "kuwait dinar": "KWD",

    "qar": "QAR",
    "qatari riyal": "QAR",

    "omr": "OMR",
    "omani rial": "OMR",

    "bhd": "BHD",
    "bahraini dinar": "BHD",

    "myr": "MYR",
    "malaysian ringgit": "MYR",
    "ringgit": "MYR",

    "npr": "NPR",
    "nepalese rupee": "NPR",
    "nepali rupee": "NPR",

    "pkr": "PKR",
    "pakistani rupee": "PKR",

    "bdt": "BDT",
    "bangladeshi taka": "BDT",
    "taka": "BDT",

    "lkr": "LKR",
    "sri lankan rupee": "LKR",

    "rub": "RUB",
    "russian ruble": "RUB",
    "ruble": "RUB",

    "zar": "ZAR",
    "south african rand": "ZAR",
    "rand": "ZAR",

    "brl": "BRL",
    "brazilian real": "BRL",
    "real": "BRL",

    "mxn": "MXN",
    "mexican peso": "MXN",

    "ars": "ARS",
    "argentine peso": "ARS",

    "try": "TRY",
    "turkish lira": "TRY",
    "lira": "TRY",

    "idr": "IDR",
    "indonesian rupiah": "IDR",
    "rupiah": "IDR",

    "vnd": "VND",
    "vietnamese dong": "VND",
    "dong": "VND",

    "php": "PHP",
    "philippine peso": "PHP",

    "egp": "EGP",
    "egyptian pound": "EGP",

    "ngn": "NGN",
    "nigerian naira": "NGN",
    "naira": "NGN",
}


# ------------------------------------
# Build Currency Name Map from pycountry
# ------------------------------------

def build_currency_map():
    currency_map = {}

    for currency in pycountry.currencies:
        code = getattr(currency, "alpha_3", None)
        name = getattr(currency, "name", None)

        if code:
            currency_map[code.lower()] = code.upper()

        if name and code:
            currency_map[name.lower()] = code.upper()

    # Common aliases should override pycountry if ambiguous
    currency_map.update(COMMON_ALIASES)

    return currency_map


CURRENCY_MAP = build_currency_map()


# ------------------------------------
# Extract Currency Details
# ------------------------------------

def extract_currency_details(query: str) -> dict:
    """
    Extract amount, from_currency, and to_currency from a query.

    Examples:
    - 100 USD to INR
    - 1000 dollars in rupees
    - 1000 euros in dollars
    - 500 Thai baht to Japanese yen
    - 100 UAE dirham to Kuwaiti dinar
    """

    query_lower = query.lower()
    query_upper = query.upper()

    # Extract amount
    amount_match = re.search(r"(\d+(\.\d+)?)", query_lower)

    if amount_match:
        amount = float(amount_match.group(1))
    else:
        amount = 1.0

    matches = []

    # 1. Detect direct ISO codes
    direct_codes = re.findall(r"\b[A-Z]{3}\b", query_upper)

    for code in direct_codes:
        if code.lower() in CURRENCY_MAP:
            matches.append((query_upper.find(code), code.upper()))

    # 2. Detect currency names and aliases
    for name, code in CURRENCY_MAP.items():
        pattern = r"\b" + re.escape(name) + r"\b"

        for match in re.finditer(pattern, query_lower):
            matches.append((match.start(), code.upper()))

    # Sort by position in query
    matches = sorted(matches, key=lambda x: x[0])

    currencies = []

    for _, code in matches:
        if code not in currencies:
            currencies.append(code)

    if len(currencies) >= 2:
        from_currency = currencies[0]
        to_currency = currencies[1]

    elif len(currencies) == 1:
        from_currency = currencies[0]

        # Smart default
        if from_currency == "INR":
            to_currency = "USD"
        else:
            to_currency = "INR"

    else:
        from_currency = "USD"
        to_currency = "INR"

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency
    }


# ------------------------------------
# Convert Currency
# ------------------------------------

def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    Convert amount from one currency to another using live exchange rates.
    """

    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        url = f"{BASE_URL}/{from_currency}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            return {
                "success": False,
                "message": f"Could not fetch exchange rates for {from_currency}."
            }

        rates = data.get("rates", {})

        if to_currency not in rates:
            return {
                "success": False,
                "message": f"Currency {to_currency} is not supported by the exchange rate API."
            }

        rate = rates[to_currency]
        converted_amount = amount * rate

        return {
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": round(rate, 6),
            "message": (
                f"{amount:g} {from_currency} = "
                f"{round(converted_amount, 2):g} {to_currency}"
            )
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Currency Conversion Error: {str(e)}"
        }


# ------------------------------------
# Manual Test
# ------------------------------------

if __name__ == "__main__":

    test_queries = [
        "1000 euros in dollars",
        "1000 dollars in rupees",
        "500 Thai baht to Japanese yen",
        "100 UAE dirham to Kuwaiti dinar",
        "1000 INR to GBP"
    ]

    for query in test_queries:
        details = extract_currency_details(query)

        print("\nQuery:", query)
        print("Extracted:", details)

        result = convert_currency(
            details["amount"],
            details["from_currency"],
            details["to_currency"]
        )

        print("Result:", result["message"])