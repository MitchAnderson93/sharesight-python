```
 ___  _                     ___  _        _     _       _    ___  ___    ___  _     ___ 
/ __|| |_   __ _  _ _  ___ / __|(_) __ _ | |_  | |_    /_\  | _ \|_ _|  / __|| |   |_ _|
\__ \| ' \ / _` || '_|/ -_)\__ \| |/ _` || ' \ |  _|  / _ \ |  _/ | |  | (__ | |__  | | 
|___/|_||_|\__,_||_|  \___||___/|_|\__, ||_||_| \__| /_/ \_\|_|  |___|  \___||____||___|
                                   |___/                                                
```

A CLI tool I made to manage and sync ShareSight investment portfolio's with local data analysis work.

### Steps to setup:
- Requires Python3/pip to run (install both)
- Update 'sample.env' to just '.env' and populate with your API key information
- ```python3 -m venv env``` to initialise a local env
- ```source env/bin/activate``` to activate local dev environment (for installing pip packages)
- ```pip install -r requirements.txt``` to install dependencies 

#### Other commands for managing the repository:
- ```pip freeze > requirements.txt``` to add/manage new dependencies 

### Using the CLI tool:
- ```python cli.py``` to run CLI

#### List all portfolios:
```python
(env): $ python cli.py list-portfolios
Output:
Your Portfolios:
- Strategies (ID: 961635)
```

#### List securities under a portfolio (ID):
```python
(env): $ python cli.py list-holdings 961635
Output:
Holdings in the selected portfolio:
- New Hope Corporation (NHC.AX - ID: 19201377)
```

#### Delete a portfolio:
```python
(env): $ python cli.py delete-portfolio 961635
Output: Portfolio deleted successfully.
```