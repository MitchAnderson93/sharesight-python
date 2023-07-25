# Commands:

## Setup:
```python
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## List all:
```python
(env): $ python script.py list-portfolios
Output:
Your Portfolios:
- Strategies (ID: 961635)
```

## List under parent:
```python
(env): $ python script.py list-holdings 961635
Output:
Holdings in the selected portfolio:
- New Hope Corporation (NHC.AX - ID: 19201377)
```
## Delete:
```python
(env): $ python script.py delete-portfolio 964472
Output: Portfolio deleted successfully.
```