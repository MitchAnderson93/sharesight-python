import os
import click
import datetime
from dateutil.relativedelta import relativedelta
import requests
import yfinance as yf
from dotenv import load_dotenv
load_dotenv()

# Custom tools that expand ontop of this 
import tools

# Sharesight API endpoint
API_BASE_URL = "https://api.sharesight.com/api/"
CLIENT_ID = os.getenv("SHARESIGHT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHARESIGHT_CLIENT_SECRET")
ACCESS_TOKEN = None
LATEST_VERSION = os.getenv('SHARESIGHT_API_LATEST_VERSION')
LEGACY_VERSION = os.getenv("SHARESIGHT_API_LEGACY_VERSION")

def request_access_token():
    """Requests a new OAuth token."""
    access_token_url = os.getenv("SHARESIGHT_ACCESS_TOKEN_URL")
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(access_token_url, data=payload)
    response_data = response.json()

    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        raise Exception(f"Error obtaining access token: {response_data}")

def get_portfolios():
    """Fetches a list of portfolios."""
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}/{LATEST_VERSION}/portfolios"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["portfolios"]
    else:
        raise Exception(f"Error fetching portfolios: {response.status_code} {response.text}")

def get_holdings(portfolio_id):
    """Fetches a list of holdings for the given portfolio ID."""
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}/{LATEST_VERSION}/portfolios/{portfolio_id}/holdings"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["holdings"]
    else:
        raise Exception(f"Error fetching holdings: {response.status_code} {response.text}")
    
def get_stock_price(symbol, date):
    """Get the stock price for a given symbol and date."""
    formatted_date = date.strftime("%Y-%m-%d")
    print(formatted_date)
    try:
        stock = yf.Ticker(f"{symbol}.AX")
        df = stock.history(start=formatted_date, end=formatted_date)
        if not df.empty:
            print(df)
            return df["Close"].values[0]
        else:
            print(f"No price data found for {symbol} on {formatted_date}.")
            return None
    except Exception as e:
        print(f"Exception while fetching price for {symbol} on {formatted_date}: {e}")
        return None
    
def delete(portfolio_id):
    """Delete a portfolio with the given ID - uses V2 legacy API endpoint"""
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}/{LEGACY_VERSION}/portfolios/{portfolio_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        click.echo("Portfolio deleted successfully.")
    else:
        raise Exception(f"Error deleting portfolio: {response.status_code} {response.text}")

# Define a new function to delete a portfolio with the given portfolio ID
def delete_portfolio_func(portfolio_id):
    try:
        delete(portfolio_id)
    except Exception as e:
        click.echo(f"Error deleting portfolio: {e}", err=True)

# Define a new function to create a portfolio
def create_portfolio_func(name):
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}/{LEGACY_VERSION}/portfolios"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.post(url, headers=headers, json={"name": name})
        response.raise_for_status()
        click.echo("Portfolio created successfully.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error creating portfolio: {e}")

@click.group()
def cli():
    """Sharesight CLI"""
    try:
        global ACCESS_TOKEN
        ACCESS_TOKEN = request_access_token()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


# Define the CLI command for deleting a portfolio
@cli.command()
@click.argument("portfolio_id", type=int)
def delete_portfolio(portfolio_id):
    """Delete a portfolio with the given portfolio ID."""
    delete_portfolio_func(portfolio_id)

# Define the CLI command for creating a portfolio
@cli.command()
@click.argument("name")
def create_portfolio(name):
    """Create a new portfolio."""
    create_portfolio_func(name)
    
@cli.command()
def list_portfolios():
    """List all portfolios."""
    try:
        portfolios = get_portfolios()
        click.echo("Your Portfolios:")
        for portfolio in portfolios:
            click.echo(f"- {portfolio['name']} (ID: {portfolio['id']})")
    except Exception as e:
        click.echo(f"Error fetching portfolios: {e}", err=True)

@cli.command()
@click.argument("portfolio_id", type=int)
def list_holdings(portfolio_id):
    """List holdings of a selected portfolio."""
    try:
        holdings = get_holdings(portfolio_id)
        click.echo("Holdings in the selected portfolio:")
        for holding in holdings:
            click.echo(f"- {holding['instrument']['name']} ({holding['instrument']['code']}.AX - ID: {holding['id']})")
    except Exception as e:
        click.echo(f"Error fetching holdings: {e}", err=True)

def get_periodic_dates(start_date, end_date, periodic_buy):
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)  # Append datetime.date object instead of string
        if periodic_buy == "weekly":
            current_date += datetime.timedelta(weeks=1)
        elif periodic_buy == "monthly":
            current_date += relativedelta(months=1)
        elif periodic_buy == "quarterly":
            current_date += relativedelta(months=3)
        elif periodic_buy == "semi-annual":
            current_date += relativedelta(months=6)
        elif periodic_buy == "annual":
            current_date += relativedelta(years=1)
    return dates

