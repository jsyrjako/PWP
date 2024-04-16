"""
This is a client for the BikingHub API. It allows users to login, register,
and interact with the API.
The client is a command line interface that allows users to post, update, and delete data,
as well as view available locations and weather data.
The client also allows users to view and interact with their favourites.
The client uses the requests library to interact with the API.
The client uses the asciified API to display ASCII art.
"""

import json
import urllib
import random
import requests
import time

SERVER_URL = "http://localhost:5000"
NAMESPACE = "bikinghub"


class BikingHubClient:
    """
    A client for the BikingHub API.
    """

    user_controls = {}

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

    def prompt_from_schema_favourite(self, ctrl, location_id=None, headers=None):
        """Prompt the user for input based on the schema in the control."""
        print(f"location_id: {location_id}")
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
            print(f"required_field: {required_field}")
            if required_field == "location_id":
                data[required_field] = location_id
            else:
                data[required_field] = self.convert_input(input(f"{desc}: "), field_type)
        return self.submit_data(ctrl, data)

    def convert_input(self, user_input, field_type):
        """Convert user input to the appropriate type based on the field type."""
        convert_functions = {"integer": int, "number": float, "string": str}
        return convert_functions.get(field_type, str)(user_input)

    def get_controls(self, control_name, path="/api/"):
        """Get the controls for a specific control name."""
        body = None
        # print(f"get_controls path: {path}")
        resp = self.session.get(SERVER_URL + path)
        if resp.status_code != 200:
            print("Unable to access API.")
        body = resp.json()
        ctrl = body.get("@controls", {}).get(f"{NAMESPACE}:{control_name}")
        return ctrl

    def set_api_key(self, api_key):
        """Set the API key in the headers."""
        self.session.headers["Bikinghub-Api-Key"] = api_key

    def get_data(self, endpoint):
        """Get data from the API."""
        resp = self.session.get(SERVER_URL + endpoint)
        return resp.json()

    def get_available_locations(self):
        """Get the available locations from the API."""
        try:
            ctrl = self.get_controls("locations-all")
            headers = self.session.headers
            resp = self.session.get(SERVER_URL + ctrl["href"], headers=headers)

            if resp.status_code == 200:
                return resp.json()
            return None
        except requests.exceptions.RequestException as e:
            print(f"Failed to get locations: {e}")
            return None

    def get_users_favourites(self):
        """Get the user's favourites from the API."""
        try:
            href = self.user_controls["self"]["href"]
            # print(href)
            resp = self.session.get(SERVER_URL + href, headers=self.session.headers)

            ctrl = resp.json()["@controls"]

            ctrl = ctrl["bikinghub:favourites-all"]
            # print(f"get_users_favourites ctrl: {ctrl}")
            resp = self.session.get(
                SERVER_URL + ctrl["href"], headers=self.session.headers
            )

            # print(f"get_users_favourites resp: {resp.json()}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except requests.exceptions.RequestException as e:
            print(f"Failed to get favourites: {e}")
            return None

    def print_weather_data(self, data):
        """Print the weather data for a location."""
        for key, value in data.items():
            if key == "items":
                print("--------------------------------------")
                for k, v in value.items():
                    print(f"{k:22}| {v}")
                print("--------------------------------------")



    def print_favorite_data(self, data):
        """Print the title and description for a favourite."""
        for key, value in data.items():
            if key == "item":
                print("--------------------------------------")
                for k, v in value.items():
                    if k == "title" or k == "description":
                        print(f"{k:12}: {v}")
                print("--------------------------------------")


    def get_location_href(self, location_id):
        """Get the href for a specific location id."""
        resp = self.get_available_locations()
        for item in resp["items"]:
            if item.get("id") == location_id:
                return item["@controls"]["self"]["href"]
        return None

    def get_weather_data(self, location_id):
        """Get the weather data for a specific location id."""
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

    def play_audio(self, url):
        """Play audio from the API."""
        try:
            for(_i, _item) in range(10):
                print(".", end="")
                time.sleep(2)
                resp = self.session.get(url)
                if resp.status_code == 200:
                    print("got audio")
                    break


        except requests.exceptions.RequestException as e:
            print(f"Failed to play audio: {e}")

    def locations_and_controls(self):
        """Get the locations and controls from the API."""

        # Get locations, ask for location id and create menu from available location controls
        already_in_favourites = False

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

        # get location controls
        response = self.get_data(location_href)
        controls = response["@controls"]
        # get controls with bikinhub: prefix
        for key in controls.keys():
            if key.startswith("bikinghub:") or key.startswith("aux_service"):
                # print control name without prefix
                if key != "bikinghub:weather-all":
                    print(key.split(":")[1])

        # add to favourites if not already in favourites
        resp = self.get_users_favourites()
        for item in resp["items"]:
            print(f"location: {location}")
            print(f"item get location_id {item.get('location_id')}")
            print(f"location_id {location_id}")
            if item.get("location_id") == location.get("id"):
                print("Already in favourites")
                already_in_favourites = True
                break

        if already_in_favourites is False:
            print("favourite-add")

        # ask for choice
        choice = input("Enter choice: ")

        if choice == "favourite-add" and already_in_favourites is False:
            ctrl = self.get_controls(
                "favourite-add",
                path=resp["@controls"]["bikinghub:favourite-add"]["href"],
            )
            response = self.prompt_from_schema_favourite(ctrl, location.get("id"))
            return response.status_code
        if choice == "weather-read":
            print("weather-read")
            wread_resp = None
            read_obj = location["@controls"]["aux_service:weather-read"]
            print(f"read_obj: {read_obj}")
            if read_obj.get('href') is None or read_obj.get('method') is None:
                print("No weather data available")
                return
            wread_resp = self.session.get(read_obj["href"])
            download_url = wread_resp.json().get("href")
            print(f"Response from aux service {response}")
            print(f"Download url: {download_url}")

        # get control href
        control_href = controls[f"bikinghub:{choice}"]["href"]
        # print(control_href)

        # If control Method is GET, get data
        if controls[f"bikinghub:{choice}"]["method"] == "GET":
            # print(f"control_href: {control_href}")
            # ctrl = self.get_controls(choice, path=control_href)
            response = self.get_data(control_href)
            self.print_weather_data(response)
        # If control Method is PUT, ask for data and put
        elif controls[f"bikinghub:{choice}"]["method"] == "PUT":
            # print(f"Choice: {choice}")
            # print(f"API location url: {location_href}")
            ctrl = self.get_controls(choice, path=location_href)
            print(ctrl)
            response = self.put_data(ctrl)
            print(response)
        # If control Method is DELETE, delete
        elif controls[f"bikinghub:{choice}"]["method"] == "DELETE":
            # print(control_href)
            response = self.delete_data(control_href)
            print(response)


    def favourites_and_controls(self):
        """Get the favourites and controls from the API."""
        resp = self.get_users_favourites()

        print("Favourites")
        i = 1
        for item in resp["items"]:
            print(f"{item['title']}: ({i})")
            i += 1
        favourite_id = input("Enter favourite id: ")

        favourite = resp["items"][int(favourite_id) - 1]
        favourite_href = favourite["@controls"]["self"]["href"]
        #print(favourite_href)

        controls = self.get_data(favourite_href)["@controls"]
        #print(f"controls **************:{controls}")
        for key in controls.keys():
            if key.startswith("bikinghub:"):
                # print control name without prefix
                if key != "bikinghub:locations-all":
                    print(key.split(":")[1])

        # ask for choice
        choice = input("Enter choice: ")

        # get control href
        control_href = controls[f"bikinghub:{choice}"]["href"]
        #print(control_href)

        # If control Method is GET, get data
        if controls[f"bikinghub:{choice}"]["method"] == "GET":
            response = self.get_data(control_href)
            self.print_favorite_data(response)
            # Get specific location id associated with the favorite
            location_id = favourite.get("location_id")
            # Retrieve controls for the specific location
            location_href = self.get_location_href(location_id)
            # Get weather data for the specific location
            response_location = self.get_data(location_href)
            control_href_location = response_location["@controls"]["bikinghub:weather-location"]["href"]
            response_location = self.get_data(control_href_location)
            self.print_weather_data(response_location)
        # If control Method is PUT, ask for data and put
        elif controls[f"bikinghub:{choice}"]["method"] == "PUT":
            ctrl = self.get_controls(choice, path=favourite_href)
            response = self.put_data(ctrl)
            print(response)
        # If control Method is DELETE, delete
        elif controls[f"bikinghub:{choice}"]["method"] == "DELETE":
            response = self.delete_data(control_href)
            print(response)


    def post_data(self, endpoint):
        """Post data to the API."""
        # ask for schema
        resp = self.prompt_from_schema(endpoint)
        return resp.status_code

    def put_data(self, endpoint):
        """Put data to the API."""
        resp = self.prompt_from_schema(endpoint)
        return resp.status_code

    def delete_data(self, endpoint):
        """Delete data from the API."""
        print(self.session.headers)
        print(SERVER_URL + endpoint)
        resp = self.session.delete(SERVER_URL + endpoint, headers=self.session.headers)
        return resp.status_code

    def get_ascii_font(self):
        """Get a random ASCII font from the asciified API."""
        font_url = "https://asciified.thelicato.io/api/v2/fonts"
        font_resp = self.session.get(font_url)
        fonts = (font_resp.json()).get("fonts")
        font = random.choice(fonts)
        return font

    def get_ascii_art(self, prompt, font=None):
        """Get ASCII art for a prompt using a specific font."""
        if not font:
            font = self.get_ascii_font()
        params = urllib.parse.urlencode({"text": prompt, "font": font})
        url = "https://asciified.thelicato.io/api/v2/ascii?" + params
        resp = self.session.get(url)
        return resp.text

    def login(self):
        """Login to the API."""
        try:
            ctrl = self.get_controls("user-login")
            headers = self.session.headers
            resp = self.prompt_from_schema(ctrl, headers=headers)

            self.user_controls = resp.json()["@controls"]

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
        """Register a new user with the API."""
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
        """Display the login menu."""
        # self.stdscr.clear()
        # self.stdscr.addstr("1. Login (l)\n", curses.color_pair(1))
        # self.stdscr.addstr("2. Register (r)\n", curses.color_pair(2))
        # self.stdscr.refresh()
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("4. Continue as guest")

    def display_data_menu(self):
        """Display the data menu."""
        print("1. Favorites and controls")
        print("2. Locations and controls")
        print("Q. Exit")

    def login_loop(self):
        """Run the login loop."""
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
        """Run the menu loop."""
        try:
            while self.logged_in is True:
                self.display_data_menu()
                choice = input("Enter choice: ")
                match choice:
                    case "1":
                        self.favourites_and_controls()

                    case "2":
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
        """Run the client."""

        self.login_loop()
        self.menu_loop()
