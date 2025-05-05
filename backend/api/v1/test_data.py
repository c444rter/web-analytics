# api/v1/test_data.py

import os
import csv
import random
import string
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.deps import get_db, get_current_user
from db import models

router = APIRouter(tags=["test_data"])

# Define the request model for test data generation
class TestDataRequest(BaseModel):
    num_orders: int = Field(..., description="Number of orders to generate", ge=1, le=1000000)
    start_date: datetime = Field(..., description="Start date for the orders")
    end_date: datetime = Field(..., description="End date for the orders")
    min_items_per_order: int = Field(1, description="Minimum number of line items per order", ge=1)
    max_items_per_order: int = Field(5, description="Maximum number of line items per order", ge=1)
    include_discounts: bool = Field(True, description="Whether to include discounts")
    include_shipping: bool = Field(True, description="Whether to include shipping")
    include_taxes: bool = Field(True, description="Whether to include taxes")
    output_file: str = Field("test_orders.csv", description="Name of the output file")
    batch_size: int = Field(10000, description="Batch size for processing large order volumes", ge=1000)

# Generic product categories with diverse items
PRODUCT_CATEGORIES = {
    "Electronics": [
        {"name": "Premium Smartphone - 128GB", "price": 799.99, "sku": "ELEC-SP-128", "variations": ["Black", "Silver", "Gold"], "attributes": {"storage": "128GB"}},
        {"name": "Premium Smartphone - 256GB", "price": 899.99, "sku": "ELEC-SP-256", "variations": ["Black", "Silver", "Gold"], "attributes": {"storage": "256GB"}},
        {"name": "Budget Smartphone", "price": 299.99, "sku": "ELEC-BSP", "variations": ["Black", "Blue", "Red"], "attributes": {"storage": "64GB"}},
        {"name": "Wireless Earbuds", "price": 129.99, "sku": "ELEC-WEB", "variations": ["White", "Black"], "attributes": {}},
        {"name": "Noise-Cancelling Headphones", "price": 249.99, "sku": "ELEC-NCH", "variations": ["Black", "Silver"], "attributes": {}},
        {"name": "Ultra HD Smart TV - 55\"", "price": 699.99, "sku": "ELEC-TV-55", "variations": [], "attributes": {"size": "55 inch"}},
        {"name": "Ultra HD Smart TV - 65\"", "price": 999.99, "sku": "ELEC-TV-65", "variations": [], "attributes": {"size": "65 inch"}},
        {"name": "Laptop - Core i5", "price": 849.99, "sku": "ELEC-LT-I5", "variations": ["Silver", "Space Gray"], "attributes": {"processor": "Core i5", "ram": "8GB"}},
        {"name": "Laptop - Core i7", "price": 1249.99, "sku": "ELEC-LT-I7", "variations": ["Silver", "Space Gray"], "attributes": {"processor": "Core i7", "ram": "16GB"}},
        {"name": "Wireless Charging Pad", "price": 39.99, "sku": "ELEC-WCP", "variations": ["Black", "White"], "attributes": {}}
    ],
    "Home & Kitchen": [
        {"name": "Stainless Steel Cookware Set", "price": 199.99, "sku": "HOME-SSCS", "variations": [], "attributes": {"pieces": "10-piece"}},
        {"name": "Stand Mixer", "price": 279.99, "sku": "HOME-STMX", "variations": ["Red", "Black", "Silver"], "attributes": {}},
        {"name": "Coffee Maker", "price": 89.99, "sku": "HOME-CM", "variations": ["Black", "Stainless Steel"], "attributes": {}},
        {"name": "Blender", "price": 69.99, "sku": "HOME-BLDR", "variations": ["Black", "White"], "attributes": {}},
        {"name": "Toaster Oven", "price": 119.99, "sku": "HOME-TSTR", "variations": ["Stainless Steel", "Black"], "attributes": {}},
        {"name": "Air Purifier", "price": 149.99, "sku": "HOME-AIRP", "variations": ["White"], "attributes": {}},
        {"name": "Robot Vacuum", "price": 299.99, "sku": "HOME-RVAC", "variations": ["Black"], "attributes": {}},
        {"name": "Bed Sheets - Queen", "price": 59.99, "sku": "HOME-BS-Q", "variations": ["White", "Gray", "Blue"], "attributes": {"size": "Queen"}},
        {"name": "Bed Sheets - King", "price": 69.99, "sku": "HOME-BS-K", "variations": ["White", "Gray", "Blue"], "attributes": {"size": "King"}},
        {"name": "Towel Set", "price": 39.99, "sku": "HOME-TWLS", "variations": ["White", "Gray", "Blue"], "attributes": {"pieces": "6-piece"}}
    ],
    "Clothing": [
        {"name": "Men's Basic T-Shirt", "price": 19.99, "sku": "CLTH-MTS", "variations": ["Black", "White", "Gray", "Navy"], "attributes": {"gender": "Men"}, "sizes": ["S", "M", "L", "XL", "XXL"]},
        {"name": "Women's Basic T-Shirt", "price": 19.99, "sku": "CLTH-WTS", "variations": ["Black", "White", "Gray", "Pink"], "attributes": {"gender": "Women"}, "sizes": ["XS", "S", "M", "L", "XL"]},
        {"name": "Men's Jeans - Slim Fit", "price": 49.99, "sku": "CLTH-MJ-SF", "variations": ["Blue", "Black"], "attributes": {"gender": "Men", "fit": "Slim"}, "sizes": ["28", "30", "32", "34", "36", "38"]},
        {"name": "Women's Jeans - Skinny", "price": 49.99, "sku": "CLTH-WJ-SK", "variations": ["Blue", "Black"], "attributes": {"gender": "Women", "fit": "Skinny"}, "sizes": ["24", "26", "28", "30", "32"]},
        {"name": "Men's Hoodie", "price": 39.99, "sku": "CLTH-MH", "variations": ["Black", "Gray", "Navy"], "attributes": {"gender": "Men"}, "sizes": ["S", "M", "L", "XL", "XXL"]},
        {"name": "Women's Hoodie", "price": 39.99, "sku": "CLTH-WH", "variations": ["Black", "Gray", "Pink"], "attributes": {"gender": "Women"}, "sizes": ["XS", "S", "M", "L", "XL"]},
        {"name": "Men's Dress Shirt", "price": 59.99, "sku": "CLTH-MDS", "variations": ["White", "Blue", "Black"], "attributes": {"gender": "Men"}, "sizes": ["S", "M", "L", "XL", "XXL"]},
        {"name": "Women's Blouse", "price": 44.99, "sku": "CLTH-WB", "variations": ["White", "Black", "Red"], "attributes": {"gender": "Women"}, "sizes": ["XS", "S", "M", "L", "XL"]},
        {"name": "Men's Shorts", "price": 29.99, "sku": "CLTH-MS", "variations": ["Khaki", "Navy", "Black"], "attributes": {"gender": "Men"}, "sizes": ["28", "30", "32", "34", "36", "38"]},
        {"name": "Women's Shorts", "price": 29.99, "sku": "CLTH-WS", "variations": ["Khaki", "Navy", "Black"], "attributes": {"gender": "Women"}, "sizes": ["24", "26", "28", "30", "32"]}
    ],
    "Books & Media": [
        {"name": "Bestselling Fiction Novel", "price": 24.99, "sku": "BOOK-FIC", "variations": [], "attributes": {"format": "Hardcover"}},
        {"name": "Bestselling Fiction Novel - Paperback", "price": 14.99, "sku": "BOOK-FIC-PB", "variations": [], "attributes": {"format": "Paperback"}},
        {"name": "Bestselling Fiction Novel - E-book", "price": 9.99, "sku": "BOOK-FIC-EB", "variations": [], "attributes": {"format": "E-book"}},
        {"name": "Popular Non-Fiction Book", "price": 27.99, "sku": "BOOK-NF", "variations": [], "attributes": {"format": "Hardcover"}},
        {"name": "Popular Non-Fiction Book - Paperback", "price": 17.99, "sku": "BOOK-NF-PB", "variations": [], "attributes": {"format": "Paperback"}},
        {"name": "Popular Non-Fiction Book - E-book", "price": 12.99, "sku": "BOOK-NF-EB", "variations": [], "attributes": {"format": "E-book"}},
        {"name": "Blockbuster Movie - Blu-ray", "price": 24.99, "sku": "MEDIA-MOV-BR", "variations": [], "attributes": {"format": "Blu-ray"}},
        {"name": "Blockbuster Movie - DVD", "price": 19.99, "sku": "MEDIA-MOV-DVD", "variations": [], "attributes": {"format": "DVD"}},
        {"name": "Popular TV Series - Complete Season", "price": 39.99, "sku": "MEDIA-TV", "variations": [], "attributes": {"format": "Blu-ray"}},
        {"name": "Chart-topping Music Album", "price": 14.99, "sku": "MEDIA-MUS", "variations": [], "attributes": {"format": "CD"}}
    ],
    "Sports & Outdoors": [
        {"name": "Yoga Mat", "price": 29.99, "sku": "SPORT-YM", "variations": ["Purple", "Blue", "Black"], "attributes": {}},
        {"name": "Dumbbells - 5lb Pair", "price": 24.99, "sku": "SPORT-DB-5", "variations": [], "attributes": {"weight": "5lb"}},
        {"name": "Dumbbells - 10lb Pair", "price": 34.99, "sku": "SPORT-DB-10", "variations": [], "attributes": {"weight": "10lb"}},
        {"name": "Dumbbells - 15lb Pair", "price": 44.99, "sku": "SPORT-DB-15", "variations": [], "attributes": {"weight": "15lb"}},
        {"name": "Running Shoes - Men's", "price": 89.99, "sku": "SPORT-RS-M", "variations": ["Black", "Gray", "Blue"], "attributes": {"gender": "Men"}, "sizes": ["7", "8", "9", "10", "11", "12", "13"]},
        {"name": "Running Shoes - Women's", "price": 89.99, "sku": "SPORT-RS-W", "variations": ["Black", "Gray", "Pink"], "attributes": {"gender": "Women"}, "sizes": ["5", "6", "7", "8", "9", "10"]},
        {"name": "Basketball", "price": 29.99, "sku": "SPORT-BB", "variations": [], "attributes": {}},
        {"name": "Tennis Racket", "price": 79.99, "sku": "SPORT-TR", "variations": [], "attributes": {}},
        {"name": "Camping Tent - 2-Person", "price": 129.99, "sku": "SPORT-CT-2", "variations": ["Green", "Blue"], "attributes": {"capacity": "2-Person"}},
        {"name": "Camping Tent - 4-Person", "price": 199.99, "sku": "SPORT-CT-4", "variations": ["Green", "Blue"], "attributes": {"capacity": "4-Person"}}
    ],
    "Beauty & Personal Care": [
        {"name": "Facial Cleanser", "price": 14.99, "sku": "BEAUTY-FC", "variations": [], "attributes": {"skin_type": "All"}},
        {"name": "Moisturizer", "price": 24.99, "sku": "BEAUTY-MSTR", "variations": [], "attributes": {"skin_type": "All"}},
        {"name": "Shampoo", "price": 12.99, "sku": "BEAUTY-SH", "variations": [], "attributes": {"hair_type": "All"}},
        {"name": "Conditioner", "price": 12.99, "sku": "BEAUTY-COND", "variations": [], "attributes": {"hair_type": "All"}},
        {"name": "Body Wash", "price": 9.99, "sku": "BEAUTY-BW", "variations": ["Original", "Lavender"], "attributes": {}},
        {"name": "Perfume", "price": 69.99, "sku": "BEAUTY-PERF", "variations": ["Floral", "Citrus"], "attributes": {}},
        {"name": "Cologne", "price": 69.99, "sku": "BEAUTY-COL", "variations": ["Woody", "Fresh"], "attributes": {}},
        {"name": "Lipstick", "price": 19.99, "sku": "BEAUTY-LS", "variations": ["Red", "Pink", "Nude"], "attributes": {}},
        {"name": "Eyeshadow Palette", "price": 39.99, "sku": "BEAUTY-ESP", "variations": ["Neutral", "Smoky"], "attributes": {}},
        {"name": "Facial Mask", "price": 5.99, "sku": "BEAUTY-FM", "variations": ["Hydrating", "Clarifying"], "attributes": {}}
    ],
    "Toys & Games": [
        {"name": "Building Blocks Set", "price": 29.99, "sku": "TOY-BBS", "variations": [], "attributes": {"age_range": "3-12"}},
        {"name": "Action Figure", "price": 19.99, "sku": "TOY-AF", "variations": ["Hero", "Villain"], "attributes": {"age_range": "4+"}},
        {"name": "Board Game - Family", "price": 24.99, "sku": "TOY-BG-FAM", "variations": [], "attributes": {"players": "2-6", "age_range": "8+"}},
        {"name": "Board Game - Strategy", "price": 34.99, "sku": "TOY-BG-STR", "variations": [], "attributes": {"players": "2-4", "age_range": "12+"}},
        {"name": "Puzzle - 500 Pieces", "price": 14.99, "sku": "TOY-PZ-500", "variations": ["Landscape", "Animals"], "attributes": {"pieces": "500", "age_range": "8+"}},
        {"name": "Puzzle - 1000 Pieces", "price": 19.99, "sku": "TOY-PZ-1000", "variations": ["Landscape", "Animals"], "attributes": {"pieces": "1000", "age_range": "12+"}},
        {"name": "Remote Control Car", "price": 49.99, "sku": "TOY-RCC", "variations": ["Red", "Blue"], "attributes": {"age_range": "6+"}},
        {"name": "Stuffed Animal", "price": 14.99, "sku": "TOY-SA", "variations": ["Bear", "Dog", "Cat"], "attributes": {"age_range": "0+"}},
        {"name": "Educational Toy", "price": 24.99, "sku": "TOY-EDU", "variations": [], "attributes": {"age_range": "3-7"}},
        {"name": "Doll", "price": 29.99, "sku": "TOY-DOLL", "variations": ["Blonde", "Brunette"], "attributes": {"age_range": "3+"}}
    ],
    "Office Supplies": [
        {"name": "Notebook - College Ruled", "price": 4.99, "sku": "OFFICE-NB-CR", "variations": ["Black", "Blue"], "attributes": {}},
        {"name": "Notebook - Wide Ruled", "price": 4.99, "sku": "OFFICE-NB-WR", "variations": ["Black", "Blue"], "attributes": {}},
        {"name": "Pen Set", "price": 12.99, "sku": "OFFICE-PS", "variations": ["Black", "Blue", "Assorted"], "attributes": {"count": "12"}},
        {"name": "Mechanical Pencil Set", "price": 8.99, "sku": "OFFICE-MPS", "variations": [], "attributes": {"count": "6"}},
        {"name": "Stapler", "price": 9.99, "sku": "OFFICE-STPL", "variations": ["Black"], "attributes": {}},
        {"name": "Desk Organizer", "price": 19.99, "sku": "OFFICE-DO", "variations": ["Black", "Silver"], "attributes": {}},
        {"name": "File Folders", "price": 14.99, "sku": "OFFICE-FF", "variations": ["Manila", "Colored"], "attributes": {"count": "25"}},
        {"name": "Printer Paper", "price": 9.99, "sku": "OFFICE-PP", "variations": [], "attributes": {"count": "500 sheets"}},
        {"name": "Sticky Notes", "price": 7.99, "sku": "OFFICE-SN", "variations": ["Yellow", "Assorted"], "attributes": {}},
        {"name": "Desk Lamp", "price": 29.99, "sku": "OFFICE-DL", "variations": ["Black", "Silver"], "attributes": {}}
    ],
    "Grocery & Gourmet": [
        {"name": "Organic Coffee Beans", "price": 14.99, "sku": "GROC-OCB", "variations": ["Light Roast", "Medium Roast", "Dark Roast"], "attributes": {"weight": "12oz"}},
        {"name": "Organic Tea Assortment", "price": 12.99, "sku": "GROC-OTA", "variations": [], "attributes": {"count": "20 bags"}},
        {"name": "Chocolate Gift Box", "price": 24.99, "sku": "GROC-CGB", "variations": ["Assorted", "Dark"], "attributes": {"weight": "8oz"}},
        {"name": "Gourmet Pasta", "price": 6.99, "sku": "GROC-GP", "variations": ["Spaghetti", "Penne", "Fettuccine"], "attributes": {"weight": "16oz"}},
        {"name": "Olive Oil - Extra Virgin", "price": 19.99, "sku": "GROC-OO-EV", "variations": [], "attributes": {"volume": "500ml"}},
        {"name": "Balsamic Vinegar", "price": 14.99, "sku": "GROC-BV", "variations": [], "attributes": {"volume": "250ml"}},
        {"name": "Spice Set", "price": 29.99, "sku": "GROC-SS", "variations": [], "attributes": {"count": "12 spices"}},
        {"name": "Gourmet Snack Box", "price": 39.99, "sku": "GROC-GSB", "variations": ["Sweet", "Savory", "Mixed"], "attributes": {}},
        {"name": "Organic Honey", "price": 9.99, "sku": "GROC-OH", "variations": [], "attributes": {"weight": "12oz"}},
        {"name": "Artisanal Jam", "price": 7.99, "sku": "GROC-AJ", "variations": ["Strawberry", "Blueberry", "Raspberry"], "attributes": {"weight": "8oz"}}
    ],
    "Health & Wellness": [
        {"name": "Multivitamin", "price": 19.99, "sku": "HEALTH-MV", "variations": ["Men's", "Women's"], "attributes": {"count": "90 tablets"}},
        {"name": "Protein Powder", "price": 29.99, "sku": "HEALTH-PP", "variations": ["Chocolate", "Vanilla"], "attributes": {"weight": "2lb"}},
        {"name": "Fitness Tracker", "price": 99.99, "sku": "HEALTH-FT", "variations": ["Black", "Blue"], "attributes": {}},
        {"name": "Yoga Block Set", "price": 19.99, "sku": "HEALTH-YBS", "variations": ["Purple", "Blue"], "attributes": {"count": "2 blocks"}},
        {"name": "Resistance Bands", "price": 24.99, "sku": "HEALTH-RB", "variations": [], "attributes": {"count": "5 bands"}},
        {"name": "Digital Scale", "price": 29.99, "sku": "HEALTH-DS", "variations": ["Black", "White"], "attributes": {}},
        {"name": "Massage Roller", "price": 14.99, "sku": "HEALTH-MR", "variations": [], "attributes": {}},
        {"name": "Essential Oil Set", "price": 39.99, "sku": "HEALTH-EOS", "variations": [], "attributes": {"count": "6 oils"}},
        {"name": "Sleep Aid", "price": 14.99, "sku": "HEALTH-SA", "variations": [], "attributes": {"count": "60 capsules"}},
        {"name": "First Aid Kit", "price": 24.99, "sku": "HEALTH-FAK", "variations": [], "attributes": {}}
    ],
    "Gift Cards": [
        {"name": "Gift Card - $25", "price": 25.00, "sku": "GIFT-25", "variations": [], "attributes": {"value": "$25"}},
        {"name": "Gift Card - $50", "price": 50.00, "sku": "GIFT-50", "variations": [], "attributes": {"value": "$50"}},
        {"name": "Gift Card - $100", "price": 100.00, "sku": "GIFT-100", "variations": [], "attributes": {"value": "$100"}},
        {"name": "E-Gift Card - $25", "price": 25.00, "sku": "EGIFT-25", "variations": [], "attributes": {"value": "$25"}},
        {"name": "E-Gift Card - $50", "price": 50.00, "sku": "EGIFT-50", "variations": [], "attributes": {"value": "$50"}},
        {"name": "E-Gift Card - $100", "price": 100.00, "sku": "EGIFT-100", "variations": [], "attributes": {"value": "$100"}}
    ]
}

