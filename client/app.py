import requests
from client import BikingHubClient

SERVER_URL = "http://localhost:5000"
NAMESPACE = "bikinghub"

if __name__ == "__main__":
    body = None
    print("YRITETÄÄN ACCESSAA APIA")
    with requests.Session() as session:
        session.headers.update({"Accept": "application/vnd.mason+json"})
        resp = session.get(SERVER_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            # print(f"TEST: API body: {body}")
            users_href = body["@controls"][f"{NAMESPACE}:users-all"]["href"]
            # favorites_href = body["@controls"][f"{NAMESPACE}:favorites-all"]["href"]
            # weather_href = body["@controls"][f"{NAMESPACE}:weather-all"]["href"]
            # locations_href = body["@controls"][f"{NAMESPACE}:locations-all"]["href"]

    print("LUODAAN CLIENTTI")
    client = BikingHubClient(session, users_href)
    print("CLIENTTI LUOTU")
    #if client.login("/api/login/"):
    #    print("Login successful")
    #else:
    #    print("Login failed")
    client.run()


    # Main loop for client

        # Suorita komentoja
    
    # Lopeta client