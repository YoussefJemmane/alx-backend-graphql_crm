import datetime
import requests
from django.conf import settings
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Log a heartbeat message to verify CRM is alive"""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    # Append to log file
    with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
        log_file.write(message)
    
    # Optional: Query GraphQL hello field to verify endpoint
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql',
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute hello query
        query = gql('{ hello }')
        result = client.execute(query)
        hello_message = result.get('hello', 'No response')
        
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} GraphQL hello: {hello_message}\n")
            
    except Exception as e:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} GraphQL query failed: {str(e)}\n")

def update_low_stock():
    """Update products with low stock using GraphQL mutation"""
    import json
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Execute GraphQL mutation
        mutation = """
        mutation {
            updateLowStockProducts {
                products {
                    id
                    name
                    stock
                }
                message
            }
        }
        """
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            mutation_data = data.get('data', {}).get('updateLowStockProducts', {})
            products = mutation_data.get('products', [])
            
            # Log updated products
            with open('/tmp/lowstockupdates_log.txt', 'a') as log_file:
                if products:
                    log_file.write(f"{timestamp} - Updated low stock products:\n")
                    for product in products:
                        log_file.write(f"  {product['name']}: new stock = {product['stock']}\n")
                else:
                    log_file.write(f"{timestamp} - No low stock products to update\n")
        else:
            with open('/tmp/lowstockupdates_log.txt', 'a') as log_file:
                log_file.write(f"{timestamp} - GraphQL mutation failed: HTTP {response.status_code}\n")
                
    except Exception as e:
        with open('/tmp/lowstockupdates_log.txt', 'a') as log_file:
            log_file.write(f"{timestamp} - Error updating low stock: {str(e)}\n")