# Flatten the product categories into a single list for easier random selection
PRODUCTS = []
for category, products in PRODUCT_CATEGORIES.items():
    for product in products:
        product_with_category = product.copy()
        product_with_category["category"] = category
        if "sizes" not in product_with_category:
            product_with_category["sizes"] = [""]
        PRODUCTS.append(product_with_category)

# Enhanced discount codes
DISCOUNT_CODES = [
    {"code": "WELCOME10", "percent": 0.10, "description": "10% off your order"},
    {"code": "SUMMER20", "percent": 0.20, "description": "20% off your order"},
    {"code": "FLASH30", "percent": 0.30, "description": "30% off your order"},
    {"code": "FREESHIP", "percent": 0.0, "free_shipping": True, "description": "Free shipping on your order"},
    {"code": "SAVE15", "percent": 0.15, "description": "15% off your order"},
    {"code": "HOLIDAY25", "percent": 0.25, "description": "25% off your order"},
    {"code": "NEWCUST", "percent": 0.10, "description": "10% off for new customers"},
    {"code": "LOYALTY5", "percent": 0.05, "description": "5% off for loyal customers"},
    {"code": "BUNDLE20", "percent": 0.20, "description": "20% off when you buy 3+ items"},
    {"code": "CLEARANCE", "percent": 0.40, "description": "40% off clearance items"}
]

