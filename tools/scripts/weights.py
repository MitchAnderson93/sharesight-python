# tools/weights.py
def assign_weights(value_scores):
    # Calculate the sum of all value scores
    total_score = sum(value_scores)

    # Calculate weights based on the value score
    weights = [score / total_score for score in value_scores]

    return weights
