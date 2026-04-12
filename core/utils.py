def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def calculate_brokerage(amount, pct, minimum):
    return max(amount * pct, minimum)