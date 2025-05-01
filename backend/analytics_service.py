# backend/analytics_service.py
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import models

def get_orders_summary(db: Session, user_id: int, upload_id: int):
    """
    Returns a dictionary with total_orders, total_revenue, and average_order_value
    for the specified user & upload.
    """
    total_orders = db.query(func.count(models.Order.id)).filter(
        models.Order.user_id == user_id,
        models.Order.upload_id == upload_id
    ).scalar() or 0

    total_revenue = db.query(func.coalesce(func.sum(models.Order.total), 0)).filter(
        models.Order.user_id == user_id,
        models.Order.upload_id == upload_id
    ).scalar()

    # Avoid dividing by zero
    if total_orders > 0:
        avg_order_value = float(total_revenue) / float(total_orders)
    else:
        avg_order_value = 0.0

    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "average_order_value": avg_order_value,
    }

def get_orders_time_series(db: Session, user_id: int, upload_id: int):
    """
    Groups orders by day and returns the number of orders per day.
    """
    results = db.query(
        func.date_trunc('day', models.Order.created_at).label('day'),
        func.count(models.Order.id)
    ).filter(
        models.Order.user_id == user_id,
        models.Order.upload_id == upload_id
    ).group_by(
        func.date_trunc('day', models.Order.created_at)
    ).order_by(
        func.date_trunc('day', models.Order.created_at)
    ).all()

    time_series = []
    for row in results:
        day_str = row[0].strftime("%Y-%m-%d") if row[0] else None
        time_series.append({
            "date": day_str,
            "orderCount": row[1]
        })

    return time_series

# analytics_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from db import models

def get_top_cities_by_orders(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return the top N cities by count of orders, using the shipping_city field.
    Filter out empty, null, or 'nan' values.
    """
    results = (
        db.query(
            models.Order.shipping_city.label("city"),
            func.count(models.Order.id).label("order_count")
        )
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id,
            # Filter out empty, null, or 'nan' values
            models.Order.shipping_city.isnot(None),
            models.Order.shipping_city != "",
            models.Order.shipping_city != "nan"
        )
        .group_by(models.Order.shipping_city)
        .order_by(func.count(models.Order.id).desc())  # descending by order_count
        .limit(limit)
        .all()
    )

    # Convert query rows to a list of dictionaries for easy JSON serialization
    return [
        {
            "city": row.city or "Unknown",
            "order_count": row.order_count
        }
        for row in results
    ]

def get_top_cities_by_revenue(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return the top N cities by sum of Order.total (revenue).
    Filter out empty, null, or 'nan' values.
    """
    results = (
        db.query(
            models.Order.shipping_city.label("city"),
            func.sum(models.Order.total).label("revenue")
        )
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id,
            # Filter out empty, null, or 'nan' values
            models.Order.shipping_city.isnot(None),
            models.Order.shipping_city != "",
            models.Order.shipping_city != "nan",
            # Ensure total is valid
            models.Order.total.isnot(None),
            models.Order.total != 0
        )
        .group_by(models.Order.shipping_city)
        .order_by(func.sum(models.Order.total).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "city": row.city or "Unknown",
            "revenue": float(row.revenue or 0)
        }
        for row in results
    ]

