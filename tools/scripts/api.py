import requests
import yfinance as yf
from bs4 import BeautifulSoup

def get_fields(ticker):

    """Get additional fields for a given ticker via yfinance"""
    company = yf.Ticker(ticker+'.AX')
    dividend_yield = company.info.get("dividendYield", None)
    stability = company.info.get("payoutRatio", None)  # You can fetch this from a different source if available
    current_price = company.history(period="1d")["Close"].iloc[-1]
    sector_code = company.info.get("sector", None)

    # Convert dividend_yield to percentage
    if dividend_yield is not None:
        dividend_yield = dividend_yield * 100

    return {
        "yield": dividend_yield,
        "stability": stability,
        "price": current_price,
        "sector": sector_code,
    }