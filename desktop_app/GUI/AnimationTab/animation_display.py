import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB
from GUI.AnimationTab.led_display import LEDDisplay


class AnimationDisplay(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self, master, color_picker_rgb: ColorPickerRGB, *args, **kwargs
    ) -> None:
        super().__init__(master, border_color="black", border_width=4, *args, **kwargs)
        self._color_picker_rgb = color_picker_rgb

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._led_display = LEDDisplay(self, border_color="black", border_width=4)
        self._led_display.grid(
            row=0,
            column=0,
            padx=AnimationDisplay._PADX,
            pady=AnimationDisplay._PADY,
            sticky="nsew",
        )

        self._color_and_speed_frame = ctk.CTkFrame(
            self, border_color="black", border_width=4
        )
        self._color_and_speed_frame.grid(
            row=1,
            column=0,
            padx=AnimationDisplay._PADX,
            pady=AnimationDisplay._PADY,
            sticky="nsew",
        )

        self._color_and_speed_frame.grid_rowconfigure(0, weight=1)
        self._color_and_speed_frame.grid_columnconfigure((0, 1), weight=1)

        slider_frame = ctk.CTkFrame(
            self._color_and_speed_frame, border_color="black", border_width=4
        )
        slider_frame.grid(
            row=0,
            column=0,
            padx=AnimationDisplay._PADX,
            pady=AnimationDisplay._PADY,
            sticky="nsew",
        )
        slider_frame.grid_rowconfigure((0, 1), weight=1)
        slider_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._brightness_slider = ctk.CTkSlider(
            slider_frame,
            fg_color="#E0DEDA",
            progress_color="#C2C0BA",
            button_color="#E0DEDA",
            button_hover_color="#EAE9E6",
            from_=0,
            to=255,
            number_of_steps=256,
            command=self._update_brightness_slider,
        )
        self._brightness_slider.set(255)
        self._brightness_slider.grid(
            row=0, column=1, padx=ColorPickerRGB._PADX, pady=10
        )

        brightness_label_left = ctk.CTkLabel(
            slider_frame,
            text="🔅",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 25),
            anchor="e",
        )
        brightness_label_left.grid(
            row=0, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e"
        )

        brightness_label_right = ctk.CTkLabel(
            slider_frame,
            text="🔆",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 25),
            anchor="w",
        )
        brightness_label_right.grid(
            row=0, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._animation_speed_slider = ctk.CTkSlider(
            slider_frame,
            fg_color="#E0DEDA",
            progress_color="#C2C0BA",
            button_color="#E0DEDA",
            button_hover_color="#EAE9E6",
            from_=1,
            to=600,
            number_of_steps=600,
            command=self._update_animation_speed_slider,
        )
        self._animation_speed_slider.set(300)
        self._animation_speed_slider.grid(
            row=1, column=1, padx=ColorPickerRGB._PADX, pady=10
        )

        self._animation_speed = self._animation_speed_slider.get()

        animation_speed_label_left = ctk.CTkLabel(
            slider_frame,
            text="🐇",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 25),
            anchor="e",
        )
        animation_speed_label_left.grid(
            row=1, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e"
        )

        animation_speed_label_right = ctk.CTkLabel(
            slider_frame,
            text="🐢",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 25),
            anchor="w",
        )
        animation_speed_label_right.grid(
            row=1, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._color_display = ctk.CTkFrame(
            self._color_and_speed_frame,
            border_color="black",
            border_width=4,
            height=200,
            width=200,
        )
        self._color_display.grid(
            row=0,
            column=1,
            padx=AnimationDisplay._PADX,
            pady=AnimationDisplay._PADY,
        )

    def _update_brightness_slider(self, value) -> None:
        self._color_picker_rgb.update_from_animation_tab(value)
        self.update_color_display()

    def _update_animation_speed_slider(self, value) -> None:
        self._animation_speed = self._animation_speed_slider.get()

    def update_color_display(self) -> None:
        self._color_display.configure(
            True,
            fg_color=self._color_picker_rgb.convert_rgb_to_hex(
                self._color_picker_rgb.rgb
            ),
        )
        self._brightness_slider.set(self._color_picker_rgb.brightness_slider_value)

    @property
    def led_display(self) -> LEDDisplay:
        return self._led_display

    @property
    def brightness_slider_value(self) -> float:
        return self._brightness_slider.get()

    @property
    def animation_speed_slider_value(self) -> float:
        return self._animation_speed_slider.get()