# Enhanced shipping methods
SHIPPING_METHODS = [
    {"name": "Economy Shipping", "cost": 7.50, "delivery_days": "5-7 business days"},
    {"name": "Standard Shipping", "cost": 10.00, "delivery_days": "3-5 business days"},
    {"name": "Express Shipping", "cost": 15.00, "delivery_days": "1-2 business days"},
    {"name": "Next Day Air", "cost": 25.00, "delivery_days": "Next business day"},
    {"name": "International Economy", "cost": 20.00, "delivery_days": "7-14 business days"},
    {"name": "International Priority", "cost": 35.00, "delivery_days": "3-5 business days"},
    {"name": "Store Pickup", "cost": 0.00, "delivery_days": "Available today"}
]

# Expanded states with tax rates
STATES = [
    {"name": "Alabama", "code": "AL", "tax_rate": 0.04},
    {"name": "Alaska", "code": "AK", "tax_rate": 0.00},
    {"name": "Arizona", "code": "AZ", "tax_rate": 0.056},
    {"name": "Arkansas", "code": "AR", "tax_rate": 0.065},
    {"name": "California", "code": "CA", "tax_rate": 0.0725},
    {"name": "Colorado", "code": "CO", "tax_rate": 0.029},
    {"name": "Connecticut", "code": "CT", "tax_rate": 0.0635},
    {"name": "Delaware", "code": "DE", "tax_rate": 0.00},
    {"name": "Florida", "code": "FL", "tax_rate": 0.06},
    {"name": "Georgia", "code": "GA", "tax_rate": 0.04},
    {"name": "Hawaii", "code": "HI", "tax_rate": 0.04},
    {"name": "Idaho", "code": "ID", "tax_rate": 0.06},
    {"name": "Illinois", "code": "IL", "tax_rate": 0.0625},
    {"name": "Indiana", "code": "IN", "tax_rate": 0.07},
    {"name": "Iowa", "code": "IA", "tax_rate": 0.06},
    {"name": "Kansas", "code": "KS", "tax_rate": 0.065},
    {"name": "Kentucky", "code": "KY", "tax_rate": 0.06},
    {"name": "Louisiana", "code": "LA", "tax_rate": 0.0445},
    {"name": "Maine", "code": "ME", "tax_rate": 0.055},
    {"name": "Maryland", "code": "MD", "tax_rate": 0.06},
    {"name": "Massachusetts", "code": "MA", "tax_rate": 0.0625},
    {"name": "Michigan", "code": "MI", "tax_rate": 0.06},
    {"name": "Minnesota", "code": "MN", "tax_rate": 0.06875},
    {"name": "Mississippi", "code": "MS", "tax_rate": 0.07},
    {"name": "Missouri", "code": "MO", "tax_rate": 0.04225},
    {"name": "Montana", "code": "MT", "tax_rate": 0.00},
    {"name": "Nebraska", "code": "NE", "tax_rate": 0.055},
    {"name": "Nevada", "code": "NV", "tax_rate": 0.0685},
    {"name": "New Hampshire", "code": "NH", "tax_rate": 0.00},
    {"name": "New Jersey", "code": "NJ", "tax_rate": 0.06625},
    {"name": "New Mexico", "code": "NM", "tax_rate": 0.05125},
    {"name": "New York", "code": "NY", "tax_rate": 0.04},
    {"name": "North Carolina", "code": "NC", "tax_rate": 0.0475},
    {"name": "North Dakota", "code": "ND", "tax_rate": 0.05},
    {"name": "Ohio", "code": "OH", "tax_rate": 0.0575},
    {"name": "Oklahoma", "code": "OK", "tax_rate": 0.045},
    {"name": "Oregon", "code": "OR", "tax_rate": 0.00},
    {"name": "Pennsylvania", "code": "PA", "tax_rate": 0.06},
    {"name": "Rhode Island", "code": "RI", "tax_rate": 0.07},
    {"name": "South Carolina", "code": "SC", "tax_rate": 0.06},
    {"name": "South Dakota", "code": "SD", "tax_rate": 0.045},
    {"name": "Tennessee", "code": "TN", "tax_rate": 0.07},
    {"name": "Texas", "code": "TX", "tax_rate": 0.0625},
    {"name": "Utah", "code": "UT", "tax_rate": 0.0485},
    {"name": "Vermont", "code": "VT", "tax_rate": 0.06},
    {"name": "Virginia", "code": "VA", "tax_rate": 0.053},
    {"name": "Washington", "code": "WA", "tax_rate": 0.065},
    {"name": "West Virginia", "code": "WV", "tax_rate": 0.06},
    {"name": "Wisconsin", "code": "WI", "tax_rate": 0.05},
    {"name": "Wyoming", "code": "WY", "tax_rate": 0.04}
]

