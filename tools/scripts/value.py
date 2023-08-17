# tools/value_score.py
def calculate_value_score(row):
    # Define weights for each parameter (you can adjust these as needed)
    weight_yield = 0.1
    weight_stability = 0.1
    weight_value = 0.8

    # Handle missing values for yield and stability
    yield_percentage = float(row["yield"]) if row["yield"] is not None else 0.0
    stability = float(row["stability"]) if row["stability"] is not None else 0.0

    # Convert value to float
    value = float(row["value"])

    # Calculate the value score using the weighted sum of each parameter
    # Adjust weight_value based on value relative to price
    if value > row["price"]:
        weight_value *= 0.8  # Reduce weight if value is higher than price
    elif value < row["price"]:
        weight_value *= 1.2  # Increase weight if value is lower than price

    value_score = (
        weight_yield * yield_percentage +
        weight_stability * (1 - stability) +
        weight_value * (value / row["price"])
    )
    return value_score
