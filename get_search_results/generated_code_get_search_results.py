import requests
import json
import openai
import argparse


def make_uber_eats_post_request(request_params, cookies_dict, dish_type):
    headers = {
        'content-type': 'application/json',
        'origin': 'https://www.ubereats.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-csrf-token': request_params['var__8300255037882393421'],
        'x-uber-client-name': 'eats-web',
        'referer': 'https://www.ubereats.com/',
    }
    
    cookies = cookies_dict
    
    data = {
        "userQuery": dish_type,
        "date": "",
        "startTime": 0,
        "endTime": 0,
        "sortAndFilters": [],
        "vertical": "ALL",
        "searchSource": "SEARCH_SUGGESTION",
        "displayType": "SEARCH_RESULTS",
        "searchType": "GLOBAL_SEARCH",
        "keyName": "",
        "cacheKey": "",
        "recaptchaToken": ""
    }
    
    response = requests.post(
        'https://www.ubereats.com/_p/api/getSearchFeedV1',
        headers=headers,
        cookies=cookies,
        json=data
    )
    
    if response.status_code == 200:
        response_data = response.json()

        return response_data
    else:
        return {"error": f"Request failed with status code {response.status_code}"}

def parse_restaurants_with_openai(response_data):
    prompt = f"""Please analyze these restaurants and format them nicely:
{json.dumps(response_data, indent=2)}
For each restaurant, provide:
1. Restaurant name
2. URL
3. One featured dish"""

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing with OpenAI: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for restaurants by dish type.")
    parser.add_argument("dish_type", type=str, help="Type of dish to search for")
    
    args = parser.parse_args()
    dish_type = args.dish_type
    cookies_string = "jwt-session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    cookies_dict = dict(item.split("=") for item in cookies_string.split("; "))

    var__8300255037882393421 = cookies_dict['jwt-session']

    request_params = {"var__8300255037882393421": var__8300255037882393421}
    result = make_uber_eats_post_request(request_params, cookies_dict, dish_type)

    # Extract the top 10 restaurants
    restaurants = []
    feed_items = result.get('data', {}).get('feedItems', [])

    for item in feed_items:
        store = item.get('store', {})
        if store:
            # Extracting the store name
            store_name = store.get('title', {}).get('text', 'Unknown')
            
            # Extracting one dish (assuming the first image represents a dish)
            dish_image_url = store.get('image', {}).get('items', [{}])[0].get('url', 'No image available')
            
            # Constructing the full URL
            base_url = "https://www.ubereats.com"
            store_url = base_url + store.get('actionUrl', 'N/A')
            
            restaurant_info = {
                'name': store_name,
                'dish_image_url': dish_image_url,
                'url': store_url
            }
            restaurants.append(restaurant_info)
        
        if len(restaurants) >= 10:
            break

    # Print the top 10 restaurants
    for i, restaurant in enumerate(restaurants, start=1):
        print(f"{i}. Name: {restaurant['name']}, Dish Image URL: {restaurant['dish_image_url']}, Full URL: {restaurant['url']}")