def get_steam_sale_data(cookie_string):
    import requests
    import json

    url = 'https://store.steampowered.com/dynamicstore/saledata/?cc=US'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie_string
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            return {"bAllowAppImpressions": data.get("bAllowAppImpressions")}
        except json.JSONDecodeError:
            return {'error': 'Failed to parse JSON'}
    else:
        return {'error': f'Request failed with status code {response.status_code}'}

def parse_cookie_string(cookie_string):
    cookies = {}
    for item in cookie_string.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

# Call functions in order
cookie_string = "session_id=abc123; path=/"
cookie_dict = parse_cookie_string(cookie_string)
steam_sale_data = get_steam_sale_data(cookie_string)

print(steam_sale_data)