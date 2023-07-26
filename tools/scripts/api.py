import yfinance as yf

def get_fields(ticker):
    """Get additional fields for a given ticker."""
    ticker_data = yf.Ticker(ticker+'.AX')
    dividend_yield = ticker_data.info.get("trailingAnnualDividendYield", None)
    stability = None  # Add code here to fetch historical stability percent from a data source
    current_price = ticker_data.info.get("regularMarketPrice", None)
    sector_code = ticker_data.info.get("sector", None)
    company_name = ticker_data.info.get("longName", None)

    return {
        "dividend_yield": dividend_yield,
        "stability": stability,
        "current_price": current_price,
        "sector_code": sector_code,
        "company_name": company_name,
    }