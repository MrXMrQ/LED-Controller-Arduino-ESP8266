import customtkinter as ctk
import requests
import ast
from typing import Dict, Tuple, Optional, Callable, Any

from arduino import Arduino


class SingleLedTab(ctk.CTkFrame):
    """Tab for controlling individual LED colors in an RGB LED strip."""

    led_index_to_frame = {}

    def __init__(self, master: Any, arduino: Dict[str, str], **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.arduino = arduino
        self._last_led = -1
        self._led_index_to_color = {}
        self._rgb_values = {"r": 0, "g": 0, "b": 0}
        self._brightness = 0

        self._updating = False

        self._create_left_frame()
        self._create_right_frame()

    def _create_left_frame(self) -> None:
        """Create the left frame with LED indicators"""
        self._leftFrame = self._create_bordered_frame(self)
        self._leftFrame.grid(row=0, column=0, pady=5, padx=10, sticky="nsew")

        self._canvas = ctk.CTkCanvas(
            self._leftFrame, highlightthickness=0, bg=self._leftFrame.cget("fg_color")
        )

        self._scrollbar = ctk.CTkScrollbar(
            self._leftFrame, orientation="vertical", command=self._canvas.yview
        )

        self._content_frame = ctk.CTkFrame(
            self._canvas, fg_color=self._leftFrame.cget("fg_color")
        )

        self._content_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._content_frame.grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1
        )

        self._window = self._canvas.create_window(
            (0, 0), window=self._content_frame, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.pack(side="right", fill="both", expand=True, pady=10, padx=10)
        self._scrollbar.pack(side="left", fill="y", pady=15, padx=5)

        self.draw_leds(self.arduino)

    def _create_right_frame(self) -> None:
        """Create the right frame with color controls"""
        self._rightFrame = self._create_bordered_frame(self)
        self._rightFrame.grid_rowconfigure((0, 1), weight=1)
        self._rightFrame.grid_columnconfigure(0, weight=1)
        self._rightFrame.grid(row=0, column=1, pady=5, padx=10, sticky="nsew")

        self._rightTopFrame = ctk.CTkFrame(
            master=self._rightFrame, border_color="black", border_width=4
        )
        self._rightTopFrame.grid_rowconfigure(0, weight=1)
        self._rightTopFrame.grid_columnconfigure(0, weight=1)
        self._rightTopFrame.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)

        self._colorDisplay = ctk.CTkFrame(
            master=self._rightTopFrame,
            fg_color="#000000",
            border_color="black",
            border_width=4,
            height=200,
            width=200,
        )
        self._colorDisplay.grid(row=0, column=0, padx=10, pady=10)

        self._rightBotFrame = ctk.CTkFrame(
            master=self._rightFrame, border_color="black", border_width=4
        )
        self._rightBotFrame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self._rightBotFrame.grid_columnconfigure((0, 1, 2), weight=1)
        self._rightBotFrame.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)

        self._create_rgb_controls()

    def _create_bordered_frame(self, master) -> ctk.CTkFrame:
        """Create a standard bordered frame with consistent styling"""
        return ctk.CTkFrame(
            master,
            fg_color="gray21",
            corner_radius=15,
            border_color="black",
            border_width=4,
        )

    def _create_rgb_controls(self) -> None:
        """Create RGB sliders, labels, entries and buttons"""
        colors = ["r", "g", "b"]
        color_names = {"r": "red", "g": "green", "b": "blue"}

        for i, color in enumerate(colors):
            slider = ctk.CTkSlider(
                self._rightBotFrame,
                from_=0,
                to=255,
                number_of_steps=256,
                command=lambda value, c=color: self._update_single_color(c, value),
                fg_color=color_names[color],
            )
            slider.grid(row=i, column=0, padx=10, pady=10)
            slider.set(self._rgb_values[color])
            setattr(self, f"_{color}_slider", slider)

            label = ctk.CTkLabel(
                self._rightBotFrame, text=color.upper(), text_color=color_names[color]
            )
            label.grid(row=i, column=1, padx=10, pady=10)

            entry = ctk.CTkEntry(self._rightBotFrame)
            entry.grid(row=i, column=2, padx=10, pady=10)
            entry.insert(0, "0")
            entry.bind("<Return>", self._update_from_rgb)
            setattr(self, f"_{color}_entry", entry)

        # Create brightness slider and label
        self._slider_br = ctk.CTkSlider(
            self._rightBotFrame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.update_brightness,
            fg_color="gray25",
        )
        self._slider_br.grid(row=3, column=0, padx=10, pady=10)
        self._slider_br.set(self._brightness)

        # Add brightness label
        br_label = ctk.CTkLabel(self._rightBotFrame, text="💡", text_color="white")
        br_label.grid(row=3, column=1, padx=10, pady=10)

        # Add brightness entry field
        self._br_entry = ctk.CTkEntry(self._rightBotFrame)
        self._br_entry.grid(row=3, column=2, padx=10, pady=10)
        self._br_entry.insert(0, str(self._brightness))
        self._br_entry.bind("<Return>", self._update_from_brightness_entry)

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

        rgb_button = ctk.CTkButton(
            self._rightBotFrame,
            text="Apply RGB",
            command=self._update_from_rgb,
            **button_options,
        )
        rgb_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    def draw_leds(self, arduino: Arduino) -> None:
        """Draw LED indicators in the content frame"""
        SingleLedTab.led_index_to_frame = {}
        self._led_index_to_color = {}

        if self._content_frame.winfo_children():
            for widget in self._content_frame.winfo_children():
                widget.destroy()

        num_leds = self._get_num_leds(arduino)
        if num_leds is None:
            return

        elements_per_line = 6
        row = 0

        for i in range(num_leds):
            if i % elements_per_line == 0:
                row += 1

            led = ctk.CTkFrame(
                self._content_frame,
                corner_radius=15,
                height=50,
                width=50,
                border_color="black",
                fg_color="black",
                border_width=4,
            )

            SingleLedTab.led_index_to_frame[i] = led
            led.bind("<Button-1>", lambda event, key=i: self._on_led_click(key))
            led.grid(row=row, column=i % elements_per_line, padx=7, pady=10)

        if "/singleLED" in arduino["last_command"]:
            singleLEDsetting = ast.literal_eval(
                arduino["last_command"].replace("/singleLED?singleLED=", "")
            )

            for i in singleLEDsetting:
                SingleLedTab.led_index_to_frame[i[0]].configure(
                    True, fg_color=f"#{i[1]:02x}{i[2]:02x}{i[3]:02x}"
                )

                self._led_index_to_color[i[0]] = (i[1], i[2], i[3], i[4])

    def _on_led_click(self, key: int) -> None:
        """Handle LED click events"""
        if self._last_led in SingleLedTab.led_index_to_frame:
            SingleLedTab.led_index_to_frame[self._last_led].configure(
                border_color="black"
            )

        SingleLedTab.led_index_to_frame[key].configure(border_color="gray25")
        self._last_led = key

        if key in self._led_index_to_color:
            r, g, b, brightness = self._led_index_to_color[key]
            self._update_ui_values(r, g, b, brightness)
        else:
            self._update_ui_values(0, 0, 0, 0)

    def _update_ui_values(
        self, r: int, g: int, b: int, brightness: float = None
    ) -> None:
        """Update UI elements with RGB values and optional brightness"""
        self._updating = True

        try:
            self._r_slider.set(r)
            self._g_slider.set(g)
            self._b_slider.set(b)

            for color, value in zip(["r", "g", "b"], [r, g, b]):
                entry = getattr(self, f"_{color}_entry")
                entry.delete(0, ctk.END)
                entry.insert(0, str(value))

            self._rgb_values["r"] = r
            self._rgb_values["g"] = g
            self._rgb_values["b"] = b

            if brightness is not None:
                self._brightness = brightness
                self._slider_br.set(brightness)
                self._br_entry.delete(0, ctk.END)
                self._br_entry.insert(0, str(int(brightness)))

            self._colorDisplay.configure(
                require_redraw=True, fg_color=f"#{r:02x}{g:02x}{b:02x}"
            )
        finally:
            self._updating = False

    def _on_mousewheel(self, event) -> None:
        """Handle scrolling in LED list"""
        if self._canvas.winfo_exists() and self._canvas.winfo_ismapped():
            self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _get_num_leds(self, arduino) -> Optional[int]:
        """Get the number of LEDs from the Arduino server"""
        if arduino is None:
            return 0

        try:
            response = requests.get(f"http://{arduino['ip_address']}/num")

            if response.status_code in (200, 204):
                return int(response.text)

            print(f"FAIL: {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Connection failure: {e}")
            return None

    def _update_single_color(self, color: str, value: float) -> None:
        """Update a single color value (R, G, or B)"""
        if self._updating:
            return

        int_value = int(value)

        r = self._rgb_values["r"]
        g = self._rgb_values["g"]
        b = self._rgb_values["b"]

        if color == "r":
            r = int_value
        elif color == "g":
            g = int_value
        elif color == "b":
            b = int_value

        entry = getattr(self, f"_{color}_entry")
        entry.delete(0, ctk.END)
        entry.insert(0, str(int_value))

        self._rgb_values[color] = int_value

        self._colorDisplay.configure(
            require_redraw=True, fg_color=f"#{r:02x}{g:02x}{b:02x}"
        )

        self._update_selected_led_color(r, g, b, self._brightness)

    def update_brightness(self, value: float) -> None:
        """Update brightness value and update the UI"""
        if self._updating:
            return

        brightness_value = int(value)
        self._brightness = brightness_value

        # Update brightness entry field
        self._br_entry.delete(0, ctk.END)
        self._br_entry.insert(0, str(brightness_value))

        # Update the selected LED if one is selected
        if self._last_led != -1:
            r = self._rgb_values["r"]
            g = self._rgb_values["g"]
            b = self._rgb_values["b"]
            self._update_selected_led_color(r, g, b, brightness_value)

    def _update_from_brightness_entry(self, event=None) -> None:
        """Update brightness from the entry field"""
        try:
            brightness_value = float(self._br_entry.get())
            brightness_value = max(0, min(100, brightness_value))  # Clamp to 0-100

            self._slider_br.set(brightness_value)
            self.update_brightness(brightness_value)
        except ValueError:
            print("Invalid brightness value. Please enter a number between 0-100.")
            # Reset to current value
            self._br_entry.delete(0, ctk.END)
            self._br_entry.insert(0, str(int(self._brightness)))

    def _update_from_rgb(self, event=None) -> None:
        """Update color from RGB input fields"""
        try:
            r_value = self._clamp_rgb_value(int(self._r_entry.get()))
            g_value = self._clamp_rgb_value(int(self._g_entry.get()))
            b_value = self._clamp_rgb_value(int(self._b_entry.get()))

            self._update_ui_values(r_value, g_value, b_value)

            self._update_selected_led_color(r_value, g_value, b_value, self._brightness)

        except ValueError:
            print("Invalid RGB values. Please enter numbers between 0-255.")

    def _clamp_rgb_value(self, value: int) -> int:
        """Clamp RGB value to 0-255 range"""
        return max(0, min(255, value))

    def _update_selected_led_color(
        self, r: int, g: int, b: int, brightness: float
    ) -> None:
        """Update the color of the selected LED"""
        if self._last_led != -1 and self._last_led in SingleLedTab.led_index_to_frame:
            SingleLedTab.led_index_to_frame[self._last_led].configure(
                fg_color=f"#{r:02x}{g:02x}{b:02x}"
            )

            # Store the color and brightness in the dictionary
            self._led_index_to_color[self._last_led] = (r, g, b, brightness)

            # Here you would typically also send this to the Arduino
            # For example: self._send_led_data(self._last_led, r, g, b, brightness)
