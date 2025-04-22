import random
import customtkinter as ctk
from arduinoManager import ArduinoManager
import requests

from GUI.ColorTab.color_tab import ColorTab
from GUI.AnimationTab.animation_tab import AnimationTab
from GUI.single_led_tab import SingleLedTab
from GUI.device_tab import DeviceTab


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

        if isinstance(tab, DeviceTab):
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
        return DeviceTab(
            self.midFrame, self._manager, self._build_device_map, self.option_menu
        )

    def initColorTab(self) -> ctk.CTkFrame:
        return ColorTab(self.midFrame)

    def initAnimationTab(self) -> AnimationTab:
        return AnimationTab(self.midFrame, self._color_tab)

        def start_animation(animation_function):
            """Start a new animation sequence"""
            self.running = False
            if self.animation_task and led.winfo_exists():
                self.after_cancel(self.animation_task)
            reset_leds()
            self.running = True
            animation_function()

        def reset_leds():
            """Reset all LEDs to off state"""
            for led in leds:
                if led.winfo_exists() and led.winfo_ismapped():
                    led.configure(fg_color="black")

        def adjust_brightness(rgb, brightness):
            """Adjust color based on brightness"""
            factor = brightness / 255

            new_r = int(rgb[0] * factor)
            new_g = int(rgb[1] * factor)
            new_b = int(rgb[2] * factor)

            new_r = max(0, min(new_r, 255))
            new_g = max(0, min(new_g, 255))
            new_b = max(0, min(new_b, 255))

            return f"#{new_r:02x}{new_g:02x}{new_b:02x}"

        def generate_similar_colors(base_color, num_colors=4):
            """Generate similar colors for effects"""
            r, g, b = [int(base_color[i : i + 2], 16) for i in range(1, 7, 2)]
            colors = [base_color]

            step = 255 // num_colors

            for i in range(-num_colors // 2, num_colors // 2 + 1):
                new_r = max(0, min(255, r + i * step))
                new_g = max(0, min(255, g + i * step))
                new_b = max(0, min(255, b + i * step))

                colors.append(f"#{new_r:02x}{new_g:02x}{new_b:02x}")

            return colors

        # Animation functions
        def start_rainbow_wave():
            """Rainbow wave animation"""
            colors = [
                (255, 0, 0),
                (255, 127, 0),
                (255, 255, 0),
                (0, 255, 0),
                (0, 0, 255),
                (75, 0, 130),
                (139, 0, 255),
            ]

            Window.command = "rainbow"

            index = 0

            def animate():
                nonlocal index
                if not self.running:
                    return
                for i, led in enumerate(leds):
                    if led.winfo_exists():
                        led.configure(
                            fg_color=adjust_brightness(
                                colors[(index + i) % len(colors)], Window.brightness
                            )
                        )
                index = (index + 1) % len(colors)
                self.animation_task = self.after(int(Window.speed), animate)

            start_animation(animate)

        def start_pulsing_light():
            """Pulsing light animation with configurable color and brightness"""
            # Get base RGB values from the class
            base_r, base_g, base_b = Window.r_value, Window.g_value, Window.b_value
            max_brightness = Window.brightness
            Window.command = "pulse"

            # Calculate brightness steps
            min_brightness = 50  # Minimum brightness level
            step = 20  # Step size for brightness changes

            if max_brightness < min_brightness:
                max_brightness = min_brightness

            # Create brightness levels for pulsing up and down
            up_levels = list(range(min_brightness, int(max_brightness), step))
            down_levels = list(range(int(max_brightness), min_brightness, -step))

            if not up_levels:
                up_levels = [min_brightness]
            if not down_levels or down_levels == up_levels:
                down_levels = []

            brightness_levels = up_levels + down_levels

            # Generate color values for each brightness level
            color_values = []
            for brightness in brightness_levels:
                # Scale RGB values according to their base values and current brightness
                r = min(255, int(base_r * brightness / 255))
                g = min(255, int(base_g * brightness / 255))
                b = min(255, int(base_b * brightness / 255))
                color_values.append(
                    f"#{hex(r)[2:]:0>2}{hex(g)[2:]:0>2}{hex(b)[2:]:0>2}"
                )

            if not color_values:
                color_values = [f"#{hex(0)[2:]:0>2}{hex(0)[2:]:0>2}{hex(0)[2:]:0>2}"]

            index = 0

            def animate():
                nonlocal index
                if not self.running:
                    return
                if color_values and index < len(color_values):
                    current_color = color_values[index]
                    for led in leds:
                        if led.winfo_exists():
                            led.configure(fg_color=current_color)

                index = (index + 1) % len(color_values)

                self.animation_task = self.after(int(Window.speed), animate)

            start_animation(animate)

        def start_chasing_light():
            """Chasing light animation"""
            index = 0

            Window.command = "chasing"

            def animate():
                nonlocal index
                if not self.running:
                    return
                reset_leds()
                if leds[index].winfo_exists():
                    leds[index].configure(
                        fg_color=adjust_brightness(
                            (Window.r_value, Window.g_value, Window.b_value),
                            Window.brightness,
                        )
                    )
                index = (index + 1) % len(leds)
                self.animation_task = self.after(int(Window.speed), animate)

            start_animation(animate)

        def start_strobe():
            """Strobe light animation"""
            colors = [
                adjust_brightness(
                    (Window.r_value, Window.g_value, Window.b_value), Window.brightness
                ),
                "#000000",
            ]
            index = 0

            Window.command = "strobe"

            def animate():
                nonlocal index
                if not self.running:
                    return
                reset_leds()

                colors[0] = adjust_brightness(
                    (Window.r_value, Window.g_value, Window.b_value), Window.brightness
                )

                for led in leds:
                    if led.winfo_exists():
                        led.configure(fg_color=colors[index])
                index = 1 - index
                self.animation_task = self.after(int(Window.speed), animate)

            start_animation(animate)

        def start_raindrop():
            """Raindrop animation"""

            Window.command = "raindrop"

            def animate():
                if not self.running:
                    return

                reset_leds()
                led = random.choice(leds)
                if led.winfo_exists():
                    led.configure(
                        fg_color=adjust_brightness(
                            (Window.r_value, Window.g_value, Window.b_value),
                            Window.brightness,
                        )
                    )
                self.after(
                    int(Window.speed) + 200,
                    lambda led=led: (
                        led.configure(fg_color="black") if led.winfo_exists() else None
                    ),
                )
                self.animation_task = self.after(random.randint(100, 500), animate)

            start_animation(animate)

        def start_fireplace():
            """Fireplace animation"""

            Window.command = "fireplace"

            def animate():
                if not self.running:
                    return
                reset_leds()
                led = random.choice(leds)
                if led.winfo_exists() and led.winfo_ismapped():
                    base_color = adjust_brightness(
                        (Window.r_value, Window.g_value, Window.b_value),
                        Window.brightness,
                    )
                    colors = generate_similar_colors(base_color, 6)

                    led.configure(fg_color=random.choice(colors))
                    self.after(
                        int(Window.speed),
                        lambda led=led: (
                            led.configure(fg_color="black")
                            if led.winfo_exists()
                            else None
                        ),
                    )
                self.animation_task = self.after(random.randint(100, 400), animate)

            start_animation(animate)

        def update_brightness():
            """Update brightness value"""
            Window.brightness = brightness_slider.get()

        def update_speed():
            """Update animation speed"""
            Window.speed = speedSlider.get()

        def temp():
            pass

        def on_mousewheel(event):
            """Handle scrolling in animation list"""
            if canvas.winfo_exists() and canvas.winfo_ismapped():
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def resizeButton(event):
            """Resize the animation buttons canvas"""
            canvas.itemconfigure(
                window, width=event.width - scrollbar.winfo_width() - 60
            )

        frame = ctk.CTkFrame(self.midFrame)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure((0, 1), weight=1)

        # Animation selection list
        leftFrame = ctk.CTkFrame(
            frame,
            corner_radius=15,
            fg_color="gray20",
            border_color="black",
            border_width=5,
        )
        leftFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        canvas = ctk.CTkCanvas(
            leftFrame, highlightthickness=0, bg=leftFrame.cget("fg_color")
        )
        scrollbar = ctk.CTkScrollbar(
            leftFrame, orientation="vertical", command=canvas.yview
        )

        content_frame = ctk.CTkFrame(canvas, fg_color=leftFrame.cget("fg_color"))
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Animation buttons
        buttons = [
            ("🌈 Rainbow Wave", start_rainbow_wave),
            ("💓 Pulsing Light", start_pulsing_light),
            ("🚀 Chasing Light", start_chasing_light),
            ("⚡ Strobe", start_strobe),
            ("🌧️ Raindrop", start_raindrop),
            ("🔥 Fireplace", start_fireplace),
            ("1", temp),
            ("2", temp),
            ("3", temp),
            ("4", temp),
            ("5", temp),
        ]

        self.animationButtons = []

        for text, command in buttons:
            btn = ctk.CTkButton(
                content_frame, text=text, command=command, **Window.button_options
            )
            btn.pack(fill="x", padx=5, pady=5)
            self.animationButtons.append(btn)

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        leftFrame.bind("<Configure>", resizeButton)

        canvas.pack(side="right", fill="both", expand=True, pady=10, padx=20)
        scrollbar.pack(side="left", fill="y", pady=15, padx=5)

        # Preview and controls panel
        rightFrame = ctk.CTkFrame(
            frame, border_color="black", border_width=5, corner_radius=15
        )
        rightFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        rightFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        rightFrame.grid_columnconfigure(0, weight=1)

        # LED preview
        topFrame = ctk.CTkFrame(
            rightFrame,
            border_color="black",
            border_width=5,
        )
        topFrame.grid(row=0, rowspan=2, column=0, padx=15, pady=15, sticky="nsew")
        topFrame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        leds = []
        for i in range(5):
            led = ctk.CTkFrame(
                topFrame,
                border_color="black",
                fg_color="black",
                border_width=5,
                width=50,
                height=50,
                corner_radius=15,
            )
            led.grid(row=0, column=i, padx=10, pady=10)
            leds.append(led)

        botFrame = ctk.CTkFrame(rightFrame, border_color="black", border_width=5)
        botFrame.grid_rowconfigure((0, 1), weight=1)
        botFrame.grid_columnconfigure((0, 1, 2), weight=1)
        botFrame.grid(row=3, column=0, padx=15, pady=15)

        sun_label = ctk.CTkLabel(
            botFrame, text="☀️", text_color="white", font=("inter", 20, "bold")
        )
        sun_label.grid(row=0, column=2, padx=10, pady=10)

        brightness_slider = ctk.CTkSlider(
            botFrame,
            from_=0,
            to=255,
            number_of_steps=256,
            command=lambda x: update_brightness(),
        )
        brightness_slider.grid(row=0, column=1)
        brightness_slider.set(Window.brightness)

        night_label = ctk.CTkLabel(
            botFrame, text="🌑", text_color="white", font=("inter", 20, "bold")
        )
        night_label.grid(row=0, column=0, padx=10, pady=10)

        speedUp = ctk.CTkLabel(
            botFrame, text="⏫", text_color="white", font=("inter", 20, "bold")
        )
        speedUp.grid(row=1, column=2, padx=10, pady=10)

        speedSlider = ctk.CTkSlider(
            botFrame,
            from_=1,
            to=100,
            number_of_steps=99,
            command=lambda x: update_speed(),
        )

        speedSlider.grid(row=1, column=1)
        speedSlider.set(Window.speed)

        speedDown = ctk.CTkLabel(
            botFrame, text="⏬", text_color="white", font=("inter", 20, "bold")
        )
        speedDown.grid(row=1, column=0, padx=10, pady=10)

        return frame

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