# Expanded cities for each state
CITIES = {
    "AL": ["Birmingham", "Montgomery", "Mobile", "Huntsville", "Tuscaloosa"],
    "AK": ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan"],
    "AZ": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale"],
    "AR": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro"],
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood"],
    "CT": ["Bridgeport", "New Haven", "Hartford", "Stamford", "Waterbury"],
    "DE": ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"],
    "GA": ["Atlanta", "Savannah", "Augusta", "Columbus", "Macon"],
    "HI": ["Honolulu", "Hilo", "Kailua", "Kapolei", "Kaneohe"],
    "ID": ["Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello"],
    "IL": ["Chicago", "Springfield", "Peoria", "Rockford", "Champaign"],
    "IN": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel"],
    "IA": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City"],
    "KS": ["Wichita", "Overland Park", "Kansas City", "Topeka", "Olathe"],
    "KY": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington"],
    "LA": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles"],
    "ME": ["Portland", "Lewiston", "Bangor", "South Portland", "Auburn"],
    "MD": ["Baltimore", "Frederick", "Rockville", "Gaithersburg", "Bowie"],
    "MA": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell"],
    "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor"],
    "MN": ["Minneapolis", "Saint Paul", "Rochester", "Duluth", "Bloomington"],
    "MS": ["Jackson", "Gulfport", "Southaven", "Hattiesburg", "Biloxi"],
    "MO": ["Kansas City", "St. Louis", "Springfield", "Columbia", "Independence"],
    "MT": ["Billings", "Missoula", "Great Falls", "Bozeman", "Butte"],
    "NE": ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney"],
    "NV": ["Las Vegas", "Henderson", "Reno", "North Las Vegas", "Sparks"],
    "NH": ["Manchester", "Nashua", "Concord", "Derry", "Dover"],
    "NJ": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton"],
    "NM": ["Albuquerque", "Las Cruces", "Rio Rancho", "Santa Fe", "Roswell"],
    "NY": ["New York", "Buffalo", "Rochester", "Syracuse", "Albany"],
    "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"],
    "ND": ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "OK": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond"],
    "OR": ["Portland", "Salem", "Eugene", "Gresham", "Hillsboro"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
    "RI": ["Providence", "Warwick", "Cranston", "Pawtucket", "East Providence"],
    "SC": ["Columbia", "Charleston", "North Charleston", "Mount Pleasant", "Rock Hill"],
    "SD": ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown"],
    "TN": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville"],
    "TX": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth"],
    "UT": ["Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem"],
    "VT": ["Burlington", "South Burlington", "Rutland", "Essex Junction", "Bennington"],
    "VA": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News"],
    "WA": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue"],
    "WV": ["Charleston", "Huntington", "Morgantown", "Parkersburg", "Wheeling"],
    "WI": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine"],
    "WY": ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs"]
}

