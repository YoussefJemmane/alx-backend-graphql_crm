# crm/schema.py

import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at', 'updated_at')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'created_at', 'updated_at')

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'total_amount', 'order_date', 'created_at', 'updated_at')

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Custom Error Type
class ErrorType(graphene.ObjectType):
    field = graphene.String()
    message = graphene.String()

# Mutation Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(ErrorType)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CreateCustomerResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append(ErrorType(field="email", message="Email already exists"))
        
        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^(\+\d{1,3}[- ]?)?\d{10}$|^\d{3}-\d{3}-\d{4}$'
            if not re.match(phone_pattern, input.phone):
                errors.append(ErrorType(
                    field="phone", 
                    message="Phone number must be in format +1234567890 or 123-456-7890"
                ))
        
        if errors:
            return CreateCustomerResponse(errors=errors)
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            return CreateCustomerResponse(
                customer=customer,
                message="Customer created successfully"
            )
        except Exception as e:
            return CreateCustomerResponse(
                errors=[ErrorType(field="general", message=str(e))]
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Check email uniqueness
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format if provided
                    if customer_data.phone:
                        phone_pattern = r'^(\+\d{1,3}[- ]?)?\d{10}$|^\d{3}-\d{3}-\d{4}$'
                        if not re.match(phone_pattern, customer_data.phone):
                            errors.append(f"Customer {i+1}: Invalid phone format")
                            continue
                    
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    created_customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCreateCustomersResponse(
            customers=created_customers,
            errors=errors
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = CreateProductResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate price is positive
        if input.price <= 0:
            errors.append(ErrorType(field="price", message="Price must be positive"))
        
        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append(ErrorType(field="stock", message="Stock cannot be negative"))
        
        if errors:
            return CreateProductResponse(errors=errors)
        
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return CreateProductResponse(
                product=product,
                message="Product created successfully"
            )
        except Exception as e:
            return CreateProductResponse(
                errors=[ErrorType(field="general", message=str(e))]
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = CreateOrderResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(ErrorType(field="customer_id", message="Invalid customer ID"))
            return CreateOrderResponse(errors=errors)
        
        # Validate products exist and at least one is provided
        if not input.product_ids:
            errors.append(ErrorType(field="product_ids", message="At least one product is required"))
            return CreateOrderResponse(errors=errors)
        
        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            errors.append(ErrorType(field="product_ids", message="One or more invalid product IDs"))
            return CreateOrderResponse(errors=errors)
        
        try:
            # Calculate total amount
            total_amount = sum(product.price for product in products)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount,
                order_date=input.order_date
            )
            
            # Associate products
            order.products.set(products)
            
            return CreateOrderResponse(
                order=order,
                message="Order created successfully"
            )
        except Exception as e:
            return CreateOrderResponse(
                errors=[ErrorType(field="general", message=str(e))]
            )

# Query class
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    # Basic queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None

# Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()