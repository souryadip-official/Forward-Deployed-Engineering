import requests

def get_exchange_rate(
    base: str,
    target: str 
):

    url = f"https://api.frankfurter.dev/v2/rate/{base}/{target}"
    response = requests.get(url).json()
    return response["rate"]