def get_top_products_by_quantity(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return the top N products by total quantity sold.
    """
    results = (
        db.query(
            models.LineItem.lineitem_name.label("product_name"),
            func.sum(models.LineItem.lineitem_quantity).label("total_quantity")
        )
        .join(models.Order, models.LineItem.order_id == models.Order.id)
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id
        )
        .group_by(models.LineItem.lineitem_name)
        .order_by(func.sum(models.LineItem.lineitem_quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_name": row.product_name or "Unnamed Product",
            "total_quantity": int(row.total_quantity or 0)
        }
        for row in results
    ]

def get_top_products_by_revenue(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return the top N products by total revenue (sum of lineitem_price * lineitem_quantity).
    Make sure lineitem_price is also stored as numeric for accurate aggregation.
    """
    # Use a simpler approach that avoids casting empty strings to numeric
    results = (
        db.query(
            models.LineItem.lineitem_name.label("product_name"),
            func.sum(
                models.LineItem.lineitem_quantity * models.LineItem.lineitem_price
            ).label("product_revenue")
        )
        .join(models.Order, models.LineItem.order_id == models.Order.id)
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id,
            # Filter out NULL or zero prices to avoid calculation issues
            # Note: Removed empty string comparison which causes PostgreSQL type errors
            models.LineItem.lineitem_price.isnot(None),
            models.LineItem.lineitem_price > 0
        )
        .group_by(models.LineItem.lineitem_name)
        .order_by(
            func.sum(
                models.LineItem.lineitem_quantity * models.LineItem.lineitem_price
            ).desc()
        )
        .limit(limit)
        .all()
    )


    return [
        {
            "product_name": row.product_name or "Unnamed Product",
            "product_revenue": float(row.product_revenue or 0)
        }
        for row in results
    ]

def get_unique_customer_count(db: Session, user_id: int, upload_id: int):
    """
    Count distinct email addresses for this user & upload.
    """
    return (
        db.query(func.count(func.distinct(models.Order.email)))
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id
        )
        .scalar()
    )

def get_repeat_customer_count(db: Session, user_id: int, upload_id: int):
    """
    Count how many customers (by email) have 2+ orders.
    """
    # 1) Subquery to group orders by email
    subq = (
        db.query(
            models.Order.email.label("customer_email"),
            func.count(models.Order.id).label("order_count")
        )
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id
        )
        .group_by(models.Order.email)
        .subquery()
    )

    # 2) Count how many have >= 2 orders
    return (
        db.query(func.count("*"))
        .select_from(subq)
        .filter(subq.c.order_count >= 2)
        .scalar()
    )

def get_orders_by_hour(db: Session, user_id: int, upload_id: int):
    """
    Groups orders by hour, returning a list of { "hour_block": "YYYY-MM-DD HH:00", "count_orders": N }
    """
    results = (
        db.query(
            func.date_trunc('hour', models.Order.created_at).label('hour_block'),
            func.count(models.Order.id).label('count_orders')
        )
        .filter(models.Order.user_id == user_id, models.Order.upload_id == upload_id)
        .group_by(func.date_trunc('hour', models.Order.created_at))
        .order_by(func.date_trunc('hour', models.Order.created_at))
        .all()
    )

    return [
        {
            "hour_block": row.hour_block.strftime("%Y-%m-%d %H:00") if row.hour_block else None,
            "count_orders": row.count_orders
        }
        for row in results
    ]

def get_orders_by_day_of_week(db: Session, user_id: int, upload_id: int):
    """
    Summarizes number of orders by day of week (0=Sunday, 1=Monday, ...6=Saturday).
    """
    results = (
        db.query(
            func.extract('DOW', models.Order.created_at).label('dow'),
            func.count(models.Order.id).label('count_orders')
        )
        .filter(models.Order.user_id == user_id, models.Order.upload_id == upload_id)
        .group_by(func.extract('DOW', models.Order.created_at))
        .order_by(func.extract('DOW', models.Order.created_at))
        .all()
    )

    # Convert to e.g. { "dow": 1, "count_orders": 15 } meaning Monday had 15 orders
    return [
        {
            "dow": int(row.dow),
            "count_orders": row.count_orders
        }
        for row in results
    ]

