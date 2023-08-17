import csv

def read_data_from_csv(file_path):
    """Read data from a CSV file and return rows/columns."""
    rows = []

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    return rows

