# backend/core/orders_processing.py

import math
import pandas as pd
from datetime import datetime
from db import models
from db.database import SessionLocal
from sqlalchemy.orm import Session

def safe_float(val, default=None):
    """
    Attempts to parse float from val.
    Returns default if invalid or empty.
    
    Args:
        val: The value to convert to float
        default: The default value to return if conversion fails (default is None)
    
    Returns:
        float or default: The converted float value or default if conversion fails
    """
    if val is None or (isinstance(val, str) and not val.strip()):
        return default
    try:
        f = float(val)
        if not math.isfinite(f):
            return default
        return f
    except (ValueError, TypeError):
        return default

def safe_date(val):
    """
    Attempts to parse a date/datetime from val using pandas.
    Returns None if invalid or empty.
    """
    if val is None or (isinstance(val, str) and not val.strip()):
        return None
    try:
        parsed = pd.to_datetime(val, errors='coerce', utc=False)
        if pd.isna(parsed):
            return None
        return parsed.to_pydatetime()
    except Exception:
        return None

def read_order_file(file_path: str) -> pd.DataFrame:
    """
    Reads a CSV or other supported file and returns a DataFrame.
    Adjust for Excel/JSON if needed.
    """
    if file_path.lower().endswith(".csv"):
        return pd.read_csv(file_path, low_memory=False)
    # elif file_path.lower().endswith((".xls", ".xlsx")):
    #     return pd.read_excel(file_path)
    # elif file_path.lower().endswith(".json"):
    #     return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file extension for {file_path}")

def bulk_insert_orders(db: Session, orders_data: list[dict]):
    db.bulk_insert_mappings(models.Order, orders_data)

def bulk_insert_line_items(db: Session, lineitems_data: list[dict]):
    db.bulk_insert_mappings(models.LineItem, lineitems_data)

