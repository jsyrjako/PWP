import requests
from client import BikingHubClient

SERVER_URL = "http://localhost:5000"
NAMESPACE = "bikinghub"
YELLOW = '\033[93m'
RESET = '\033[0m'

if __name__ == "__main__":
    body = None
    with requests.Session() as session:
        session.headers.update({"Accept": "application/vnd.mason+json"})
        resp = session.get(SERVER_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            users_href = body["@controls"][f"{NAMESPACE}:users-all"]["href"]

    print(f"{YELLOW}STARTING CLIENT...{RESET}\n")
    client = BikingHubClient(session, users_href)
    client.run()
