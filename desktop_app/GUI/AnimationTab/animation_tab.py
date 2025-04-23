import random
import customtkinter as ctk

from GUI.AnimationTab.animation_canvas import AnimationCanvas
from GUI.AnimationTab.animation_display import AnimationDisplay
from GUI.ColorTab.color_tab import ColorTab


class AnimationTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self, master, color_tab: ColorTab, top_menu_bar, *args, **kwargs
    ) -> None:
        super().__init__(master=master, *args, **kwargs)
        self._color_tab = color_tab
        self._top_menu_bar = top_menu_bar

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
        self._command = ""
        self._animation = None
        self._rgb = self._color_tab.color_picker_rgb.rgb
        self._delay = self.animation_display.animation_delay_slider_value

    def _convert_rgb_to_hex(self, rgb) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _rainbow(self) -> None:
        self._animation = "rainbow"
        self.create_command()
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
                    int(self._animation_display.animation_delay_slider_value),
                    animation,
                )
            )

        self._led_display.start_animation(animation_function=animation)

    def _pulsing_light(self) -> None:
        self._animation = "pulsing_light"
        self.create_command()

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
                    int(self._animation_display.animation_delay_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _chaising_light(self) -> None:
        self._animation = "chaising_light"
        self.create_command()
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
                    int(self._animation_display.animation_delay_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _strobe(self) -> None:
        self._animation = "stobe"
        self.create_command()
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
                    int(self._animation_display.animation_delay_slider_value), animation
                )
            )

        self._led_display.start_animation(animation)

    def _raindrop(self) -> None:
        self._animation = "raindrop"
        self.create_command()

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
                int(self._animation_display.animation_delay_slider_value) + 200,
                lambda led=led: (
                    led.configure(fg_color="black") if led.winfo_exists() else None
                ),
            )
            self._led_display.set_animation_task(
                self.after(random.randint(100, 500), animation)
            )

        self._led_display.start_animation(animation)

    def _fireplace(self) -> None:
        self._animation = "fireplace"
        self.create_command()

        def animate() -> None:
            if not self._led_display._is_animation_running:
                return

            num_active_leds = max(1, int(len(self._led_display.leds) * 0.3))
            active_leds = random.sample(self._led_display.leds, num_active_leds)

            base_color = self._color_tab.color_picker_rgb.rgb
            base_time = max(1, self._animation_display.animation_delay_slider_value)
            colors = self._generate_similar_colors(base_color, 8)

            for led in active_leds:
                if led.winfo_exists() and led.winfo_ismapped():
                    led.configure(fg_color=random.choice(colors))

                    base_time = max(
                        1, self._animation_display.animation_delay_slider_value
                    )
                    min_time = max(1, int(base_time * 0.5))
                    max_time = max(min_time + 1, int(base_time * 1.2))

                    flicker_time = random.randint(min_time, max_time)

                    r, g, b = base_color
                    dimmed_color = self._convert_rgb_to_hex(
                        (max(0, r // 3), max(0, g // 3), max(0, b // 3))
                    )

                    self.after(
                        flicker_time,
                        lambda led=led: (
                            led.configure(
                                fg_color=random.choice(
                                    [
                                        dimmed_color,
                                        "black",
                                    ]
                                )
                            )
                            if led.winfo_exists()
                            else None
                        ),
                    )

            next_frame_time = random.randint(30, max(31, int(base_time * 0.8)))
            self._led_display.set_animation_task(self.after(next_frame_time, animate))

        self._led_display.start_animation(animate)

    def _generate_similar_colors(self, base_color: tuple, num_colors: int = 4) -> None:
        """Generate similar colors for effects"""
        r, g, b = base_color
        colors = [self._convert_rgb_to_hex(base_color)]

        step = 255 // num_colors

        for i in range(-num_colors // 2, num_colors // 2 + 1):
            new_r = max(0, min(255, r + i * step))
            new_g = max(0, min(255, g + i * step))
            new_b = max(0, min(255, b + i * step))

            colors.append(self._convert_rgb_to_hex((new_r, new_g, new_b)))

        return colors

    def create_command(self) -> None:
        if self._animation is None:
            return ""

        animation = self._animation
        rgb = self._color_tab.color_picker_rgb.rgb
        delay = self._animation_display.animation_delay_slider_value

        self._command = f"{animation}?r={rgb[0]}&g={rgb[1]}&b={rgb[2]}&delay={delay}"

    @property
    def animation_display(self) -> AnimationDisplay:
        return self._animation_display

    @property
    def command(self) -> str:
        return self._command