def process_shopify_file(file_location: str, user_id: int, upload_id: int):
    """
    Reads the CSV with line items + repeated order-level columns.
    1) Parse all rows to build a dictionary keyed by "Shopify Order ID" (e.g. row["Name"]).
       Each key has a single "order_data" + multiple "line_items".
    2) Bulk insert all orders, fetch their new primary keys.
    3) Bulk insert line items referencing the correct order PK.

    Also updates Upload.records_processed so the front-end can show progress.
    """
    db = SessionLocal()
    try:
        # 1) Mark upload as "processing"
        upload = db.query(models.Upload).filter(
            models.Upload.id == upload_id,
            models.Upload.user_id == user_id
        ).first()
        if not upload:
            print(f"No matching Upload record for upload_id={upload_id}, user_id={user_id}")
            return
        upload.status = "processing"
        db.commit()

        # 2) Read file -> DataFrame
        df = read_order_file(file_location)
        total_rows = len(df)
        upload.total_rows = total_rows
        db.commit()

        # 3) Phase 1: Collect orders + line items in memory,
        #    keyed by "Shopify order identifier" (e.g. row["Name"] or row["Id"]).
        #    Each entry: {"order_data": {...}, "line_items": [ {...}, {...} ]}
        orders_map = {}
        processed = 0

        for idx, row in df.iterrows():
            # Use "Name" or "Id" from CSV as the unique key
            # Example: order_key = row.get("Name")
            # If "Id" is the unique Shopify ID, use that instead
            order_key = str(row.get("Name") or row.get("Id") or f"unknown_{idx}")

            # If first time seeing this order_key, create the structure
            if order_key not in orders_map:
                # Build the order_data dict from the CSV row
                # We must fill 'name' and 'email' to avoid NOT NULL violation
                order_data = {
                    "user_id": user_id,
                    "upload_id": upload_id,
                    "order_id": str(row.get("Id") or row.get("Name") or ""),
                    "name": str(row.get("Name") or "Unnamed Order"),
                    "email": str(row.get("Email") or "missing@example.com"),
                    "financial_status": str(row.get("Financial Status") or ""),
                    "paid_at": safe_date(row.get("Paid at")),
                    "fulfillment_status": str(row.get("Fulfillment Status") or ""),
                    "fulfilled_at": safe_date(row.get("Fulfilled at")),
                    "accepts_marketing": str(row.get("Accepts Marketing") or ""),
                    "currency": str(row.get("Currency") or ""),
                    "subtotal": safe_float(row.get("Subtotal")),
                    "shipping": safe_float(row.get("Shipping")),
                    "taxes": safe_float(row.get("Taxes")),
                    "total": safe_float(row.get("Total")),
                    "discount_code": str(row.get("Discount Code") or ""),
                    "discount_amount": safe_float(row.get("Discount Amount")),
                    "shipping_method": str(row.get("Shipping Method") or ""),
                    "created_at": safe_date(row.get("Created at")),
                    "cancelled_at": safe_date(row.get("Cancelled at")),
                    "payment_method": str(row.get("Payment Method") or ""),
                    "payment_reference": str(row.get("Payment Reference") or ""),
                    "refunded_amount": safe_float(row.get("Refunded Amount")),
                    "vendor": str(row.get("Vendor") or ""),
                    "outstanding_balance": safe_float(row.get("Outstanding Balance")),
                    "employee": str(row.get("Employee") or ""),
                    "location": str(row.get("Location") or ""),
                    "device_id": str(row.get("Device ID") or ""),
                    "tags": str(row.get("Tags") or ""),
                    "risk_level": str(row.get("Risk Level") or ""),
                    "source": str(row.get("Source") or ""),
                    "phone": str(row.get("Phone") or ""),
                    "receipt_number": str(row.get("Receipt Number") or ""),
                    "duties": safe_float(row.get("Duties")),
                    "billing_name": str(row.get("Billing Name") or ""),
                    "billing_street": str(row.get("Billing Street") or ""),
                    "billing_address1": str(row.get("Billing Address1") or ""),
                    "billing_address2": str(row.get("Billing Address2") or ""),
                    "billing_company": str(row.get("Billing Company") or ""),
                    "billing_city": str(row.get("Billing City") or ""),
                    "billing_zip": str(row.get("Billing Zip") or ""),
                    "billing_province": str(row.get("Billing Province") or ""),
                    "billing_country": str(row.get("Billing Country") or ""),
                    "billing_phone": str(row.get("Billing Phone") or ""),
                    "billing_province_name": str(row.get("Billing Province Name") or ""),
                    "shipping_name": str(row.get("Shipping Name") or ""),
                    "shipping_street": str(row.get("Shipping Street") or ""),
                    "shipping_address1": str(row.get("Shipping Address1") or ""),
                    "shipping_address2": str(row.get("Shipping Address2") or ""),
                    "shipping_company": str(row.get("Shipping Company") or ""),
                    "shipping_city": str(row.get("Shipping City") or ""),
                    "shipping_zip": str(row.get("Shipping Zip") or ""),
                    "shipping_province": str(row.get("Shipping Province") or ""),
                    "shipping_country": str(row.get("Shipping Country") or ""),
                    "shipping_phone": str(row.get("Shipping Phone") or ""),
                    "shipping_province_name": str(row.get("Shipping Province Name") or ""),
                    "payment_id": str(row.get("Payment ID") or ""),
                    "payment_terms_name": str(row.get("Payment Terms Name") or ""),
                    "next_payment_due_at": safe_date(row.get("Next Payment Due At")),
                    "payment_references": str(row.get("Payment References") or ""),
                }

                orders_map[order_key] = {
                    "order_data": order_data,
                    "line_items": []
                }

            # Build line item dict from the row
            # We'll link it to the actual `order_id` PK after we insert the orders
            # Ensure all numeric values are properly converted to float or default to 0
            # This prevents empty strings from being stored in numeric fields
            lineitem_price = safe_float(row.get("Lineitem price"), 0)
            lineitem_compare_price = safe_float(row.get("Lineitem compare at price"), 0)
            lineitem_discount = safe_float(row.get("Lineitem discount"), 0)
            lineitem_quantity = safe_float(row.get("Lineitem quantity"), 0)
            
            # Skip line items with invalid prices or quantities
            if lineitem_price is None or lineitem_quantity is None:
                processed += 1
                continue
                
            line_item_data = {
                "lineitem_quantity": lineitem_quantity,
                "lineitem_name": str(row.get("Lineitem name") or ""),
                "lineitem_price": lineitem_price,
                "lineitem_compare_at_price": lineitem_compare_price,
                "lineitem_sku": str(row.get("Lineitem sku") or ""),
                "lineitem_requires_shipping": str(row.get("Lineitem requires shipping") or ""),
                "lineitem_taxable": str(row.get("Lineitem taxable") or ""),
                "lineitem_fulfillment_status": str(row.get("Lineitem fulfillment status") or ""),
                "lineitem_discount": lineitem_discount,
                "variant_id": str(row.get("Lineitem sku") or ""),
                "order_id": None,  # We'll fill in later once we know the DB PK
            }

            orders_map[order_key]["line_items"].append(line_item_data)
            processed += 1

            # Optionally update upload.records_processed every few rows
            if processed % 1000 == 0:
                upload.records_processed = processed
                db.commit()

        # After we finish reading the CSV, set final processed
        upload.records_processed = processed
        db.commit()

        # 4) Phase 2: Bulk insert the unique orders, then fetch them to get PK -> link line items

        # 4a) Build a list of all unique order dicts
        all_orders = []
        for order_key, order_dict in orders_map.items():
            all_orders.append(order_dict["order_data"])

        # Bulk insert orders in BATCH_SIZE lumps
        # We'll gather them in a list, then do chunked inserts
        inserted_orders = []
        BATCH_SIZE = 1000
        start_idx = 0
        while start_idx < len(all_orders):
            chunk = all_orders[start_idx:start_idx + BATCH_SIZE]
            db.bulk_insert_mappings(models.Order, chunk)
            db.commit()
            start_idx += BATCH_SIZE

        # 4b) Now fetch those orders from the DB so we know their primary keys
        # We'll match them by (user_id, upload_id, order_id) if it's unique
        # Then build a dictionary: (order_id_str) -> DB PK
        # Because we stored "order_id" in "order_data['order_id']"
        # But if you rely on "Name" as the unique key, adapt accordingly
        found_orders = db.query(models.Order).filter(
            models.Order.user_id == user_id,
            models.Order.upload_id == upload_id
        ).all()

        pk_map = {}  # maps (the CSV order_id string) => actual DB PK
        for o in found_orders:
            csv_order_id_str = o.order_id  # we used "order_id": str(row.get("Id") or row.get("Name"))
            if csv_order_id_str not in pk_map:  # take the first match
                pk_map[csv_order_id_str] = o.id

        # 4c) Build the final line items with real `order_id` PK
        all_line_items = []
        for order_key, data_dict in orders_map.items():
            # The CSV's "order_id" string
            csv_order_id_str = data_dict["order_data"]["order_id"]
            if csv_order_id_str in pk_map:
                real_order_pk = pk_map[csv_order_id_str]
            else:
                # fallback if somehow not found
                real_order_pk = None

            for li in data_dict["line_items"]:
                li["order_id"] = real_order_pk
                all_line_items.append(li)

        # 4d) Bulk insert line items in BATCH_SIZE lumps
        start_idx = 0
        while start_idx < len(all_line_items):
            chunk = all_line_items[start_idx:start_idx + BATCH_SIZE]
            db.bulk_insert_mappings(models.LineItem, chunk)
            db.commit()
            start_idx += BATCH_SIZE

        # 5) Mark upload as completed
        upload.records_processed = processed
        upload.status = "completed"
        db.commit()

    except Exception as e:
        db.rollback()
        if upload:
            upload.status = "failed"
            db.commit()
        print("Error processing file:", e)
    finally:
        db.close()