# Enhanced name generation
def generate_random_name():
    """Generate a random name for testing."""
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
        "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy",
        "Christopher", "Lisa", "Daniel", "Margaret", "Matthew", "Betty", "Anthony", "Sandra", "Mark", "Ashley",
        "Donald", "Dorothy", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
        "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah", "Timothy", "Stephanie",
        "Ronald", "Rebecca", "Edward", "Laura", "Jason", "Sharon", "Jeffrey", "Cynthia", "Ryan", "Kathleen",
        "Jacob", "Amy", "Gary", "Shirley", "Nicholas", "Angela", "Eric", "Helen", "Jonathan", "Anna",
        "Stephen", "Brenda", "Larry", "Pamela", "Justin", "Nicole", "Scott", "Samantha", "Brandon", "Katherine",
        "Benjamin", "Emma", "Samuel", "Ruth", "Gregory", "Christine", "Alexander", "Catherine", "Patrick", "Debra",
        "Frank", "Rachel", "Raymond", "Carolyn", "Jack", "Janet", "Dennis", "Virginia", "Jerry", "Maria",
        "Tyler", "Heather", "Aaron", "Diane", "Jose", "Julie", "Adam", "Joyce", "Nathan", "Victoria",
        "Henry", "Kelly", "Zachary", "Christina", "Douglas", "Lauren", "Peter", "Joan", "Kyle", "Evelyn"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
        "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
        "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
        "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
        "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
        "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez",
        "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross",
        "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington",
        "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", "Russell", "Griffin", "Diaz", "Hayes"
    ]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name):
    """Generate a random email based on name."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com", "protonmail.com", 
               "mail.com", "zoho.com", "yandex.com", "gmx.com", "live.com", "fastmail.com", "example.com"]
    
    name_parts = name.lower().split()
    
    # Different email patterns
    patterns = [
        lambda f, l: f"{f}{l[0]}",                  # johnj
        lambda f, l: f"{f[0]}{l}",                  # jsmith
        lambda f, l: f"{f}.{l}",                    # john.smith
        lambda f, l: f"{f}{random.randint(1, 999)}", # john123
        lambda f, l: f"{l}.{f}",                    # smith.john
        lambda f, l: f"{f}_{l}",                    # john_smith
        lambda f, l: f"{l}{f[0]}",                  # smithj
        lambda f, l: f"{f}{l}",                     # johnsmith
    ]
    
    username = random.choice(patterns)(name_parts[0], name_parts[1])
    
    # Sometimes add a number
    if random.random() < 0.3:
        username += str(random.randint(1, 999))
    
    return f"{username}@{random.choice(domains)}"

def generate_random_address():
    """Generate a random address for testing."""
    street_numbers = [str(random.randint(100, 9999)) for _ in range(20)]
    
    street_names = [
        "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Washington Ave", "Park Dr", 
        "Lake Rd", "River St", "Sunset Blvd", "Highland Ave", "Forest Dr", "Meadow Ln", "Valley Rd", 
        "Mountain View Dr", "Spring St", "Willow Ave", "Chestnut St", "Magnolia Dr", "Dogwood Ln", 
        "Birch St", "Cherry Ln", "Spruce Ave", "Sycamore Dr", "Poplar St", "Aspen Ct", "Cypress Dr",
        "Juniper Ln", "Redwood Dr", "Sequoia Ct", "Hemlock Ln", "Beech St", "Walnut Ave", "Laurel Dr",
        "Hickory Ln", "Mulberry St", "Locust Ave", "Hawthorn Dr", "Acacia Ln", "Eucalyptus Dr"
    ]
    
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
    area_code = random.randint(200, 999)  # Area codes don't start with 0 or 1
    prefix = random.randint(200, 999)     # Prefixes don't start with 0 or 1
    line = random.randint(1000, 9999)
    
    # Different phone formats
    formats = [
        lambda a, p, l: f"+1 {a}-{p}-{l}",
        lambda a, p, l: f"({a}) {p}-{l}",
        lambda a, p, l: f"{a}.{p}.{l}",
        lambda a, p, l: f"{a}-{p}-{l}",
        lambda a, p, l: f"+1{a}{p}{l}"
    ]
    
    return random.choice(formats)(area_code, prefix, line)

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
    
    # Process orders in batches to handle large volumes
    batch_size = min(request.batch_size, request.num_orders)
    num_batches = (request.num_orders + batch_size - 1) // batch_size  # Ceiling division
    
    # Create CSV file and write header
    with open(output_path, 'w', newline='') as csvfile:
        # Define fields for the CSV
        order_fields = [
            "id", "name", "email", "financial_status", "paid_at", "fulfillment_status", "fulfilled_at",
            "accepts_marketing", "currency", "subtotal", "shipping", "taxes", "total", "discount_code",
            "discount_amount", "shipping_method", "created_at", "cancelled_at", "payment_method",
            "payment_reference", "refunded_amount", "vendor", "outstanding_balance", "employee", "location",
            "device_id", "billing_name", "billing_street", "billing_address1", "billing_address2",
            "billing_company", "billing_city", "billing_zip", "billing_province", "billing_country",
            "billing_phone", "billing_province_name", "shipping_name", "shipping_street", "shipping_address1",
            "shipping_address2", "shipping_company", "shipping_city", "shipping_zip", "shipping_province",
            "shipping_country", "shipping_phone", "shipping_province_name"
        ]
        
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
        
        # Process each batch
        total_line_items = 0
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, request.num_orders)
            batch_orders = []
            
            # Generate orders for this batch
            for i in range(start_idx, end_idx):
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
                    
                    # Handle product variations
                    variation = ""
                    if "variations" in product and product["variations"]:
                        variation = random.choice(product["variations"])
                    
                    # Handle product sizes
                    size = ""
                    if product["sizes"] and product["sizes"][0]:  # Check if sizes exist and aren't empty
                        size = random.choice(product["sizes"])
                    
                    # Determine if it's a gift card (no shipping, no tax)
                    is_gift_card = "Gift Cards" in product["category"]
                    
                    # Create item name with variation and size if applicable
                    item_name = product["name"]
                    if variation:
                        item_name += f" - {variation}"
                    if size:
                        item_name += f" / {size}"
                    
                    # Create SKU with variation and size codes
                    item_sku = product["sku"]
                    if variation:
                        # Add first two letters of variation to SKU
                        variation_code = variation[:2].upper()
                        item_sku += f"-{variation_code}"
                    if size:
                        # For clothing sizes, add size code
                        item_sku += f"-{size}"
                    
                    line_item = {
                        "name": item_name,
                        "price": product["price"],
                        "sku": item_sku,
                        "requires_shipping": "false" if is_gift_card else "true",
                        "taxable": "false" if is_gift_card else "true",
                        "quantity": random.randint(1, 3)
                    }
                    line_items.append(line_item)
                
                # Calculate order totals
                subtotal = sum(item["price"] * item["quantity"] for item in line_items)
                
                # Apply discount if applicable
                discount_amount = 0
                shipping_cost = 0
                
                if discount:
                    if hasattr(discount, "free_shipping") and discount.get("free_shipping", False):
                        shipping_cost = 0
                    else:
                        discount_amount = subtotal * discount["percent"]
                
                # Add shipping cost if applicable
                if shipping_method and not (discount and hasattr(discount, "free_shipping") and discount.get("free_shipping", False)):
                    shipping_cost = shipping_method["cost"]
                
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
                    "payment_method": "Credit Card",
                    "payment_reference": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
                    "refunded_amount": "0.00",
                    "vendor": product.get("category", "General Store"),
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
                
                batch_orders.append(order)
                total_line_items += len(line_items)
            
            # Write batch orders to CSV
            for order in batch_orders:
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
        "num_line_items": total_line_items,
        "date_range": f"{request.start_date.date()} to {request.end_date.date()}"
    }

@router.post("/generate", summary="Generate test order data in Shopify format")
async def generate_test_order_data(
    request: TestDataRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate test order data in Shopify format.
    
    This endpoint creates a CSV file with randomly generated order data
    that matches the Shopify export format. The data can be used for
    testing the analytics and forecasting functionality.
    
    For large data sets (>50,000 orders), the generation will be processed
    in the background to avoid timeout issues.
    
    Parameters:
    - num_orders: Number of orders to generate (up to 1,000,000)
    - start_date: Start date for the orders
    - end_date: End date for the orders
    - min_items_per_order: Minimum number of line items per order
    - max_items_per_order: Maximum number of line items per order
    - include_discounts: Whether to include discounts
    - include_shipping: Whether to include shipping
    - include_taxes: Whether to include taxes
    - output_file: Name of the output file
    - batch_size: Batch size for processing large order volumes
    
    Returns:
    - Information about the generated file
    """
    try:
        # For large datasets, process in background
        if request.num_orders > 50000:
            # Start background task
            background_tasks.add_task(generate_test_data, request)
            return {
                "status": "processing",
                "message": f"Generation of {request.num_orders} orders started in the background. The file will be available at /app/uploads/{request.output_file} when complete.",
                "estimated_completion_time": f"Approximately {request.num_orders // 10000} minutes"
            }
        else:
            # For smaller datasets, process immediately
            result = generate_test_data(request)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating test data: {str(e)}")
