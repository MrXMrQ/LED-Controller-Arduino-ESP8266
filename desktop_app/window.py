import random
from turtle import color
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

    r_value = 255
    g_value = 0
    b_value = 255
    brightness = 255
    speed = 50

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

        self.running = False
        self.animation_task = None

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
            height=50,
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
        print(
            Window.r_value,
            Window.g_value,
            Window.b_value,
            Window.brightness,
            Window.speed,
        )

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
        def temp():
            pass

        frame = ctk.CTkFrame(self.midFrame, height=50)
        frame.grid_rowconfigure((0, 1), weight=1)
        frame.grid_columnconfigure(0, weight=1)

        topFrame = ctk.CTkFrame(frame, corner_radius=15, fg_color="Blue")
        topFrame.grid(row=0, column=0, padx=15, sticky="nsew")

        topFrame.grid_rowconfigure((0, 1), weight=1)
        topFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        scanButton = ctk.CTkButton(
            topFrame, text="SCAN", command=temp, **Window.button_options
        )
        scanButton.grid(row=1, column=1, columnspan=2, sticky="ew", pady=10)

        scan_entry = ctk.CTkEntry(topFrame)
        scan_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=10)
        scan_entry.bind("<Return>", temp)

        s = ctk.CTkButton(
            topFrame, text="search", command=temp, **Window.button_options
        )
        s.grid(row=0, column=2, sticky="ew", pady=10)

        botFrame = ctk.CTkFrame(frame, corner_radius=15, fg_color="Yellow")
        botFrame.grid(row=1, column=0, padx=15)

        return frame

    def initColorTab(self) -> ctk.CTkFrame:
        def update(r, g, b) -> None:
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

        def update_from_hex(event) -> None:
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

        def update_from_rgb(event) -> None:
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

        frame = ctk.CTkFrame(self.midFrame, height=50)
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
        r_slider.set(Window.r_value)
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
        g_slider.set(Window.g_value)
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
        b_slider.set(Window.b_value)
        b_slider.configure(fg_color="blue")

        b_label = ctk.CTkLabel(leftTopFrame, text="B", text_color="blue")
        b_label.grid(row=2, column=1, padx=10, pady=10)

        r_entry = ctk.CTkEntry(leftTopFrame)
        r_entry.grid(row=0, column=2, padx=10, pady=10)
        r_entry.insert(int(r_slider.get()), str(int(r_slider.get())))
        r_entry.bind("<Return>", update_from_rgb)

        g_entry = ctk.CTkEntry(leftTopFrame)
        g_entry.grid(row=1, column=2, padx=10, pady=10)
        g_entry.insert(int(g_slider.get()), str(int(g_slider.get())))
        g_entry.bind("<Return>", update_from_rgb)

        b_entry = ctk.CTkEntry(leftTopFrame)
        b_entry.grid(row=2, column=2, padx=10, pady=10)
        b_entry.insert(int(b_slider.get()), str(int(b_slider.get())))
        b_entry.bind("<Return>", update_from_rgb)

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
        hex_entry.bind("<Return>", update_from_hex)

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
        brightness_slider.set(Window.brightness)

        night_label = ctk.CTkLabel(
            rightBotFrame, text="🌑", text_color="white", font=("inter", 20, "bold")
        )
        night_label.grid(row=0, column=0, padx=10, pady=10)

        return frame

    def initAnimationTab(self) -> ctk.CTkFrame:
        def start_animation(animation_function) -> None:
            self.running = False
            if self.animation_task:
                self.after_cancel(self.animation_task)
            reset_leds()
            self.running = True
            animation_function()

        def reset_leds() -> None:
            for led in leds:
                if led.winfo_exists() and led.winfo_ismapped():
                    led.configure(led, fg_color="black")

        def adjust_brightness(rgb: tuple, brightness) -> None:
            factor = brightness / 255

            new_r = int(rgb[0] * factor)
            new_g = int(rgb[1] * factor)
            new_b = int(rgb[2] * factor)

            new_r = max(0, min(new_r, 255))
            new_g = max(0, min(new_g, 255))
            new_b = max(0, min(new_b, 255))

            return f"#{new_r:02x}{new_g:02x}{new_b:02x}"

        def generate_similar_colors(base_color, num_colors=4) -> list:
            r, g, b = [int(base_color[i : i + 2], 16) for i in range(1, 7, 2)]
            colors = []
            colors.append(base_color)

            step = 255 // num_colors

            for i in range(-num_colors // 2, num_colors // 2 + 1):

                new_r = max(0, min(255, r + i * step))
                new_g = max(0, min(255, g + i * step))
                new_b = max(0, min(255, b + i * step))

                colors.append(f"#{new_r:02x}{new_g:02x}{new_b:02x}")

            return colors

        def start_rainbow_wave() -> None:
            colors = [
                (255, 0, 0),
                (255, 127, 0),
                (255, 255, 0),
                (0, 255, 0),
                (0, 0, 255),
                (75, 0, 130),
                (139, 0, 255),
            ]

            index = 0

            def animate() -> None:
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

        def start_pulsing_light() -> None:
            brightness_levels = [
                f"#FF{hex(i)[2:]:0>2}{hex(i)[2:]:0>2}" for i in range(50, 255, 20)
            ] + [f"#FF{hex(i)[2:]:0>2}{hex(i)[2:]:0>2}" for i in range(255, 50, -20)]

            index = 0

            def animate() -> None:
                nonlocal index
                if not self.running:
                    return
                for led in leds:
                    if led.winfo_exists():
                        led.configure(fg_color=brightness_levels[index])
                index = (index + 1) % len(brightness_levels)
                self.animation_task = self.after(int(Window.speed), animate)

            start_animation(animate)

        def start_chasing_light() -> None:
            index = 0

            def animate() -> None:
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

        def start_strobe() -> None:
            colors = [
                adjust_brightness(
                    (Window.r_value, Window.g_value, Window.b_value), Window.brightness
                ),
                "#000000",
            ]
            index = 0

            def animate() -> None:
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

        def start_raindrop() -> None:
            def animate() -> None:
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
                    int(Window.speed) + 200, lambda: led.configure(fg_color="black")
                )
                self.animation_task = self.after(random.randint(100, 500), animate)

            start_animation(animate)

        def start_fireplace() -> None:
            base_color = adjust_brightness(
                (Window.r_value, Window.g_value, Window.b_value),
                Window.brightness,
            )
            colors = generate_similar_colors(base_color, 6)

            def animate() -> None:
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
                        int(Window.speed), lambda: led.configure(fg_color="black")
                    )
                self.animation_task = self.after(random.randint(100, 400), animate)

            start_animation(animate)

        def update_brightness() -> None:
            Window.brightness = brightness_slider.get()

            if self.running:
                pass

        def update_speed() -> None:
            Window.speed = speedSlider.get()

        def on_mousewheel(event) -> None:
            if canvas.winfo_exists() and canvas.winfo_ismapped():
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def resizeButton(event) -> None:
            canvas.itemconfigure(
                window, width=event.width - scrollbar.winfo_width() - 60
            )

        frame = ctk.CTkFrame(self.midFrame, height=50)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

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

        content_frame = ctk.CTkFrame(canvas)
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        buttons = [
            ("🌈 Rainbow Wave", start_rainbow_wave),
            ("💓 Pulsing Light", start_pulsing_light),
            ("🚀 Chasing Light", start_chasing_light),
            ("⚡ Strobe", start_strobe),
            ("🌧️ Raindrop", start_raindrop),
            ("🔥 Fireplace", start_fireplace),
        ]

        self.animationButtons = []

        for text, command in buttons:
            btn = ctk.CTkButton(
                content_frame, text=text, command=command, **Window.button_options
            )
            btn.pack(fill="x", padx=5, pady=5)
            self.animationButtons.append(btn)

        for btn in content_frame.winfo_children():
            btn.configure(width=content_frame.winfo_width())

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        leftFrame.bind("<Configure>", resizeButton)

        canvas.pack(side="right", fill="both", expand=True, pady=10, padx=20)
        scrollbar.pack(side="right", fill="y", pady=15, padx=5)

        rightFrame = ctk.CTkFrame(
            frame, width=500, border_color="black", border_width=5, corner_radius=15
        )
        rightFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        rightFrame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        rightFrame.grid_columnconfigure(0, weight=1)

        topFrame = ctk.CTkFrame(
            rightFrame,
            border_color="black",
            border_width=5,
        )
        topFrame.grid(row=0, rowspan=2, column=0, padx=15, pady=15)
        rightFrame.grid_rowconfigure(1, weight=1)
        rightFrame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

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

    def initSingeLEDTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="4")
