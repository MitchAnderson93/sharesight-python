## Toolkit for using Sharesight via API

### Steps to setup:
- Requires Python3/pip to run (install both)
- Update 'sample.env' to just '.env' and populate with your API key information
- ```python3 -m venv env``` to initialise a local env
- ```source env/bin/activate``` to activate local dev environment (for installing pip packages)
- ```pip install -r requirements.txt``` to install dependencies 

### Other commands for managing the repository:
- ```pip freeze > requirements.txt``` to add/manage new dependencies 

### Using the CLI tool:
- ```python cli.py``` to run CLI

### List all portfolios:
```python
(env): $ python script.py list-portfolios
Output:
Your Portfolios:
- Strategies (ID: 961635)
```

### List securities under a portfolio (ID):
```python
(env): $ python script.py list-holdings 961635
Output:
Holdings in the selected portfolio:
- New Hope Corporation (NHC.AX - ID: 19201377)
```

### Delete a portfolio:
```python
(env): $ python script.py delete-portfolio 964472
Output: Portfolio deleted successfully.
```