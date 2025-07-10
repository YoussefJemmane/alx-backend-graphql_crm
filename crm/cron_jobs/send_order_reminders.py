import datetime
import requests

def get_pending_orders():
    """Get orders from the last 7 days using GraphQL"""
    query = '''
    query {
        allOrders {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                    orderDate
                }
            }
        }
    }
    '''
    
    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('allOrders', {}).get('edges', [])
            
            # Filter orders from last 7 days
            week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            recent_orders = []
            
            for order in orders:
                order_date_str = order['node']['orderDate']
                order_date = datetime.datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
                
                if order_date >= week_ago:
                    recent_orders.append(order)
            
            return recent_orders
        else:
            print(f"GraphQL query failed: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error querying GraphQL: {str(e)}")
        return []

# Main execution
if __name__ == "__main__":
    log_file = '/tmp/order_reminders_log.txt'
    
    orders = get_pending_orders()
    
    # Log orders
    with open(log_file, 'a') as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if orders:
            for order in orders:
                order_id = order['node']['id']
                customer_email = order['node']['customer']['email']
                file.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n")
        else:
            file.write(f"{timestamp} - No pending orders found\n")
    
    print("Order reminders processed!")

