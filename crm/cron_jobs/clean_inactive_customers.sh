#!/bin/bash

# Navigate to the project directory
cd /home/joemane/ALX/alx-backend-graphql_crm

# Execute Django management command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from datetime import datetime, timedelta
from django.utils import timezone

# Find customers with no orders in the last year
one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(
    orders__order_date__gte=one_year_ago
)

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
