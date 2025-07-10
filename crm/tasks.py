from celery import shared_task
import requests
import datetime
from decimal import Decimal

@shared_task
def generate_crm_report():
    """Generate a weekly CRM report using GraphQL queries"""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # GraphQL query to get CRM statistics
        query = """
        query {
            allCustomers {
                edges {
                    node {
                        id
                    }
                }
            }
            allOrders {
                edges {
                    node {
                        id
                        totalAmount
                    }
                }
            }
        }
        """
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract data
            customers = data.get('data', {}).get('allCustomers', {}).get('edges', [])
            orders = data.get('data', {}).get('allOrders', {}).get('edges', [])
            
            # Calculate statistics
            total_customers = len(customers)
            total_orders = len(orders)
            total_revenue = sum(
                Decimal(str(order['node']['totalAmount'])) 
                for order in orders
            )
            
            # Format the report
            report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"
            
            # Log to file
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(report + '\n')
                
            return f"CRM report generated successfully: {report}"
            
        else:
            error_msg = f"{timestamp} - GraphQL query failed: HTTP {response.status_code}"
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(error_msg + '\n')
            return error_msg
            
    except Exception as e:
        error_msg = f"{timestamp} - Error generating CRM report: {str(e)}"
        with open('/tmp/crm_report_log.txt', 'a') as log_file:
            log_file.write(error_msg + '\n')
        return error_msg
