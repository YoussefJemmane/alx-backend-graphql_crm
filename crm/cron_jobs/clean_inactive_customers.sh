#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Navigate to the project directory
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    echo "Changed to project directory: $(pwd)"
    echo "Current working directory (cwd): $(pwd)"
else
    echo "Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "manage.py not found in current directory: $(pwd)"
    exit 1
fi

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
