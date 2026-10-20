import requests

def test_financial_data_with_API_key():

    # the URL or API end point where you want to fetch data
    url="https://www.alphavantage.co/query"

    # API Key
    api_key='RK1VS37BVTBB7FG0'

    # params to be sent
    params= {
        "function":"TIME_SERIES_DAILY",
        "symbol": "RELIANCE.BSE", 
        "apikey":api_key
    }

    print("Sending authenticated HTTP GET request to financial API...")

    # sending request along with params
    response=requests.get(url, params=params)

    # Response handling (Checking server codes and payload logic)
    
    if response.status_code==200:
        print("Success! Connection established.")
        data=response.json()

        if "Error message" in data:
            print("Invalid ticker symbol")
        elif "Note" in data:
            print("\n You have hit free tier rate limit 5calls/min")

        else:
            print("Authentication is verified and data retrieved securely")

            print("\n Metadata summary received:")
            if "Meta Data" in data:
                for key, value in data["Meta Data"].items():
                    print(f" {key}:{value}")
            else:
                print(data)

    elif response.status_code == 401:
        print("Authentification failed: Invalid or missing API key")  

    elif response.status_code==429:
        print("Rate limit exceed")
    else:
        print(f"Failed with HTTP status code: {response.status_code}")



if __name__ == "__main__":
    test_financial_data_with_API_key()
