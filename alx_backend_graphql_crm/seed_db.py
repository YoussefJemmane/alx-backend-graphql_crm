# seed_db.py

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    print("Seeding database...")
    
    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    
    # Create customers
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Davis", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Wilson", "email": "david@example.com", "phone": "987-654-3210"},
        {"name": "Eve Brown", "email": "eve@example.com", "phone": "+1122334455"},
    ]
    
    customers = []
    for customer_data in customers_data:
        customer = Customer.objects.create(**customer_data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")
    
    # Create products
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Mouse", "price": Decimal("29.99"), "stock": 50},
        {"name": "Keyboard", "price": Decimal("79.99"), "stock": 25},
        {"name": "Monitor", "price": Decimal("299.99"), "stock": 15},
        {"name": "Webcam", "price": Decimal("89.99"), "stock": 8},
        {"name": "Headphones", "price": Decimal("149.99"), "stock": 20},
    ]
    
    products = []
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        products.append(product)
        print(f"Created product: {product.name}")
    
    # Create orders
    orders_data = [
        {"customer": customers[0], "product_ids": [products[0].id, products[1].id]},  # Alice: Laptop + Mouse
        {"customer": customers[1], "product_ids": [products[2].id, products[3].id]},  # Bob: Keyboard + Monitor
        {"customer": customers[2], "product_ids": [products[4].id]},  # Carol: Webcam
        {"customer": customers[3], "product_ids": [products[5].id, products[1].id]},  # David: Headphones + Mouse
        {"customer": customers[4], "product_ids": [products[0].id, products[2].id, products[4].id]},  # Eve: Laptop + Keyboard + Webcam
    ]
    
    for order_data in orders_data:
        customer = order_data["customer"]
        product_ids = order_data["product_ids"]
        order_products = Product.objects.filter(id__in=product_ids)
        
        # Calculate total amount
        total_amount = sum(product.price for product in order_products)
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount
        )
        
        # Associate products
        order.products.set(order_products)
        
        product_names = ", ".join([p.name for p in order_products])
        print(f"Created order for {customer.name}: {product_names} (Total: ${total_amount})")
    
    print("\nDatabase seeded successfully!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")

if __name__ == "__main__":
    seed_database()