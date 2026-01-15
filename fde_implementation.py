"""
CASE STUDY 1: THE DATA AGGREGATOR
Context: A client provides a messy stream of transaction data from two different sources. 
Your goal is to normalize this data so it can be used by the frontend dashboard.

TASK:
1. Fetch data from two mocked internal sources (provided below).
2. Merge the data on 'user_id'.
3. Filter out any transactions marked as 'failed'.
4. Calculate the total 'lifetime_value' (LTV) for each user.
5. Return a JSON-ready list of users who have an LTV > 500, 
   sorted by LTV in descending order.

Constraint: 
- Do not use external libraries like Pandas (stay in standard library/JSON).
- Handle cases where a user might exist in one source but not the other.
"""

# --- MOCK DATA SOURCES (Do not modify the data itself) ---
source_a = [
    {"user_id": 1, "name": "Alice", "status": "active"},
    {"user_id": 2, "name": "Bob", "status": "active"},
    {"user_id": 3, "name": "Charlie", "status": "inactive"},
]

source_b = [
    {"user_id": 1, "amount": 250, "state": "success"},
    {"user_id": 1, "amount": 300, "state": "success"},
    {"user_id": 2, "amount": 100, "state": "success"},
    {"user_id": 2, "amount": 50, "state": "failed"},
    {"user_id": 3, "amount": 600, "state": "success"},
]

def process_client_data(users, transactions):
    # add if user["status"] == "active" to filter additionally??
    processed_dict = {user["user_id"]: {"user_id": user["user_id"], "name": user["name"], "ltv": 0} for user in users}

    # for transaction in transactions:
    #     user_id = transaction["user_id"]
    #     if transaction["state"] == "success" and transaction["user_id"] in processed_dict:
    #         if user_id in users:
    #             processed_dict[user_id]["ltv"] += transaction["amount"]
    #         else:
    #             processed_dict[transaction["user_id"]] = {
    #             "user_id": transaction["user_id"],
    #             "name": "Unknown",  # or some default name
    #             "ltv": transaction["amount"] if transaction["state"] == "success" else 0
    #             }

    for transaction in transactions:
        if transaction["state"] == "success" and transaction["user_id"] in processed_dict:
                processed_dict[transaction["user_id"]]["ltv"] += int(transaction["amount"])

    # print(processed_dict)
    return flatten(processed_dict, filter = lambda value: value > 500)

def flatten(dictionary, filter = None):
    # return [value for inner_dict in dictionary.values() for value in inner_dict.values()]
    flattened = [value for value in dictionary.values() if filter(value["ltv"])]
    return sorted(flattened, key = lambda x: x["ltv"], reverse=True)

# GEMINI SUGGESTED "PRO" VERSION

""" 
1. What you did well:
- Hash Map Strategy: Initializing processed_dict with user_id as the key is the professional way to handle data merges.
- Separation of Concerns: Using a helper function (even a simple one like flatten) shows you think about modularity.
- Filtering Logic: Correct use of reverse=True in sorting and specific state filtering ("success").

2. Fixing Areas of Improvement (The "Now")
The pro version fixes specific vulnerabilities in your original solution to ensure it is production-ready:
- Key Errors: Uses .get() instead of bracket notation []. If a client's JSON is missing a field, dict["key"] crashes the program; dict.get("key") allows you to handle it gracefully.
- Data Integrity: It adds type casting (e.g., float()). Clients often send numbers as strings ("500"), which will cause a TypeError if you try to add them to an integer 0 without casting.
- Efficiency: It streamlines the final step. Instead of calling a separate flatten function and then sorted, it uses a list comprehension to filter and sort in a single, readable flow.

___________________________________________________________________________

Follow up: Great. Now, the client has 1 million transactions and 500k users. 
Also, some amounts are in different currencies. How do you adjust?

2. Preparing for "Step 2" (The "Later")
The pro version sets up the architecture to handle common follow-up requirements: The "Ghost User" Problem
- In "Step 2," an interviewer might say: "We found out Source B has transactions for users not yet registered in Source A. We still need to track their LTV.
- Your Original: Only processes users who exist in source_a.
- The Pro Version: Uses user_map.get(uid, {"name": "Unknown User"}). This ensures you don't lose financial data just because the metadata is missing.

Scalability (The "Big Data" Problem): If the dataset grows to millions of rows: 
- The Pro Version is optimized for $O(N + M)$ time complexity.
- By iterating through users once and transactions once—and using a Hash Map for lookups—it avoids the "Nested Loop" trap ($O(N \times M)$) that causes scripts to time out on large client datasets.

"""

def process_client_data2(users, transactions):
    # 1. Index users for O(1) access
    user_map = {u["user_id"]: u for u in users}
    
    # 2. Track LTVs using a temporary dict
    # This handles transactions for users NOT in the user_map too
    stats = {} 

    for t in transactions:
        uid = t.get("user_id")
        # Robustness check: skip if data is truly malformed
        if not uid or t.get("state") != "success":
            continue
            
        if uid not in stats:
            # Handle "Unknown" users (The FDE "Missing Data" edge case)
            user_info = user_map.get(uid, {"name": "Unknown User"})
            stats[uid] = {"user_id": uid, "name": user_info["name"], "ltv": 0}
            
        # Type casting: ensure amount is a number
        stats[uid]["ltv"] += float(t.get("amount", 0))

    # 3. Filter and Sort in one clean list comprehension
    result = [v for v in stats.values() if v["ltv"] > 500]
    return sorted(result, key=lambda x: x["ltv"], reverse=True)


def __main__():
    result = process_client_data2(source_a, source_b)
    print(result)

if __name__ == "__main__":
    __main__()

# Expected Result Format: 
# [{"user_id": 3, "name": "Charlie", "ltv": 600}, {"user_id": 1, "name": "Alice", "ltv": 550}]