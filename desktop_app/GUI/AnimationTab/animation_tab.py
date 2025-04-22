import random
import customtkinter as ctk

from GUI.AnimationTab.animation_canvas import AnimationCanvas
from GUI.AnimationTab.animation_display import AnimationDisplay
from GUI.ColorTab.color_tab import ColorTab


class AnimationTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(self, master, color_tab: ColorTab, *args, **kwargs) -> None:
        super().__init__(master=master, *args, **kwargs)
        self._color_tab = color_tab

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        buttons = [
            ("🌈 Rainbow", self._rainbow),
            ("💓 Pulse", self._pulsing_light),
            ("🚀 Chasing light", self._chaising_light),
            ("⚡ Strobe", self._strobe),
            ("🌧️ Raindrop", self._raindrop),
            ("🔥 Fireplace", self._fireplace),
        ]

        self._animation_canvas = AnimationCanvas(self, buttons)
        self._animation_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self._animation_display = AnimationDisplay(
            self, self._color_tab.color_picker_rgb
        )
        self._animation_display.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self._led_display = self._animation_display.led_display

    def _convert_rgb_to_hex(self, rgb) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _rainbow(self) -> None:
        colors = [
            (255, 0, 0),  # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (75, 0, 130),  # Indigo
            (139, 0, 255),  # Violet
        ]
        index = 0

        def animation() -> None:
            nonlocal index
            if not self._led_display._is_animation_running:
                return

            brightness = self._animation_display.brightness_slider_value

            for i, led in enumerate(self._led_display.leds):
                color_idx = (index + i) % len(colors)
                r = max(0, min(int(colors[color_idx][0] * brightness / 255), 255))
                g = max(0, min(int(colors[color_idx][1] * brightness / 255), 255))
                b = max(0, min(int(colors[color_idx][2] * brightness / 255), 255))

                hex_color = self._convert_rgb_to_hex((r, g, b))
                led.configure(fg_color=hex_color)

            index = (index + 1) % len(colors)
            self._led_display.set_animation_task(
                self.after(
                    int(self._animation_display.animation_speed_slider_value),
                    animation,
                )
            )

        self._led_display.start_animation(animation_function=animation)

    def _pulsing_light(self) -> None:
        base_r, base_g, base_b = self._color_tab.color_picker_rgb.rgb
        max_brightness = self._animation_display.brightness_slider_value

        min_brightness = 50
        step = 20

        if max_brightness < min_brightness:
            max_brightness = min_brightness

        up_levels = list(range(min_brightness, int(max_brightness), step))
        down_levels = list(range(int(max_brightness), min_brightness, -step))

        if not up_levels:
            up_levels = [min_brightness]
        if not down_levels or down_levels == up_levels:
            down_levels = []

        brightness_levels = up_levels + down_levels

        color_values = []
        for brightness in brightness_levels:
            # Scale RGB values according to their base values and current brightness
            r = min(255, int(base_r * brightness / 255))
            g = min(255, int(base_g * brightness / 255))
            b = min(255, int(base_b * brightness / 255))
            color_values.append(self._convert_rgb_to_hex((r, g, b)))

        if not color_values:
            color_values = [self._convert_rgb_to_hex((0, 0, 0))]

        index = 0

        def animation() -> None:
            nonlocal index

            if not self._led_display._is_animation_running:
                return

            if color_values and index < len(color_values):
                current_color = color_values[index]
                for led in self._led_display.leds:
                    if led.winfo_exists():
                        led.configure(fg_color=current_color)

            index = (index + 1) % len(color_values)

            self._led_display.set_animation_task(
                self.after(
                    int(self._animation_display.animation_speed_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _chaising_light(self) -> None:
        index = 0

        def animation() -> None:
            nonlocal index
            if not self._led_display._is_animation_running:
                return

            self._led_display._reset_LEDs()
            if self._led_display.leds[index].winfo_exists():
                self._led_display.leds[index].configure(
                    fg_color=self._convert_rgb_to_hex(
                        self._color_tab.color_picker_rgb.rgb
                    )
                )

            index = (index + 1) % len(self._led_display.leds)
            self._led_display.set_animation_task(
                self.after(
                    int(self._animation_display.animation_speed_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _strobe(self) -> None:
        colors = [
            self._convert_rgb_to_hex(self._color_tab.color_picker_rgb.rgb),
            "#000000",
        ]
        index = 0

        def animation() -> None:
            nonlocal index

            if not self._led_display._is_animation_running:
                return

            self._led_display._reset_LEDs()

            colors[0] = self._convert_rgb_to_hex(self._color_tab.color_picker_rgb.rgb)

            for led in self._led_display.leds:
                if led.winfo_exists():
                    led.configure(fg_color=colors[index])

            index = 1 - index

            self._led_display.set_animation_task(
                self.after(
                    int(self._animation_display.animation_speed_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _raindrop(self) -> None:
        def animation() -> None:
            if not self._led_display._is_animation_running:
                return

            self._led_display._reset_LEDs()
            led = random.choice(self._led_display.leds)
            if led.winfo_exists():
                led.configure(
                    fg_color=self._convert_rgb_to_hex(
                        self._color_tab.color_picker_rgb.rgb
                    )
                )

            self.after(
                int(self._animation_display.animation_speed_slider_value) + 200,
                lambda led=led: (
                    led.configure(fg_color="black") if led.winfo_exists() else None
                ),
            )
            self._led_display.set_animation_task(
                self.after(random.randint(100, 500), animation)
            )

        self._led_display.start_animation(animation)

    def _fireplace(self) -> None:
        pass

    @property
    def animation_display(self) -> AnimationDisplay:
        return self._animation_display