def push_trade_to_sharesight(trade):
    """Push a trade to Sharesight."""
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}{LEGACY_VERSION}/trades.json"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.post(url, headers=headers, json={"trade": trade})
        response.raise_for_status()
        print(response)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error pushing trade to Sharesight: {e}")

def push_trades(total_capital, start_date, end_date, sorted_rows, weights, portfolio_id, periodic_buy):
    
    # Convert start_date and end_date to strings
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    num_days = (end_date - start_date).days
    if periodic_buy == "weekly":
        num_buy_orders = max(num_days // 7, 1)
    elif periodic_buy == "monthly":
        num_buy_orders = max(num_days // 30, 1)
    elif periodic_buy == "quarterly":
        num_buy_orders = max(num_days // 90, 1)
    elif periodic_buy == "semi-annual":
        num_buy_orders = max(num_days // 180, 1)
    elif periodic_buy == "annual":
        num_buy_orders = max(num_days // 365, 1)

    print(num_buy_orders)

    # Push trades to Sharesight for each buy order
    for row, weight in zip(sorted_rows, weights):
        # Calculate the capital for this row based on its weight
        row_capital = total_capital * weight

        # Calculate the amount of capital for each buy order
        capital_per_buy_order = row_capital / num_buy_orders

        for buy_date in get_periodic_dates(start_date, end_date, periodic_buy):
            try:
                stock_price = get_stock_price(row["ticker"], buy_date)
            except Exception as e:
                print(f"Error: {e}")
                continue  # Skip this trade and proceed with the next one

            if stock_price is None:
                print(f"Skipping trade for {row['ticker']} on {buy_date}: No price data found.")
                continue  # Skip this trade and proceed with the next one

            # Continue with the rest of the trade process using the stock_price
            # Calculate the number of units to buy, factoring in brokerage fees
            units_to_buy = (capital_per_buy_order - 9.95) / stock_price

            # Create a trade for this row with the calculated units to buy
            trade = {
                "unique_identifier": f"{row['ticker']}-{buy_date}",
                "transaction_type": "BUY",
                "transaction_date": buy_date.strftime("%Y-%m-%d"),  # No need to format here
                "portfolio_id": portfolio_id,  # Use the user-input portfolio ID here
                "symbol": row["ticker"],
                "market": "ASX",  # Replace with the actual market code
                "quantity": units_to_buy,
                "price": stock_price,
                "exchange_rate": 1.0,  # Replace with the actual exchange rate if applicable
            }

            # Call the function to push the trade to Sharesight
            push_trade_to_sharesight(trade)

        click.echo("Trades were pushed to Sharesight successfully.")

def get_user_input():
    portfolio_id = click.prompt("Enter portfolio ID:", type=int)
    total_capital = click.prompt("Enter total capital:", type=float, default=100000)
    start_date = click.prompt("Enter start date (YYYY-MM-DD):", type=click.DateTime(formats=["%Y-%m-%d"]))
    end_date = click.prompt("Enter end date (YYYY-MM-DD):", type=click.DateTime(formats=["%Y-%m-%d"]))
    periodic_buy = click.prompt("Enter periodic buy (weekly/monthly/quarterly/semi-annual/annual):",
                                type=click.Choice(["weekly", "monthly", "quarterly", "semi-annual", "annual"]))
    return total_capital, start_date, end_date, periodic_buy, portfolio_id

@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.pass_context
def build_portfolio_from_csv(ctx, file):
    """Generate a list of securities from CSV and designs a value weighted portfolio (experimental)"""
    rows = tools.read.read_data_from_csv(file)
    value_scores = []  # Store the value scores for each row

    for row in rows:
        ticker = row["ticker"]
        row["value"] = float(row["value"])
        additional_fields = tools.api.get_fields(ticker)
        row.update(additional_fields)
        row["value_score"] = tools.value.calculate_value_score(row)
        value_scores.append(row["value_score"])

    # Call the function to assign weights based on value scores
    weights = tools.weights.assign_weights(value_scores)

    # Sort the rows by value score (in descending order)
    sorted_rows = sorted(rows, key=lambda x: x["value_score"], reverse=True)

    # Print the sorted rows with formatted stability and weight
    for row, weight in zip(sorted_rows, weights):
        # Convert value to float

        # Format stability as float with 2 decimal places
        stability = row.get("stability")
        if stability is not None:
            stability = round(float(stability) * 100, 2)
        row["stability"] = stability

        # Format weight as float with 2 decimal places
        row["weight"] = round(weight * 100, 2)

        # readable output
        print(row)

    # Ask the user if they want to push trades to Sharesight
    if click.confirm("Do you want to push the trades to Sharesight?", default=False):
        total_capital, start_date, end_date, periodic_buy, portfolio_id = get_user_input()
        push_trades(total_capital=total_capital, start_date=start_date, end_date=end_date,
                    sorted_rows=sorted_rows, weights=weights, portfolio_id=portfolio_id, periodic_buy=periodic_buy)
        
if __name__ == "__main__":
    cli()