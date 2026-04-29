def evaluate_order(order):
    score = 0

    for item in order["items"]:
        if item["quantity"] <= 0:
            continue

        if item["price"] > 100 and item["category"] != "book":
            score += 3
        elif item["price"] > 50 or item["category"] == "electronics":
            score += 2
        else:
            score += 1

    attempts = 0
    while attempts < 3:
        try:
            risk = order["total"] / order["payments"]
        except ZeroDivisionError:
            score += 4
            break

        if risk > 30:
            score += 1

        attempts += 1
        if order.get("manual_review"):
            break

    return "hold" if score >= 8 else "pass"
