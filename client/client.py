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
import time
import os
from getpass import getpass
import requests
import simpleaudio as sa

SERVER_URL = "http://localhost:5000"
NAMESPACE = "bikinghub"
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


class BikingHubClient:
    """
    A client for the BikingHub API.
    """

    user_controls = {}

    def __init__(self, session, users_href):
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

    def prompt_from_schema(self, ctrl, location_id=None, headers=None):
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
            if required_field == "password":
                data[required_field] = getpass(f"{desc}: ")
            elif required_field == "location_id":
                data[required_field] = location_id
            else:
                while True:
                    try:
                        data[required_field] = self.convert_input(
                            input(f"{desc}: "), field_type
                        )
                    except ValueError:
                        print("Invalid input")
                        continue
                    break
        return self.submit_data(ctrl, data)

    def convert_input(self, user_input, field_type):
        """Convert user input to the appropriate type based on the field type."""
        convert_functions = {"integer": int, "number": float, "string": str}
        return convert_functions.get(field_type, str)(user_input)

    def get_controls(self, control_name, path="/api/"):
        """Get the controls for a specific control name."""
        body = None
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
            resp = self.session.get(SERVER_URL + href, headers=self.session.headers)
            ctrl = resp.json()["@controls"]
            ctrl = ctrl["bikinghub:favourites-all"]

            resp = self.session.get(
                SERVER_URL + ctrl["href"], headers=self.session.headers
            )

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
            i = 0
            while i < 20:
                print(".", end="")
                time.sleep(1)
                resp = self.session.get(url)
                if resp.status_code == 200:
                    print("Got audio")
                    # Save the audio file
                    os.makedirs("tmp", exist_ok=True)
                    with open("tmp/file.wav", "wb") as audio:
                        audio.write(resp.content)
                    break
                i += 1

            print("Playing audio")
            wave_obj = sa.WaveObject.from_wave_file("tmp/file.wav")
            wave_obj.play()

        except requests.exceptions.RequestException as e:
            print(f"Failed to play audio: {e}")

    def locations_and_controls(self):
        """Get the locations and controls from the API."""

        # Get locations, ask for location id and create menu from available location controls
        already_in_favourites = False

        resp = self.get_available_locations()

        api_location_url = resp["@controls"]["self"]["href"]

        print("\nLocations:")
        # print locations and ask for location id to get weather data
        item_list = []
        i = 1
        for item in resp["items"]:
            item_list.append(str(i))
            print(f"{item['name']}: {RED}({i}){RESET}")
            i += 1

        # print add new location
        print(f"Add new location: {RED}(0){RESET}")
        print(f"Enter {RED}Q{RESET} to to go back")
        location_id = input("Enter location id: ")

        while location_id not in item_list and location_id not in ["0", "Q", "q"]:
            print("Invalid location id")
            location_id = input("Enter location id: ")

        if location_id == "0":
            ctrl = self.get_controls("location-add", api_location_url)
            response = self.prompt_from_schema(ctrl)
            if response.status_code == 201:
                print(f"Location added {GREEN}successfully{RESET}\n")
                return
            else:
                print(f"Location add {RED}failed{RESET}\n")

                return

        if location_id == "Q" or location_id == "q":
            print("")
            return

        # get location href
        location = resp["items"][int(location_id) - 1]
        location_href = location["@controls"]["self"]["href"]

        print("\nControls:")
        # get location controls
        response = self.get_data(location_href)
        controls = response["@controls"]
        # get controls with bikinhub: prefix
        for key in controls.keys():
            if key.startswith("bikinghub:") or key.startswith("aux_service"):
                # print control name without prefix
                if key != "bikinghub:weather-all":
                    print(f"{RED}{key.split(':')[1]}{RESET}")
        print(f"Press {RED}Q{RESET} to go back")

        # add to favourites if not already in favourites
        resp = self.get_users_favourites()
        for item in resp["items"]:
            # print(f"location: {location}")
            # print(f"item get location_id {item.get('location_id')}")
            # print(f"location_id {location_id}")
            if item.get("location_id") == location.get("id"):
                print("Already in favourites")
                already_in_favourites = True
                break

        if already_in_favourites is False:
            print(f"{RED}favourite-add{RESET}")

        # ask for choice
        choice = input("Enter choice: ")

        split_keys = []
        for key in controls.keys():
            if key.startswith("bikinghub:") or key.startswith("aux_service"):
                split_keys.append(key.split(":")[1])

        choice = choice.lower()

        while (
            choice not in split_keys
            and choice not in ["Q", "q"]
            and choice != "favourite-add"
        ):
            choice = input("Enter choice: ")

        if choice == "Q" or choice == "q":
            print("")
            return

        if choice == "favourite-add" and already_in_favourites is False:
            ctrl = self.get_controls(
                "favourite-add",
                path=resp["@controls"]["bikinghub:favourite-add"]["href"],
            )
            response = self.prompt_from_schema(ctrl, location.get("id"))
            if response.status_code == 201:
                print(f"Favourite added {GREEN}successfully{RESET}")
                return
            else:
                print(f"Favourite add {RED}failed{RESET}")
                return

        if choice == "weather-read":
            print("weather-read")
            wread_resp = None
            read_obj = location["@controls"]["aux_service:weather-read"]
            # print(f"read_obj: {read_obj}")
            if read_obj.get("href") is None or read_obj.get("method") is None:
                print("No weather data available")
                return
            wread_resp = self.session.get(read_obj["href"])
            download_url = wread_resp.json().get("href")
            print(f"Download url: {download_url}")
            self.play_audio(download_url)
            if wread_resp.status_code == 202:
                print(f"Weather data read {GREEN} successfully{RESET}\n")
                return
            else:
                print(f"Weather data read {RED}failed{RESET}\n")
                return

        # get control href
        control_href = controls[f"bikinghub:{choice}"]["href"]
        # print(control_href)

        # If control Method is GET, get data
        if controls[f"bikinghub:{choice}"]["method"] == "GET":
            response = self.get_data(control_href)
            self.print_weather_data(response)

        # If control Method is PUT, ask for data and put
        elif controls[f"bikinghub:{choice}"]["method"] == "PUT":
            ctrl = self.get_controls(choice, path=location_href)
            response = self.put_data(ctrl)
            if response == 204:
                print(f"Location updated {GREEN}successfully{RESET}")
                return
            else:
                print(f"Location update {RED}failed{RESET}")
                return

        # If control Method is DELETE, delete
        elif controls[f"bikinghub:{choice}"]["method"] == "DELETE":
            # print(control_href)
            response = self.delete_data(control_href)
            if response == 204:
                print(f"Location deleted {GREEN}successfully{RESET}")
                return
            else:
                print(f"Location delete {RED}failed{RESET}")
                return
        print("")

    def favourites_and_controls(self):
        """Get the favourites and controls from the API."""
        resp = self.get_users_favourites()

        print("\nFavourites:")
        index_list = []
        i = 1
        for item in resp["items"]:
            index_list.append(str(i))
            print(f"{item['title']}: {RED}({i}){RESET}")
            i += 1

        print(f"Press {RED}Q{RESET} to go back")

        favourite_id = input("Enter favourite id: ")

        while favourite_id not in index_list and favourite_id not in ["Q", "q"]:
            print("Invalid favourite id")
            favourite_id = input("Enter favourite id: ")

        if favourite_id == "Q" or favourite_id == "q":
            print("")
            return

        favourite = resp["items"][int(favourite_id) - 1]
        favourite_href = favourite["@controls"]["self"]["href"]

        split_keys = []

        print("\nControls:")
        controls = self.get_data(favourite_href)["@controls"]
        for key in controls.keys():
            if key.startswith("bikinghub:"):
                # print control name without prefix
                if key != "bikinghub:locations-all":
                    print(f"{RED}{key.split(':')[1]}{RESET}")
                    split_keys.append(key.split(":")[1])
        print(f"Press {RED}Q{RESET} to go back")

        choice = None

        while True:
            choice = input("Enter choice: ")
            if choice.lower() in ["quit", "q"] or choice in split_keys:
                break

        if choice == "Q" or choice == "q":
            print("")
            return

        # get control href
        control_href = controls[f"bikinghub:{choice}"]["href"]

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
            control_href_location = response_location["@controls"][
                "bikinghub:weather-location"
            ]["href"]
            response_location = self.get_data(control_href_location)
            self.print_weather_data(response_location)
        # If control Method is PUT, ask for data and put
        elif controls[f"bikinghub:{choice}"]["method"] == "PUT":
            ctrl = self.get_controls(choice, path=favourite_href)
            location_id = favourite.get("location_id")
            response = self.put_data(ctrl, location_id)
            if response == 204:
                print(f"Favourite updated {GREEN}successfully{RESET}")
            else:
                print(f"Favourite update {RED}failed{RESET}")
        # If control Method is DELETE, delete
        elif controls[f"bikinghub:{choice}"]["method"] == "DELETE":
            response = self.delete_data(control_href)
            if response == 204:
                print(f"Favourite deleted {GREEN}successfully{RESET}")
            else:
                print(f"Favourite delete {RED}failed{RESET}")
        print("")

    def post_data(self, endpoint):
        """Post data to the API."""
        # ask for schema
        resp = self.prompt_from_schema(endpoint)
        return resp.status_code

    def put_data(self, endpoint, location_id=None):
        """Put data to the API."""
        resp = self.prompt_from_schema(endpoint, location_id=location_id)
        return resp.status_code

    def delete_data(self, endpoint):
        """Delete data from the API."""
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
                print(f"Login {GREEN}successful{RESET}")
                username = resp.json()["username"]
                font = self.get_ascii_font()
                print(self.get_ascii_art("Welcome", font))
                print(self.get_ascii_art(username, font))
                self.set_api_key(resp.json()["api_key"])
                return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"Login {RED}failed{RESET}", e)
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
                return f"User registered {GREEN}successfully{RESET}"
            elif resp.status_code == 409:
                return "User already {RED}exists{RESET}"
            return resp.status_code
        except KeyboardInterrupt:
            return f"User registration {RED}cancelled{RESET}"

    def display_login_menu(self):
        """Display the login menu."""
        print(f"{RED}1. {RESET}Login")
        print(f"{RED}2. {RESET}Register")
        print(f"{RED}3. {RESET}Exit")
        print(f"{RED}4. {RESET}Continue as guest")

    def display_data_menu(self):
        """Display the data menu."""
        print(f"{RED}1. {RESET}Favorites and controls")
        print(f"{RED}2. {RESET}Locations and controls")
        print(f"{RED}Q. {RESET}Exit")

    def login_loop(self):
        """Run the login loop."""
        try:
            while self.logged_in is False:
                self.display_login_menu()
                choice = input("Enter choice: ")
                match choice:
                    case "1":
                        if self.login():
                            self.logged_in = True
                        else:
                            print("Login failed")
                            self.logged_in = False

                    case "2":
                        # promt user schema for registration from server
                        response = self.register()
                        print(str(response))

                    case "3":
                        break

                    case "4":
                        self.logged_in = True
                    case _:
                        print("Invalid choice")
        except KeyboardInterrupt:
            pass

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
                        print(ascii_art)

                    case "tts":
                        text = input("Enter text: ")
                        print(f"Text to speech: {text}")

                    case "Q" | "q" | "exit" | "EXIT" | "Quit" | "quit":
                        self.logged_in = False
                        break
                    case _:
                        print("Invalid choice")
        except KeyboardInterrupt:
            pass

    def run(self):
        """Run the client."""

        self.login_loop()
        self.menu_loop()
