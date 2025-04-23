import requests
import customtkinter as ctk

from ArduinoBackend.arduino import Arduino
from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.Menus.options_menu import OptionsMenu


class SingleLEDDisplay(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self,
        master,
        options_menu: OptionsMenu,
        color_picker_rgb: ColorPickerRGB,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="gray20", *args, **kwargs)
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._options_menu = options_menu
        self._color_picker_rgb = color_picker_rgb
        self._elements_per_row = 7

        self._canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bg=self.cget("fg_color")
        )

        self._scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self._canvas.yview
        )
        self._scrollbar.pack(side="left", fill="y")

        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side="right", fill="both", expand=True)

        self._content_frame = ctk.CTkFrame(
            self._canvas, border_color="black", border_width=4
        )

        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._content_frame, anchor="nw"
        )

        self.draw_leds()

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<Configure>", self._on_frame_configure)

    def _on_frame_configure(self, event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def draw_leds(self) -> None:
        self._led_count = self._request_led_count()
        self._LEDS = []

        if self._content_frame.winfo_children():
            for widget in self._content_frame.winfo_children():
                widget.destroy()

        if self._led_count == 0:
            self._led = None
            return

        row = 0

        for i in range(self._led_count):
            if i % self._elements_per_row == 0:
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
            led.bind("<Button-1>", lambda event, led=led: self._on_click_led(led))
            led.bind("<MouseWheel>", self._on_mousewheel)
            led.grid(
                row=row,
                column=i % self._elements_per_row,
                padx=(SingleLEDDisplay._PADX + 5, 0),
                pady=SingleLEDDisplay._PADX,
            )
            self._LEDS.append(led)

        self._led = self._LEDS[0]

    def _on_click_led(self, led: ctk.CTkFrame) -> None:
        if self._led is not None:
            self._led.configure(True, border_color="black")

        led.configure(True, border_color="gray25")
        self._led = led
        self._color_picker_rgb.update_rgb_from_hex(
            "#000000" if self._led._fg_color == "black" else self._led._fg_color
        )

    def _request_led_count(self) -> None:
        if not self._options_menu.get() in self._options_menu.device_map:
            return 0

        arduino: Arduino = self._options_menu.device_map[self._options_menu.get()]

        if not arduino():
            return 0

        try:
            response = requests.get(f"http://{arduino.ip_address}/num")

            if response.status_code in (200, 204):
                return int(response.text)

            print(f"FAIL: {response.status_code}")
            return 0
        except requests.exceptions.RequestException as e:
            print(f"Connection failure: {e}")
            return 0

    def update_led_color(self, value) -> None:
        pass

    @property
    def led(self) -> ctk.CTkFrame:
        return self._led
