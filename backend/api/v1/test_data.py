# api/v1/test_data.py

import os
import csv
import random
import string
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.deps import get_db, get_current_user
from db import models

router = APIRouter(tags=["test_data"])

# Define the request model for test data generation
class TestDataRequest(BaseModel):
    num_orders: int = Field(..., description="Number of orders to generate", ge=1, le=10000)
    start_date: datetime = Field(..., description="Start date for the orders")
    end_date: datetime = Field(..., description="End date for the orders")
    min_items_per_order: int = Field(1, description="Minimum number of line items per order", ge=1)
    max_items_per_order: int = Field(5, description="Maximum number of line items per order", ge=1)
    include_discounts: bool = Field(True, description="Whether to include discounts")
    include_shipping: bool = Field(True, description="Whether to include shipping")
    include_taxes: bool = Field(True, description="Whether to include taxes")
    output_file: str = Field("test_orders.csv", description="Name of the output file")

# Sample product data
PRODUCTS = [
    {"name": "FF01 - Poly-Cotton Crew Neck T-Shirt - Black", "price": 20.00, "sku": "FF01BLK", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF01 - Poly-Cotton Crew Neck T-Shirt - White", "price": 20.00, "sku": "FF01WHT", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF01 - Poly-Cotton Crew Neck T-Shirt - Heather Lake Blue", "price": 20.00, "sku": "FF01HTRBLU", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF02 - Poly-Cotton V-Neck T-Shirt - Black", "price": 22.00, "sku": "FF02BLK", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF02 - Poly-Cotton V-Neck T-Shirt - White", "price": 22.00, "sku": "FF02WHT", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF03 - Premium Cotton Hoodie - Black", "price": 45.00, "sku": "FF03BLK", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF03 - Premium Cotton Hoodie - Gray", "price": 45.00, "sku": "FF03GRY", "sizes": ["S", "M", "L", "XL", "XXL"]},
    {"name": "FF04 - Slim Fit Jeans - Blue", "price": 65.00, "sku": "FF04BLU", "sizes": ["28", "30", "32", "34", "36"]},
    {"name": "FF04 - Slim Fit Jeans - Black", "price": 65.00, "sku": "FF04BLK", "sizes": ["28", "30", "32", "34", "36"]},
    {"name": "Gift Card - 15", "price": 15.00, "sku": "Giftcard15", "sizes": [""]},
    {"name": "Gift Card - 25", "price": 25.00, "sku": "Giftcard25", "sizes": [""]},
    {"name": "Gift Card - 50", "price": 50.00, "sku": "Giftcard50", "sizes": [""]},
]

# Sample discount codes
DISCOUNT_CODES = [
    {"code": "WELCOME10", "percent": 0.10},
    {"code": "SUMMER20", "percent": 0.20},
    {"code": "FLASH30", "percent": 0.30},
    {"code": "FREESHIP", "percent": 0.0, "free_shipping": True},
]

# Sample shipping methods
SHIPPING_METHODS = [
    {"name": "Economy Shipping", "cost": 7.50},
    {"name": "Standard Shipping", "cost": 10.00},
    {"name": "Express Shipping", "cost": 15.00},
]

# Sample states with tax rates
STATES = [
    {"name": "Texas", "code": "TX", "tax_rate": 0.0825},
    {"name": "California", "code": "CA", "tax_rate": 0.0725},
    {"name": "New York", "code": "NY", "tax_rate": 0.0845},
    {"name": "Florida", "code": "FL", "tax_rate": 0.06},
    {"name": "Illinois", "code": "IL", "tax_rate": 0.0625},
]

