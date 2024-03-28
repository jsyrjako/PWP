import requests
import json
#from curses import wrapper

SERVER_URL = "http://localhost:5000/"
NAMESPACE = "bikinghub"

# Initialize curses
#print("TEST Initializing curses")
# stdscr = curses.initscr()
#curses.noecho()
#curses.cbreak()
# stdscr.keypad(True)
#print("TEST Curses initialized")
## Initialize color pairs
#curses.start_color()
#curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
#curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
#curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)


class BikingHubClient:

    def __init__(self, session, users_href):
        print("TEST Initializing client")

        self.session = session
        self.users_href = users_href
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Bikinghub-Api-Key": ""
        }
        self.endpoints = {}




    # def __del__(self):
    #     curses.nocbreak()
    #     self.stdscr.keypad(False)
    #     curses.echo()
    #     curses.endwin()

    def set_api_key(self, api_key):
        self.session.headers["Bikinghub-Api-Key"] = api_key

    def get_data(self, endpoint):
        resp = self.session.get(SERVER_URL + endpoint)
        return resp.json()
    
    def get_weather_data(self, endpoint, location_id):
        resp = self.session.get(SERVER_URL + endpoint + f"/{location_id}")
        return resp.json()    

    def post_data(self, endpoint, data):
        resp = self.session.post(SERVER_URL + endpoint, json=data)
        return resp.status_code

    def put_data(self, endpoint, data):
        resp = self.session.put(SERVER_URL + endpoint, json=data)
        return resp.status_code

    def delete_data(self, endpoint):
        resp = self.session.delete(SERVER_URL + endpoint)
        return resp.status_code
    
    def login(self, endpoint, username="user1", password="password1"):
        resp = self.session.post(SERVER_URL + endpoint, json={"name": username, "password": password})
        
        if resp.status_code == 200:
            self.set_api_key(resp.json()["api_key"])
            return True
        return False

    def register(self, endpoint, username="user2", password="password2"):
        resp = self.session.post(SERVER_URL + endpoint, json={"username": username, "password": password})
        return resp.status_code
            

    def create_user():
        pass
    
    def display_login_menu(self):
        # self.stdscr.clear()
        # self.stdscr.addstr("1. Login (l)\n", curses.color_pair(1))
        # self.stdscr.addstr("2. Register (r)\n", curses.color_pair(2))
        # self.stdscr.refresh()
        print("1. Login")
        print("2. Register")
        print("3. Post data")
        print("4. Update data")
        print("5. Get weather data")
        print("6. Exit")
    
    def run(self):
        print("TEST Running client")
        while True:
            self.display_login_menu()
            choice = input("Enter choice: ")
            match choice:
                case '1':
                    username = input("Enter username: ")
                    password = input("Enter password: ")
                    if self.login("/api/login", username, password):
                        print("Login successful")
                    else:
                        print("Login failed")

                case '2':
                    # promt user schema for registration from server
                    self.prompt_from_schema(self.users_href)

                case '3':
                    data = {"key": "value"}  # replace with actual data
                    response = self.post_data("/api/data", data)  # replace with actual endpoint
                    # self.stdscr.addstr(str(response) + "\n")
                    print(str(response))
                case '4':
                    data = {"key": "value"}  # replace with actual data
                    response = self.put_data("/api/data", data)  # replace with actual endpoint
                    # self.stdscr.addstr(str(response) + "\n")
                    print(str(response))
                case '5':
                    location_id = "location_id"  # replace with actual location ID
                    weather_data = self.get_weather_data(location_id)
                    # self.stdscr.addstr(str(weather_data) + "\n")
                    print(str(weather_data))
                case '6':
                    break
                case _:
                    # self.stdscr.addstr("Invalid choice\n")
                    print("Invalid choice")
            # self.stdscr.getch()
            print("TEST Exiting client")

    def submit_data(self, ctrl, data):
        """Submit data to the API and return the response."""
        url = SERVER_URL + ctrl["href"]
        resp = self.session.request(
            ctrl["method"],
            url,
            data=json.dumps(data),
            headers={"Content-type": "application/json"},
        )
        return resp

    def prompt_from_schema(self, ctrl):
        """Prompt the user for input based on the schema in the control."""
        data = {}
        schema = ctrl.get("schema")
        if not schema:
            schema_url = ctrl["schemaUrl"]
            schema_resp = self.session.get(schema_url)
            schema = schema_resp.json()

        fields = schema["required"]
        for required_field in fields:
            desc = schema["properties"][fields].get("description")
            field_type = schema["properties"][fields].get("type")
            data[required_field] = self.convert_input(input(f"{desc}: "), field_type)
            
        return self.submit_data(self.session, ctrl, data)

    def convert_input(user_input, field_type):
        convert_functions = {'integer': int, 'number': float, 'string': str}
        return convert_functions.get(field_type, str)(user_input)

