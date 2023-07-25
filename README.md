# Commands:

## List all:
```python
(env): $ python script.py list-portfolios

output:
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
(env): $ python script.py delete-holding 961635 19201377

Output:None
```