# Sample cities for each state
CITIES = {
    "TX": ["Austin", "Dallas", "Houston", "San Antonio", "Fort Worth"],
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    "NY": ["New York", "Buffalo", "Rochester", "Syracuse", "Albany"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"],
    "IL": ["Chicago", "Springfield", "Peoria", "Rockford", "Champaign"],
}

def generate_random_name():
    """Generate a random name for testing."""
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", "William", "Jessica", "Ty", "Emma", "Daniel", "Olivia"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Root", "Jackson"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name):
    """Generate a random email based on name."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "example.com"]
    name_parts = name.lower().split()
    if random.random() < 0.5:
        username = f"{name_parts[0]}{name_parts[1][0]}"
    else:
        username = f"{name_parts[0][0]}{name_parts[1]}"
    
    if random.random() < 0.3:
        username += str(random.randint(1, 99))
    
    return f"{username}@{random.choice(domains)}"

def generate_random_address():
    """Generate a random address for testing."""
    street_numbers = [str(random.randint(100, 9999)) for _ in range(20)]
    street_names = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Washington Ave", "Park Dr", "Lake Rd", "River St", "Flameleaf Sumac Drive"]
    
    state = random.choice(STATES)
    city = random.choice(CITIES[state["code"]])
    zip_codes = [f"{random.randint(10000, 99999)}" for _ in range(10)]
    
    return {
        "street": f"{random.choice(street_numbers)} {random.choice(street_names)}",
        "city": city,
        "state": state["name"],
        "state_code": state["code"],
        "zip": random.choice(zip_codes),
        "tax_rate": state["tax_rate"]
    }

def generate_random_phone():
    """Generate a random phone number."""
    area_code = random.randint(100, 999)
    prefix = random.randint(100, 999)
    line = random.randint(1000, 9999)
    return f"+1 {area_code}-{prefix}-{line}"

def generate_test_data(request: TestDataRequest):
    """Generate test data based on the request parameters."""
    # Create the uploads directory if it doesn't exist
    UPLOAD_DIR = "/app/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Create the output file path
    output_path = os.path.join(UPLOAD_DIR, request.output_file)
    
    # Calculate the date range and distribution
    date_range = (request.end_date - request.start_date).days
    if date_range <= 0:
        raise ValueError("End date must be after start date")
    
    # Generate random dates for orders
    order_dates = []
    for _ in range(request.num_orders):
        random_days = random.randint(0, date_range)
        order_date = request.start_date + timedelta(days=random_days)
        # Add some time variation
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        order_date = order_date.replace(hour=hour, minute=minute, second=second)
        order_dates.append(order_date)
    
    # Sort dates to make them chronological
    order_dates.sort()
    
    # Generate order IDs
    order_ids = [1080000 + i for i in range(request.num_orders)]
    
    # Generate orders with line items
    orders = []
    for i in range(request.num_orders):
        # Generate customer information
        customer_name = generate_random_name()
        customer_email = generate_random_email(customer_name)
        address = generate_random_address()
        phone = generate_random_phone()
        
        # Generate order details
        order_id = order_ids[i]
        order_date = order_dates[i]
        
        # Determine if this order has a discount
        has_discount = request.include_discounts and random.random() < 0.3
        discount = random.choice(DISCOUNT_CODES) if has_discount else None
        
        # Determine shipping method
        shipping_method = random.choice(SHIPPING_METHODS) if request.include_shipping else None
        
        # Generate line items
        num_items = random.randint(request.min_items_per_order, request.max_items_per_order)
        line_items = []
        for _ in range(num_items):
            product = random.choice(PRODUCTS)
            size_code = random.choice([1, 2, 3, 4, 5])
            size = product["sizes"][size_code - 1] if product["sizes"] else ""
            
            # For gift cards, no size
            if "Gift Card" in product["name"]:
                item_name = product["name"]
                item_sku = product["sku"]
                requires_shipping = "false"
                taxable = "false"
            else:
                item_name = f"{product['name']} / {size}"
                item_sku = f"{product['sku']}{size_code:02d}"
                requires_shipping = "true"
                taxable = "true"
            
            line_item = {
                "name": item_name,
                "price": product["price"],
                "sku": item_sku,
                "requires_shipping": requires_shipping,
                "taxable": taxable,
                "quantity": random.randint(1, 3)
            }
            line_items.append(line_item)
        
        # Calculate order totals
        subtotal = sum(item["price"] * item["quantity"] for item in line_items)
        
        # Apply discount if applicable
        discount_amount = 0
        if discount:
            if hasattr(discount, "free_shipping"):
                shipping_cost = 0
            else:
                discount_amount = subtotal * discount["percent"]
        
        # Add shipping cost if applicable
        shipping_cost = shipping_method["cost"] if shipping_method else 0
        
        # Calculate taxes if applicable
        tax_amount = 0
        if request.include_taxes:
            taxable_amount = subtotal - discount_amount
            tax_amount = taxable_amount * address["tax_rate"]
        
        # Calculate total
        total = subtotal - discount_amount + shipping_cost + tax_amount
        
        # Create the order
        order = {
            "id": order_id,
            "name": f"#{order_id}",
            "email": customer_email,
            "financial_status": "paid",
            "paid_at": order_date.strftime("%Y-%m-%d %H:%M:%S %z"),
            "fulfillment_status": "unfulfilled",
            "fulfilled_at": "",
            "accepts_marketing": "yes" if random.random() < 0.7 else "no",
            "currency": "USD",
            "subtotal": f"{subtotal:.2f}",
            "shipping": f"{shipping_cost:.2f}",
            "taxes": f"{tax_amount:.2f}",
            "total": f"{total:.2f}",
            "discount_code": discount["code"] if discount else "",
            "discount_amount": f"{discount_amount:.2f}",
            "shipping_method": shipping_method["name"] if shipping_method else "",
            "created_at": order_date.strftime("%Y-%m-%d %H:%M:%S %z"),
            "cancelled_at": "",
            "payment_method": "Shopify Payments",
            "payment_reference": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
            "refunded_amount": "0.00",
            "vendor": "Los Angeles Apparel",
            "outstanding_balance": "0.00",
            "employee": "",
            "location": "",
            "device_id": "",
            "billing_name": customer_name,
            "billing_street": address["street"],
            "billing_address1": address["street"],
            "billing_address2": "",
            "billing_company": "",
            "billing_city": address["city"],
            "billing_zip": address["zip"],
            "billing_province": address["state_code"],
            "billing_country": "US",
            "billing_phone": phone,
            "billing_province_name": address["state"],
            "shipping_name": customer_name,
            "shipping_street": address["street"],
            "shipping_address1": address["street"],
            "shipping_address2": "",
            "shipping_company": "",
            "shipping_city": address["city"],
            "shipping_zip": address["zip"],
            "shipping_province": address["state_code"],
            "shipping_country": "US",
            "shipping_phone": phone,
            "shipping_province_name": address["state"],
            "line_items": line_items
        }
        
        orders.append(order)
    
    # Write to CSV file
    with open(output_path, 'w', newline='') as csvfile:
        # Get all possible field names from the first order and its line items
        first_order = orders[0]
        order_fields = list(first_order.keys())
        order_fields.remove("line_items")  # Remove line_items as it's not a direct field
        
        # Add line item fields with "Lineitem" prefix
        line_item_fields = [
            "Lineitem quantity", "Lineitem name", "Lineitem price", 
            "Lineitem compare at price", "Lineitem sku", "Lineitem requires shipping",
            "Lineitem taxable", "Lineitem fulfillment status", "Lineitem discount"
        ]
        
        # Combine all fields
        all_fields = order_fields + line_item_fields
        
        writer = csv.DictWriter(csvfile, fieldnames=all_fields)
        writer.writeheader()
        
        # Write each order with its line items
        for order in orders:
            line_items = order.pop("line_items")
            
            # Write the first row with order details and first line item
            if line_items:
                first_item = line_items[0]
                row = order.copy()
                row["Lineitem quantity"] = first_item["quantity"]
                row["Lineitem name"] = first_item["name"]
                row["Lineitem price"] = first_item["price"]
                row["Lineitem compare at price"] = ""
                row["Lineitem sku"] = first_item["sku"]
                row["Lineitem requires shipping"] = first_item["requires_shipping"]
                row["Lineitem taxable"] = first_item["taxable"]
                row["Lineitem fulfillment status"] = "pending"
                row["Lineitem discount"] = "0.00"
                writer.writerow(row)
                
                # Write additional rows for remaining line items
                for item in line_items[1:]:
                    # Create a row with minimal order info and line item details
                    item_row = {field: "" for field in all_fields}
                    item_row["name"] = f"#{order['id']}"
                    item_row["email"] = order["email"]
                    item_row["created_at"] = order["created_at"]
                    item_row["Lineitem quantity"] = item["quantity"]
                    item_row["Lineitem name"] = item["name"]
                    item_row["Lineitem price"] = item["price"]
                    item_row["Lineitem compare at price"] = ""
                    item_row["Lineitem sku"] = item["sku"]
                    item_row["Lineitem requires shipping"] = item["requires_shipping"]
                    item_row["Lineitem taxable"] = item["taxable"]
                    item_row["Lineitem fulfillment status"] = "pending"
                    item_row["Lineitem discount"] = "0.00"
                    item_row["vendor"] = order["vendor"]
                    writer.writerow(item_row)
            else:
                # Write just the order with empty line item fields
                row = order.copy()
                for field in line_item_fields:
                    row[field] = ""
                writer.writerow(row)
    
    return {
        "file_path": output_path,
        "num_orders": request.num_orders,
        "num_line_items": sum(len(order["line_items"]) for order in orders),
        "date_range": f"{request.start_date.date()} to {request.end_date.date()}"
    }

@router.post("/generate", summary="Generate test order data in Shopify format")
async def generate_test_order_data(
    request: TestDataRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate test order data in Shopify format.
    
    This endpoint creates a CSV file with randomly generated order data
    that matches the Shopify export format. The data can be used for
    testing the analytics and forecasting functionality.
    
    Parameters:
    - num_orders: Number of orders to generate
    - start_date: Start date for the orders
    - end_date: End date for the orders
    - min_items_per_order: Minimum number of line items per order
    - max_items_per_order: Maximum number of line items per order
    - include_discounts: Whether to include discounts
    - include_shipping: Whether to include shipping
    - include_taxes: Whether to include taxes
    - output_file: Name of the output file
    
    Returns:
    - Information about the generated file
    """
    try:
        result = generate_test_data(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test data: {str(e)}")
