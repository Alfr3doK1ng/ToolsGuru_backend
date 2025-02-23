import requests
import re

def fetch_and_parse_steam_search(cookie_string):
    # Define the URL
    url = 'https://store.steampowered.com/search/?snr=1_4_4__12&term=chess'

    # Set up the headers
    headers = {
        'Connection': 'keep-alive',
        'Host': 'store.steampowered.com',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': cookie_string
    }

    # Send a GET request
    response = requests.get(url, headers=headers)

    # Ensure the request was successful
    if response.status_code != 200:
        raise Exception(f"Request failed with status code: {response.status_code}")

    # Get the content of the response
    html_content = response.text

    # Define the dictionary to store parsed values
    parsed_values = {}

    # Use openai chat completions with gpt4o to parse content
    from openai import OpenAI
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You need to parse the html content and return a list of games that are in the html content. You need to return the name, url, and price of the game. You need to return the first 5 games that are in the html content."},
            {"role": "user", "content": html_content[:100000]}  # Ensure prompt is a string
        ],
    )
    parsed_values = completion.choices[0].message.content

    return parsed_values

# Starting point
if __name__ == "__main__":
    # Hard coded cookies in string format
    cookie_string = "key1=value1;key2=value2"
    # Convert cookie string to dictionary for easier access
    cookies_dict = {c.split('=')[0]: c.split('=')[1] for c in cookie_string.split(';')}
    
    # Call the function with the constructed cookie string
    result = fetch_and_parse_steam_search(cookie_string)
    
    # Print the result
    print(result)