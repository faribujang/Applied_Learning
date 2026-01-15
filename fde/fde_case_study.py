"""
CASE STUDY 2: THE "HEAVY" DASHBOARD
Context: An FDE Colleague wrote a script to sync client product inventories. 
The client complains that the script is "timing out" when they hit 10,000 products 
and sometimes duplicates data.

TASK:
1. Identify 3 architectural or logic flaws in the code below.
2. Propose (or rewrite) a version that is more efficient (O(n) instead of O(n^2)).
3. Add a basic "check" to ensure we don't process the same product ID twice.
"""

def sync_inventory(client_products, master_catalog):
    """
    client_products: List of dicts e.g. [{"id": "p1", "price": 20}]
    master_catalog: List of dicts e.g. [{"id": "p1", "name": "Widget"}]
    """
    synced_data = []

    # Current Logic (The "Problematic" Code):
    for product in client_products:
        for item in master_catalog:
            if product['id'] == item['id']:
                # Heavy transformation logic simulated here
                combined = {
                    "id": product['id'],
                    "name": item['name'],
                    "price": product['price']
                }
                synced_data.append(combined)
    
    return synced_data

# CHALLENGE: 
# How would you handle this if 'master_catalog' was an API endpoint 
# that only allowed 100 items per request? (Briefly describe in comments)