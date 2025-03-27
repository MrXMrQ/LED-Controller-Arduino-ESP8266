import customtkinter as ctk
from ipScanner import IPScanner
import requests


class Window(ctk.CTk):
    url = "http://"
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

    r_value = 127
    g_value = 127
    b_value = 127
    brightness = 255

    def __init__(
        self, title: str, width: int, height: int, maxWidth: int, maxHeight: int
    ):
        super().__init__()

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.maxsize(maxWidth, maxHeight)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=4)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.midFrame = self.initMidFrame()
        self.midFrame.grid(row=1, column=0, sticky="nsew", padx=20, pady=3)

        self.topFrame = self.initTopFrame()
        self.topFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=3)

        self.botFrame = self.initBotFrame()
        self.botFrame.grid(row=2, column=0, sticky="nsew", padx=20, pady=3)

        self.current_tab = self.initScanTab()
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initTopFrame(self) -> ctk.CTkFrame:
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

        label = ctk.CTkLabel(
            topFrame, text="LED-Controller", font=("Inter", 30, "bold")
        )
        label.grid(row=0, column=0, columnspan=4, pady=5)

        button_data = [
            ("SCAN", lambda: self.loadTab(self.initScanTab())),
            ("COLOR", lambda: self.loadTab(self.initColorTab())),
            ("ANIMATION", lambda: self.loadTab(self.initAnimationTab())),
            ("SINGLE LED", lambda: self.loadTab(self.initSingeLEDTab())),
        ]

        for col, (text, command) in enumerate(button_data):
            btn = ctk.CTkButton(
                topFrame,
                text=text,
                command=command,
                **Window.button_options,
            )
            btn.grid(row=1, column=col, pady=5, padx=10, sticky="ew")

        return topFrame

    def loadTab(self, tab) -> None:
        self.current_tab.destroy()
        self.current_tab = tab
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initMidFrame(self) -> ctk.CTkFrame:
        middleFrame = ctk.CTkFrame(
            master=self,
            height=40,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        return middleFrame

    def initBotFrame(self) -> ctk.CTkFrame:
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

        options = [""]  # self.fillOptions()
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
        )
        self.option_menu.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

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

    def ledOnButtonClick(self) -> None:
        print("LED ON")

    def ledOffButtonClick(self) -> None:
        if self.option_menu.get() == "":
            return

        print(f"{Window.url}{self.option_menu.get()}/ledOff")

        requests.post(f"{Window.url}{self.option_menu.get()}/ledOff")

    def pushButtonClick(self) -> None:
        print(Window.r_value, Window.g_value, Window.b_value, Window.brightness)

        if self.option_menu.get() == "":
            print("Unable to push")
            return

        print(self.option_menu.get())

    def fillOptions(self) -> list:
        ips = IPScanner()
        devices = ips.get_devices()

        if devices == []:
            return [""]

        return devices

    def initScanTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            self.midFrame,
            text="1",
            fg_color="gray",
            corner_radius=15,
        )

    def initColorTab(self) -> ctk.CTkLabel:
        def update(r, g, b):
            Window.r_value = int(r)
            Window.g_value = int(g)
            Window.b_value = int(b)

        def update_color() -> None:
            r_value = r_slider.get()
            g_value = g_slider.get()
            b_value = b_slider.get()

            r_entry.delete(0, ctk.END)
            g_entry.delete(0, ctk.END)
            b_entry.delete(0, ctk.END)

            r_entry.insert(0, str(int(r_value)))
            g_entry.insert(0, str(int(g_value)))
            b_entry.insert(0, str(int(b_value)))

            update(r_value, g_value, b_value)

            hex_entry.delete(0, ctk.END)
            hex_entry.insert(
                0, f"#{int(r_value):02x}{int(g_value):02x}{int(b_value):02x}"
            )

            colorDisplay.configure(
                require_redraw=True,
                fg_color=f"#{int(r_value):02x}{int(g_value):02x}{int(b_value):02x}",
            )

        def update_brightness():
            Window.brightness = int(brightness_slider.get())

        def update_from_hex() -> None:
            hex_value = hex_entry.get()

            if len(hex_value) == 7 and hex_value[0] == "#":
                try:
                    r_value, g_value, b_value = [
                        int(hex_value[i : i + 2], 16) for i in range(1, 7, 2)
                    ]

                    r_slider.set(r_value)
                    g_slider.set(g_value)
                    b_slider.set(b_value)

                    update(r_value, g_value, b_value)

                    r_entry.delete(0, ctk.END)
                    g_entry.delete(0, ctk.END)
                    b_entry.delete(0, ctk.END)

                    r_entry.insert(0, str(int(r_value)))
                    g_entry.insert(0, str(int(g_value)))
                    b_entry.insert(0, str(int(b_value)))

                    colorDisplay.configure(require_redraw=True, fg_color=hex_value)

                except ValueError:
                    print("Unknown HEX value")
            else:
                print("Unknown HEX value")

        def update_from_rgb() -> None:
            try:
                r_value = int(r_entry.get())
                g_value = int(g_entry.get())
                b_value = int(b_entry.get())

                if 0 <= r_value <= 255 and 0 <= g_value <= 255 and 0 <= b_value <= 255:
                    r_slider.set(r_value)
                    g_slider.set(g_value)
                    b_slider.set(b_value)

                    update(r_value, g_value, b_value)

                    colorDisplay.configure(
                        require_redraw=True,
                        fg_color=f"#{r_value:02x}{g_value:02x}{b_value:02x}",
                    )

                    hex_entry.delete(0, ctk.END)
                    hex_entry.insert(0, f"#{r_value:02x}{g_value:02x}{b_value:02x}")
                else:
                    print("RGB value between 0 - 255")
            except ValueError:
                print("Unknown RGB value")

        frame = ctk.CTkFrame(self.midFrame)
        frame.grid_rowconfigure((0, 1), weight=1)
        frame.grid_columnconfigure((0, 1), weight=1)

        leftTopFrame = ctk.CTkFrame(master=frame, border_color="black", border_width=4)
        leftTopFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        leftTopFrame.grid_columnconfigure((0, 1, 2), weight=1)
        leftTopFrame.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        r_slider = ctk.CTkSlider(
            leftTopFrame,
            from_=0,
            to=255,
            number_of_steps=256,
            command=lambda x: update_color(),
        )
        r_slider.grid(row=0, column=0, padx=10, pady=10)
        r_slider.set(255 / 2)
        r_slider.configure(fg_color="red")

        r_label = ctk.CTkLabel(leftTopFrame, text="R", text_color="red")
        r_label.grid(row=0, column=1, padx=10, pady=10)

        g_slider = ctk.CTkSlider(
            leftTopFrame,
            from_=0,
            to=255,
            number_of_steps=256,
            command=lambda x: update_color(),
        )
        g_slider.grid(row=1, column=0, padx=10, pady=10)
        g_slider.set(255 / 2)
        g_slider.configure(fg_color="green")

        g_label = ctk.CTkLabel(leftTopFrame, text="G", text_color="green")
        g_label.grid(row=1, column=1, padx=10, pady=10)

        b_slider = ctk.CTkSlider(
            leftTopFrame,
            from_=0,
            to=255,
            number_of_steps=256,
            command=lambda x: update_color(),
        )
        b_slider.grid(row=2, column=0, padx=10, pady=10)
        b_slider.set(255 / 2)
        b_slider.configure(fg_color="blue")

        b_label = ctk.CTkLabel(leftTopFrame, text="B", text_color="blue")
        b_label.grid(row=2, column=1, padx=10, pady=10)

        r_entry = ctk.CTkEntry(leftTopFrame)
        r_entry.grid(row=0, column=2, padx=10, pady=10)
        r_entry.insert(int(r_slider.get()), str(int(r_slider.get())))

        g_entry = ctk.CTkEntry(leftTopFrame)
        g_entry.grid(row=1, column=2, padx=10, pady=10)
        g_entry.insert(int(g_slider.get()), str(int(g_slider.get())))

        b_entry = ctk.CTkEntry(leftTopFrame)
        b_entry.grid(row=2, column=2, padx=10, pady=10)
        b_entry.insert(int(b_slider.get()), str(int(b_slider.get())))

        rgb_button = ctk.CTkButton(
            leftTopFrame,
            text="RGB Eingabe",
            command=update_from_rgb,
            **Window.button_options,
        )
        rgb_button.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        leftBotFrame = ctk.CTkFrame(master=frame, border_color="black", border_width=4)
        leftBotFrame.grid_rowconfigure((0, 1), weight=1)
        leftBotFrame.grid_columnconfigure(0, weight=1)
        leftBotFrame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        hex_entry = ctk.CTkEntry(leftBotFrame, height=50)
        hex_entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        hex_entry.insert(
            0,
            f"#{int(int(r_entry.get())):02x}{int(int(g_entry.get())):02x}{int(int(b_entry.get())):02x}",
        )

        hex_button = ctk.CTkButton(
            leftBotFrame, text="HEX", command=update_from_hex, **Window.button_options
        )
        hex_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        rightFrame = ctk.CTkFrame(master=frame, border_width=4, border_color="black")
        rightFrame.grid_rowconfigure((0, 1), weight=1)
        rightFrame.grid_columnconfigure(0, weight=1)
        rightFrame.grid(row=0, rowspan=2, column=1, sticky="nsew", padx=10, pady=10)

        colorDisplay = ctk.CTkFrame(
            master=rightFrame,
            fg_color=f"#{int(r_slider.get()):02x}{int(g_slider.get()):02x}{int(b_slider.get()):02x}",
            border_color="black",
            border_width=4,
        )
        colorDisplay.grid_rowconfigure((0, 1), weight=1)
        colorDisplay.grid_columnconfigure(0, weight=1)
        colorDisplay.grid(row=0, column=0)

        rightBotFrame = ctk.CTkFrame(
            master=rightFrame, border_width=4, border_color="black"
        )
        rightBotFrame.grid_rowconfigure(0, weight=1)
        rightBotFrame.grid_columnconfigure((0, 1, 2), weight=1)
        rightBotFrame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        sun_label = ctk.CTkLabel(
            rightBotFrame, text="☀️", text_color="white", font=("inter", 20, "bold")
        )
        sun_label.grid(row=0, column=2, padx=10, pady=10)

        brightness_slider = ctk.CTkSlider(
            rightBotFrame,
            from_=0,
            to=255,
            number_of_steps=256,
            command=lambda x: update_brightness(),
        )
        brightness_slider.grid(row=0, column=1)
        brightness_slider.set(255 / 2)

        night_label = ctk.CTkLabel(
            rightBotFrame, text="🌑", text_color="white", font=("inter", 20, "bold")
        )
        night_label.grid(row=0, column=0, padx=10, pady=10)

        return frame

    def initAnimationTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="3")

    def initSingeLEDTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="4")
