import requests
import json
import urllib
import random

SERVER_URL = "http://localhost:5000"
NAMESPACE = "bikinghub"


class BikingHubClient:

    def __init__(self, session, users_href):
        print("TEST Initializing client")

        self.session = session
        self.users_href = users_href
        self.session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Bikinghub-Api-Key": "",
        }
        self.logged_in = False
        self.endpoints = {}

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

    def prompt_from_schema(self, ctrl, headers=None):
        """Prompt the user for input based on the schema in the control."""
        data = {}
        schema = ctrl.get("schema")
        if not schema:
            schema_url = ctrl["schemaUrl"]
            schema_resp = self.session.get(schema_url, headers=headers)
            if schema_resp.status_code != 200:
                print("Unable to access schema.")
                return None
            schema = schema_resp.json()
        fields = schema["required"]
        for required_field in fields:
            desc = schema["properties"][required_field].get("description")
            field_type = schema["properties"][required_field].get("type")
            data[required_field] = self.convert_input(input(f"{desc}: "), field_type)
        return self.submit_data(ctrl, data)

    def convert_input(self, user_input, field_type):
        convert_functions = {"integer": int, "number": float, "string": str}
        return convert_functions.get(field_type, str)(user_input)

    def get_controls(self, control_name, path="/api/"):
        body = None
        resp = self.session.get(SERVER_URL + path)
        if resp.status_code != 200:
            print("Unable to access API.")
        body = resp.json()
        ctrl = body.get("@controls", {}).get(f"{NAMESPACE}:{control_name}")
        return ctrl

    def set_api_key(self, api_key):
        self.session.headers["Bikinghub-Api-Key"] = api_key

    def get_data(self, endpoint):
        resp = self.session.get(SERVER_URL + endpoint)
        return resp.json()

    def get_available_locations(self):
        try:
            ctrl = self.get_controls("locations-all")
            headers = self.session.headers
            resp = self.session.get(SERVER_URL + ctrl["href"], headers=headers)

            if resp.status_code == 200:
                return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get locations: {e}")
            return None

    def print_weather_data(self, data):
        for key, value in data.items():
            if key == "items":
                for k, v in value.items():
                    print(f"{k}: {v}")

    def get_weather_data(self, location_id):
        try:
            ctrl = self.get_controls("weather-all")
            headers = self.session.headers
            resp = self.session.get(SERVER_URL + ctrl["href"], headers=headers)

            # get href for location id
            location_href = None
            for item in resp.json()["items"]:
                if item["id"] == int(location_id):
                    location_href = item["@controls"]["self"]["href"]
                    break

            if location_href is None:
                print("Invalid location id")
                return None

            resp = self.session.get(SERVER_URL + location_href, headers=headers)
            return resp.json()
        except KeyboardInterrupt:
            return None

    def locations_and_controls(self):
        # Get locations, ask for location id and create menu from available location controls
        resp = self.get_available_locations()

        api_location_url = resp["@controls"]["self"]["href"]

        # print locations and ask for location id to get weather data
        i = 1
        for item in resp["items"]:
            print(f"{item['name']}: ({i})")
            i += 1
        # print add new location
        print("Add new location: (0)")
        location_id = input("Enter location id: ")

        if location_id == "0":
            ctrl = self.get_controls("location-add", api_location_url)
            response = self.prompt_from_schema(ctrl)
            return response.status_code

        # get location href
        location = resp["items"][int(location_id) - 1]
        location_href = location["@controls"]["self"]["href"]
        print(location_href)

        # get location controls
        response = self.get_data(location_href)
        controls = response["@controls"]
        # get controls with bikinhub: prefix
        for key in controls.keys():
            if key.startswith("bikinghub:"):
                # print control name without prefix
                if key != "bikinghub:weather-all":
                    print(key.split(":")[1])

        # ask for choice
        choice = input("Enter choice: ")
        # get control href

        control_href = controls[f"bikinghub:{choice}"]["href"]
        print(control_href)
        # If control Method is GET, get data
        if controls[f"bikinghub:{choice}"]["method"] == "GET":
            print(f"control_href: {control_href}")
            # ctrl = self.get_controls(choice, path=control_href)
            response = self.get_data(control_href)
            self.print_weather_data(response)
        # If control Method is PUT, ask for data and put
        elif controls[f"bikinghub:{choice}"]["method"] == "PUT":
            print(f"Choice: {choice}")
            print(f"API location url: {location_href}")
            ctrl = self.get_controls(choice, path=location_href)
            print(ctrl)
            response = self.put_data(ctrl)
            print(response)
        # If control Method is DELETE, delete
        elif controls[f"bikinghub:{choice}"]["method"] == "DELETE":
            print(control_href)
            response = self.delete_data(control_href)
            print(response)

    def post_data(self, endpoint):
        # ask for schema
        resp = self.prompt_from_schema(endpoint)
        return resp.status_code

    def put_data(self, endpoint):
        resp = self.prompt_from_schema(endpoint)
        return resp.status_code

    def delete_data(self, endpoint):
        print(self.session.headers)
        print(SERVER_URL + endpoint)
        resp = self.session.delete(SERVER_URL + endpoint, headers=self.session.headers)
        return resp.status_code

    def get_ascii_font(self):
        font_url = "https://asciified.thelicato.io/api/v2/fonts"
        font_resp = self.session.get(font_url)
        fonts = (font_resp.json()).get("fonts")
        font = random.choice(fonts)
        return font

    def get_ascii_art(self, prompt, font=None):
        if not font:
            font = self.get_ascii_font()
        params = urllib.parse.urlencode({"text": prompt, "font": font})
        url = "https://asciified.thelicato.io/api/v2/ascii?" + params
        resp = self.session.get(url)
        return resp.text

    def login(self):
        try:
            ctrl = self.get_controls("user-login")
            headers = self.session.headers
            resp = self.prompt_from_schema(ctrl, headers=headers)

            if resp.status_code == 200:
                print(f"Login successful")
                username = resp.json()["username"]
                font = self.get_ascii_font()
                print(self.get_ascii_art("Welcome", font))
                print(self.get_ascii_art(username, font))
                self.set_api_key(resp.json()["api_key"])
                return True
            print(f"Login failed")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Login failed")
            return False
        except KeyboardInterrupt:
            return False

    def register(self):
        try:
            ctrl = self.get_controls("user-add")
            headers = self.session.headers
            resp = self.prompt_from_schema(ctrl, headers=headers)

            while resp.status_code == 409:
                print("User already exists")
                print("Please enter new credentials")
                resp = self.prompt_from_schema(ctrl, headers=headers)

            if resp.status_code == 201:
                return "User registered successfully"
            elif resp.status_code == 409:
                return "User already exists"
            return resp.status_code
        except KeyboardInterrupt:
            return "User registration cancelled"

    def display_login_menu(self):
        # self.stdscr.clear()
        # self.stdscr.addstr("1. Login (l)\n", curses.color_pair(1))
        # self.stdscr.addstr("2. Register (r)\n", curses.color_pair(2))
        # self.stdscr.refresh()
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("4. Continue as guest")

    def display_data_menu(self):
        print("1. Post data")
        print("2. Update data")
        print("3. Get weather data")
        print("4. Locations and controls")
        print("Q. Exit")

    def login_loop(self):
        try:
            while self.logged_in is False:
                print("TEST Running client")
                self.display_login_menu()
                choice = input("Enter choice: ")
                match choice:
                    case "1":
                        if self.login():
                            print("Login successful")
                            self.logged_in = True
                        else:
                            print("Login failed")
                            self.logged_in = False

                    case "2":
                        # promt user schema for registration from server
                        response = self.register()
                        # self.stdscr.addstr(str(response) + "\n")
                        print(str(response))

                    case "3":
                        break

                    case "4":
                        self.logged_in = True
        except KeyboardInterrupt:
            pass
        finally:
            print("\nTEST Exiting client")

    def menu_loop(self):
        try:
            while self.logged_in is True:
                self.display_data_menu()
                choice = input("Enter choice: ")
                match choice:
                    case "1":
                        data = {"key": "value"}  # replace with actual data
                        response = self.post_data(
                            "/api/locations/"
                        )  # replace with actual endpoint
                        # self.stdscr.addstr(str(response) + "\n")
                        print(str(response))
                    case "2":
                        data = {"key": "value"}  # replace with actual data
                        response = self.put_data(
                            "/api/data", data
                        )  # replace with actual endpoint
                        # self.stdscr.addstr(str(response) + "\n")
                        print(str(response))
                    case "3":
                        # get available locations
                        response = self.get_available_locations()
                        # print locations and ask for location id to get weather data
                        i = 1
                        for item in response["items"]:
                            print(f"{item['name']}: ({i})")
                            i += 1

                        location_id = input("Enter location id: ")
                        # get weather data
                        response = self.get_weather_data(location_id)
                        # print weather data
                        print(response)

                    case "4":
                        self.locations_and_controls()

                    case "ascii":
                        f_prompt = input("Enter font (empty for random): ")
                        if not f_prompt:
                            f_prompt = self.get_ascii_font()
                        prompt = input("Enter prompt: ")
                        ascii_art = self.get_ascii_art(prompt)
                        # self.stdscr.addstr(ascii_art + "\n")
                        print(ascii_art)
                    case "Q", "q", "exit", "EXIT":
                        self.logged_in = True
                    case _:
                        # self.stdscr.addstr("Invalid choice\n")
                        print("Invalid choice")
                # self.stdscr.getch()
                print("TEST Exiting client")
        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting client")

    def run(self):

        self.login_loop()
        self.menu_loop()
