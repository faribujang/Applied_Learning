# from fastapi import FastAPI
import sys
import requests, json
from datetime import datetime, timedelta
from collections import defaultdict


def asteroids(date, span):

    endpoint = "https://api.nasa.gov/neo/rest/v1/feed"
    # api_key = "DEMO_KEY"
    api_key = "VQJQbUDubiFLLbuUyXGdePWaySqODtOSYlziTJmA"
    params = {
        "start_date": date,
        "end_date": (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=span)).strftime("%Y-%m-%d"),
        "api_key": api_key
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        print("success")
    else:
        print(f'Error: {response.status_code}')

    data = response.json()

    asts = []
    # for asteroid in data:
    # Cache file path
    cache_file = f"asteroid_cache_{date}_{span}.json"
    
    # Try to load from cache first
    try:
        with open(cache_file, 'r') as f:
            print(f"Loading data from cache: {cache_file}")
            return json.load(f)
    except FileNotFoundError:
        print(f"No cache found, fetching from API...")
    
    #     name, min_d, max_d, hazardous = asteroid["name"], asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_min"], asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"], asteroid["is_potentially_hazardous_asteroid"]
    #     ast = {
    #         "name": name,
    #         "min_diameter_km": min_d,
    #         "max_diameter_km": max_d,
    #         "is_hazardous": hazardous
    #     }
    #     asts.append(ast)

    # asts = sorted(asts, lambda x: x["max_diameter_km"], reverse=True)


    # NASA API structure: {"near_earth_objects": {"2015-09-07": [...], "2015-09-08": [...]}}
    near_earth_objects = data.get("near_earth_objects", {})
    
    # Iterate through each date's asteroid list
    for date_key, asteroids_on_date in near_earth_objects.items():
        for asteroid in asteroids_on_date:
            name = asteroid["name"]
            min_d = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_min"] * 1000
            max_d = asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"] * 1000
            hazardous = asteroid["is_potentially_hazardous_asteroid"]
            
            ast = {
                "date": date_key,
                "name": name,
                "min_diameter_m": min_d,
                "max_diameter_m": max_d,
                "is_hazardous": hazardous
            }
            asts.append(ast)

    asts = sorted(asts, key=lambda x: x["max_diameter_m"], reverse=True)
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump(asts, f, indent=2)
    print(f"Data cached to: {cache_file}")

    return asts

def main(args):
    date, span = args[0], int(args[1])

    ast_data = asteroids(date, span=span)

    # Group asteroids by date
    from collections import defaultdict
    asteroids_by_date = defaultdict(list)
    
    for asteroid in ast_data:
        asteroids_by_date[asteroid.get("date", "Unknown")].append(asteroid)
    
    # Print grouped by date
    for date_key in sorted(asteroids_by_date.keys()):
        print(f"Date: {date_key} \n")
        
        for asteroid in asteroids_by_date[date_key]:
            hazard_status = "Hazardous" if asteroid["is_hazardous"] else "Not Hazardous"
            print(f"Name: {asteroid['name']:<30} | Min: {asteroid['min_diameter_m']:>8.4f} m | "
                  f"Max: {asteroid['max_diameter_m']:>8.4f} m | {hazard_status}")
        print()

if __name__ == "__main__":

    args = sys.argv[1], sys.argv[2]

    main(args)