import requests
import re

def fetch_and_parse_steam_search(cookie_string):
    url = "https://store.steampowered.com/search/"
    headers = {
        'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Upgrade-Insecure-Requests': '1',
    }
    params = {
        'snr': '1_4_4__12',
        'term': 'FPS'
    }
    cookies = {item.split('=')[0]: item.split('=')[1] for item in cookie_string.split('; ')}

    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    
    from openai import OpenAI
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You need to parse the html content and return a list of games that are in the html content. You need to return the name, description, url, and price of the game. You need to return the first 5 games that are in the html content."},
            {"role": "user", "content": response.text[:100000]}  # Ensure prompt is a string
        ],
    )
    parsed_games = completion.choices[0].message.content
    return parsed_games

# Example cookie usage
cookie_string = "cookie_name1=cookie_value1; cookie_name2=cookie_value2"
result = fetch_and_parse_steam_search(cookie_string)
print(result)