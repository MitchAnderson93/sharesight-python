# Commands:

## Setup script:
1. Update 'sample.env' to just '.env' and populate with your API key information
2. Setup project repository virtual env, activate and install requirements
```python
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## List all portfolios:
```python
(env): $ python cli.py list-portfolios
Output:
Your Portfolios:
- Strategies (ID: 961635)
```

## List securities under a portfolio (ID):
```python
(env): $ python script.py list-holdings 961635
Output:
Holdings in the selected portfolio:
- New Hope Corporation (NHC.AX - ID: 19201377)
```

## Delete a portfolio:
```python
(env): $ python script.py delete-portfolio 964472
Output: Portfolio deleted successfully.
```