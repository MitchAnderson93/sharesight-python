import os
import requests
import click
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

@click.group()
def cli():
    """ShareSight Portfolio Manager CLI"""
    try:
        global ACCESS_TOKEN
        ACCESS_TOKEN = request_access_token()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

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

@cli.command()
@click.argument("portfolio_id", type=int)
def delete_portfolio(portfolio_id):
    """Delete a portfolio with a given ID."""
    try:
        delete(portfolio_id)
    except Exception as e:
        click.echo(f"Error deleting portfolio: {e}", err=True)

@cli.command()
@click.argument("file", type=click.Path(exists=True))
def read_csv(file):
    """Generate a list of securities from CSV"""
    rows = tools.read.read_data_from_csv(file)
    for row in rows:
        # Get the ticker from each row
        ticker = row["TICKER"]
        # Get additional fields using the get_fields function
        additional_fields = tools.api.get_fields(ticker)
        # Add the additional fields to the row
        row.update(additional_fields)

        # Calculate the percentage difference between the current price and the 'value' field
        if "current_price" in row and "VALUE" in row:
            current_price = row["current_price"]
            value = float(row["VALUE"])
            if value != 0:
                percentage_diff = abs((current_price - value) / value) * 100
            else:
                percentage_diff = 0.0
            row["percentage_difference"] = percentage_diff

        # Print the updated row
        print(row)


if __name__ == "__main__":
    cli()