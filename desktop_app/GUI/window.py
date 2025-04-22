import customtkinter as ctk
from ArduinoBackend.arduinoManager import ArduinoManager
import requests

from GUI.ColorTab.color_tab import ColorTab
from GUI.AnimationTab.animation_tab import AnimationTab
from GUI.SingleLEDControllTab.single_led_tab import SingleLedTab


class Window(ctk.CTk):
    button_options = {
        "corner_radius": 7,
        "height": 50,
        "fg_color": "#8387C4",
        "hover_color": "#8378C4",
        "text_color": "white",
        "font": ("Inter", 20, "bold"),
        "border_width": 4,
        "border_color": "#2D315A",
    }

    # Default color and animation settings
    r_value = 101
    g_value = 101
    b_value = 101
    brightness = 51
    speed = 25
    command = "ledOn"
    last_command = ""
    last_button = None

    def __init__(self, title, width, height, max_width, max_height):
        super().__init__()

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        # Configure grid layout
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._manager = ArduinoManager()

        for i in self._manager.devices:
            Window.last_command = f"http://{i.ip_address}{i.last_command}"

        # Initialize frames
        self.midFrame = self.initMidFrame()
        self.midFrame.grid(row=1, rowspan=9, column=0, sticky="nsew", padx=20, pady=3)
        self.midFrame.pack_propagate(False)

        self.botFrame = self.initBotFrame()
        self.botFrame.grid(row=10, column=0, sticky="nsew", padx=20, pady=3)

        self.topFrame = self.initTopFrame()
        self.topFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=3)

        # Animation state
        self.running = False
        self.animation_task = None

        # Initialize starting tab
        self.current_tab = self.initScanTab()
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initTopFrame(self):
        """Initialize the top frame with navigation buttons"""
        topFrame = ctk.CTkFrame(
            master=self,
            height=20,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        topFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        topFrame.grid_rowconfigure(1, weight=1)

        # Title label
        label = ctk.CTkLabel(
            topFrame, text="LED-Controller", font=("Inter", 30, "bold")
        )
        label.grid(row=0, column=0, columnspan=4, pady=5)

        self._scan_tab = self.initScanTab()
        self._color_tab = self.initColorTab()
        self._animation_tab = self.initAnimationTab()
        self._single_tab = self.initSingeLEDTab()

        # Navigation buttons
        button_data = [
            ("SCAN", self._scan_tab),
            ("COLOR", self._color_tab),
            ("ANIMATION", self._animation_tab),
            ("SINGLE LED", self._single_tab),
        ]

        for col, (text, tab_init) in enumerate(button_data):
            btn = ctk.CTkButton(
                topFrame,
                text=text,
                **Window.button_options,
            )
            btn.grid(row=1, column=col, pady=5, padx=10, sticky="ew")
            btn.configure(
                command=lambda b=btn, f=tab_init: self.loadTab(f, b),
            )

        return topFrame

    def loadTab(self, tab, button: ctk.CTkButton):
        """Replace current tab with new tab"""
        if Window.last_button is not None:
            Window.last_button.configure(True, **Window.button_options)

        button.configure(fg_color="#44477A")
        Window.last_button = button

        if isinstance(tab, str):
            self._manager = ArduinoManager()
            self._build_device_map()
            options_list = list(self.device_map.keys())
            print(options_list)
            default_value = options_list[0] if options_list else "No devices"

            self.option_menu.configure(
                values=options_list,
                variable=ctk.StringVar(value=default_value),
            )

            tab.update_arduinos(self._manager)

        self.current_tab.destroy()
        self.current_tab = tab
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initMidFrame(self):
        """Initialize the middle frame that will contain tab content"""
        middleFrame = ctk.CTkFrame(
            master=self,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )
        return middleFrame

    def initBotFrame(self):
        """Initialize the bottom frame with control buttons"""
        botFrame = ctk.CTkFrame(
            master=self,
            height=20,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        botFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        botFrame.grid_rowconfigure(0, weight=1)

        self._build_device_map()
        options = list(self.device_map.keys())
        default_value = options[0] if options else "No devices"

        self.option_menu = ctk.CTkOptionMenu(
            botFrame,
            values=options,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            button_color="#8387C4",
            button_hover_color="#6D72A3",
            dropdown_fg_color="#8387C4",
            dropdown_text_color="white",
            variable=ctk.StringVar(value=default_value),
            command=self.option_change,
        )
        self.option_menu.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        # Control buttons
        button_data = [
            ("LED ON", self.ledOnButtonClick),
            ("LED OFF", self.ledOffButtonClick),
            ("PUSH", self.pushButtonClick),
        ]

        for col, (text, command) in enumerate(button_data):
            btn = ctk.CTkButton(
                botFrame, text=text, command=command, **Window.button_options
            )
            btn.grid(row=0, column=col + 1, pady=5, padx=10, sticky="ew")

        return botFrame

    def _build_device_map(self, *args) -> dict:
        """
        Build a mapping from display names to device objects.
        Handles duplicate names by adding unique identifiers.
        """
        self.device_map = {}
        name_counts = {}

        if args:
            self._manager = args[0]

        for device in self._manager.devices:
            if device():
                name = device.name

                # Handle duplicate names by adding MAC address suffix
                if name in self.device_map:
                    # If this is the first duplicate, rename the original
                    if name_counts.get(name, 0) == 0:
                        original_device = self.device_map[name]
                        short_mac = self._get_short_mac(original_device.mac_address)
                        new_key = f"{name} ({short_mac})"
                        self.device_map[new_key] = original_device
                        del self.device_map[name]

                    # Count this name
                    name_counts[name] = name_counts.get(name, 0) + 1

                    # Add this device with MAC suffix
                    short_mac = self._get_short_mac(device.mac_address)
                    key = f"{name} ({short_mac})"
                    self.device_map[key] = device
                else:
                    # First occurrence of this name
                    self.device_map[name] = device
                    name_counts[name] = 0

        return self.device_map

    def _get_short_mac(self, mac_address: str) -> str:
        """
        Get shortened version of MAC address for display

        Args:
            mac_address: Full MAC address

        Returns:
            Last 6 characters of MAC address
        """
        if not mac_address or mac_address == "Unknown":
            return "Unknown"
        # Return last 6 chars of MAC address
        return mac_address[-6:].upper()

    def ledOnButtonClick(self) -> None:
        """Handle LED ON button click"""
        if self.option_menu.get() in self.device_map.keys():
            arduino_as_dict = self.device_map[self.option_menu.get()].to_dict()
            if arduino_as_dict["status"]:
                self.post(Window.last_command)

    def ledOffButtonClick(self) -> None:
        """Handle LED OFF button click"""
        if self.option_menu.get() in self.device_map.keys():
            arduino_as_dict = self.device_map[self.option_menu.get()].to_dict()
            if arduino_as_dict["status"]:
                url = f"http://{arduino_as_dict["ip_address"]}/ledOff"
                self.post(url)

    def pushButtonClick(self) -> None:
        """Push current color settings to device"""
        if isinstance(self.current_tab, SingleLedTab):
            arduino_as_dict = self.device_map[self.option_menu.get()].to_dict()
            a = ()

            for i in self.current_tab._led_index_to_color:
                new_element = (i,) + self.current_tab._led_index_to_color[i]
                a = a + (new_element,)

            url = f"http://{arduino_as_dict["ip_address"]}/singleLED?singleLED={a}"
            Window.last_command = url

            for i in self._manager.devices:
                if i == self.device_map[self.option_menu.get()]:
                    i._last_command = url.replace(
                        f"http://{arduino_as_dict["ip_address"]}", ""
                    )
                    i._single_led = a

                    self.device_map[self.option_menu.get()] = i

            self._manager._save_to_file(self._manager.devices)

            self.post(url)
            return

        if self.option_menu.get() in self.device_map.keys():
            arduino_as_dict = self.device_map[self.option_menu.get()].to_dict()
            if arduino_as_dict["status"]:
                r = Window.r_value
                g = Window.g_value
                b = Window.b_value
                brightness = Window.brightness
                speed = Window.speed

                url = f"http://{arduino_as_dict["ip_address"]}/{Window.command}?r={r}&g={g}&b={b}&br={brightness}&d={speed}"
                Window.last_command = url

                for i in self._manager.devices:
                    if i == self.device_map[self.option_menu.get()]:
                        i._last_command = url.replace(
                            f"http://{arduino_as_dict["ip_address"]}", ""
                        )

                self._manager._save_to_file(self._manager.devices)

                self.post(url)

    def post(self, url: str) -> None:
        print(url)
        try:
            response = requests.post(url)

            if response.status_code in (200, 204):
                print(response.text)
                return

            print(f"FAIL: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"connection failure: {e}")

    def initScanTab(self) -> ctk.CTkFrame:
        # return DeviceTab(
        # self.midFrame, self._manager, self._build_device_map, self.option_menu
        # )
        return ctk.CTkFrame(self.midFrame)

    def initColorTab(self) -> ctk.CTkFrame:
        return ColorTab(self.midFrame)

    def initAnimationTab(self) -> AnimationTab:
        return AnimationTab(self.midFrame, self._color_tab)

    def option_change(self, option):
        if isinstance(self.current_tab, SingleLedTab):
            self.current_tab.draw_leds(
                self.device_map[self.option_menu.get()].to_dict()
            )

    def initSingeLEDTab(self) -> ctk.CTkLabel:
        return SingleLedTab(
            self.midFrame,
            (
                self.device_map[self.option_menu.get()].to_dict()
                if self.option_menu.get() in self.device_map
                else None
            ),
        )

    def getNumLEDs(self) -> int:
        if self.option_menu.get() in self.device_map.keys():
            arduino_as_dict = self.device_map[self.option_menu.get()].to_dict()
            try:
                response = requests.get(
                    f"http://{arduino_as_dict["ip_address"]}/ledNum"
                )

                if response.status_code in (200, 204):
                    return int(response.text)

                print(f"FAIL: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"connection failure: {e}")

    def setCommand(self, command: str) -> None:
        Window.command = command
