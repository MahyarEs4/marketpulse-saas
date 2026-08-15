from decimal import Decimal


def format_price_change_alert(
    competitor_name: str,
    old_price: Decimal,
    new_price: Decimal,
    change_amount: Decimal,
    change_percent: Decimal | None,
    currency: str,
) -> str:
    direction = "افزایش" if change_amount > 0 else "کاهش"
    percent_text = "نامشخص" if change_percent is None else f"{change_percent}%"

    return (
        f"<b>Price Alert</b>\n"
        f"Competitor: {competitor_name}\n"
        f"Old Price: {old_price} {currency}\n"
        f"New Price: {new_price} {currency}\n"
        f"Change: {direction} ({change_amount} {currency})\n"
        f"Change Percent: {percent_text}"
    )
