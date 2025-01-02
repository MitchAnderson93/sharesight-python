import os
import requests
import click
from art import text2art
from dotenv import load_dotenv

load_dotenv()

# Sharesight API configurations
API_BASE_URL = os.getenv("SHARESIGHT_API_BASE_PATH")
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
    """Delete a portfolio with the given ID - uses V2 legacy API endpoint."""
    global ACCESS_TOKEN
    url = f"{API_BASE_URL}/{LEGACY_VERSION}/portfolios/{portfolio_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        click.echo("Portfolio deleted successfully.")
    else:
        raise Exception(f"Error deleting portfolio: {response.status_code} {response.text}")

class CustomGroup(click.Group):
    """Custom Click Group to include ASCII art in the help message."""
    def format_help(self, ctx, formatter):
        ascii_art = text2art("ShareSight API CLI", font="small")
        click.echo(ascii_art)
        super().format_help(ctx, formatter)

@click.group(cls=CustomGroup)
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

if __name__ == "__main__":
    cli()