def get_top_discount_codes(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return the top discount codes by how many orders used them.
    Filter out empty, null, or 'nan' values.
    """
    results = (
        db.query(
            models.Order.discount_code.label("discount_code"),
            func.count(models.Order.id).label("code_usage")
        )
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id,
            # Filter out empty, null, or 'nan' values
            models.Order.discount_code.isnot(None),
            models.Order.discount_code != "",
            models.Order.discount_code != "nan"
        )
        .group_by(models.Order.discount_code)
        .order_by(func.count(models.Order.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "discount_code": row.discount_code,
            "code_usage": row.code_usage
        }
        for row in results
    ]

def get_top_discount_codes_by_savings(db: Session, user_id: int, upload_id: int, limit: int = 5):
    """
    Return top discount codes by total discount_amount across orders.
    Filter out empty, null, or 'nan' values.
    """
    results = (
        db.query(
            models.Order.discount_code.label("discount_code"),
            func.sum(models.Order.discount_amount).label("total_discount")
        )
        .filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id,
            # Filter out empty, null, or 'nan' values
            models.Order.discount_code.isnot(None),
            models.Order.discount_code != "",
            models.Order.discount_code != "nan",
            # Ensure discount_amount is valid
            models.Order.discount_amount.isnot(None),
            models.Order.discount_amount > 0
        )
        .group_by(models.Order.discount_code)
        .order_by(func.sum(models.Order.discount_amount).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "discount_code": row.discount_code,
            "total_discount": float(row.total_discount or 0)
        }
        for row in results
    ]

def get_repeat_customer_metrics(db: Session, user_id: int, upload_id: int):
    """
    Combines repeat customer count + unique customer count,
    and calculates the repeat rate (percentage).
    """
    unique_count = get_unique_customer_count(db, user_id, upload_id)
    repeat_count = get_repeat_customer_count(db, user_id, upload_id)

    if unique_count > 0:
        repeat_rate = float(repeat_count) / float(unique_count) * 100.0
    else:
        repeat_rate = 0.0

    return {
        "unique_count": unique_count,
        "repeat_count": repeat_count,
        "repeat_rate_percent": repeat_rate
    }


# A central registry that maps "keys" to aggregator functions and descriptive info
ANALYTICS_REGISTRY = {
    "orders_summary": {
        "label": "Orders Summary",
        "description": "Returns total orders, total revenue, and average order value (AOV).",
        "handler": get_orders_summary,
    },
    "time_series": {
        "label": "Daily Time Series",
        "description": "Groups orders by day, returning the number of orders each day.",
        "handler": get_orders_time_series,
    },
    "top_cities_by_orders": {
        "label": "Top Cities (by Order Count)",
        "description": "Rank shipping cities by how many orders.",
        "handler": get_top_cities_by_orders,
    },
    "top_cities_by_revenue": {
        "label": "Top Cities (by Revenue)",
        "description": "Rank shipping cities by total revenue (sum of Order.total).",
        "handler": get_top_cities_by_revenue,
    },
    "top_products_by_quantity": {
        "label": "Top Products (by Quantity)",
        "description": "Rank line items by total quantity sold.",
        "handler": get_top_products_by_quantity,
    },
    "top_products_by_revenue": {
        "label": "Top Products (by Revenue)",
        "description": "Rank line items by total revenue (price * quantity).",
        "handler": get_top_products_by_revenue,
    },
    "repeat_customers": {
        "label": "Repeat Customer Metrics",
        "description": "Combines repeat & unique customers, plus the repeat purchase rate.",
        "handler": get_repeat_customer_metrics,
    },
    "orders_by_hour": {
        "label": "Hourly Orders",
        "description": "Groups orders by hour of the day (date_trunc('hour', created_at)).",
        "handler": get_orders_by_hour,
    },
    "orders_by_day_of_week": {
        "label": "Orders by Day of Week",
        "description": "Groups orders by day of week (0=Sunday, 1=Monday, ...).",
        "handler": get_orders_by_day_of_week,
    },
    "top_discount_codes": {
        "label": "Top Discount Codes (by usage)",
        "description": "Shows which discount codes were used most frequently on orders.",
        "handler": get_top_discount_codes,
    },
    "top_discount_codes_by_savings": {
        "label": "Top Discount Codes (by total discount)",
        "description": "Shows which discount codes created the greatest total discount_amount.",
        "handler": get_top_discount_codes_by_savings,
    },
}
