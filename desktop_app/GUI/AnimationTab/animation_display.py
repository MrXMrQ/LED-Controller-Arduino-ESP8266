import customtkinter as ctk

from GUI.ColorTab.color_picker_rgb import ColorPickerRGB


class AnimationDisplay(ctk.CTkFrame):
    button_styles = {
        "corner_radius": 7,
        "height": 60,
        "fg_color": "#8387C4",
        "hover_color": "#8378C4",
        "text_color": "white",
        "font": ("Inter", 20, "bold"),
        "border_width": 4,
        "border_color": "#2D315A",
    }

    _PADX = 10
    _PADY = 20

    def __init__(
        self, master, color_picker_rgb: ColorPickerRGB, *args, **kwargs
    ) -> None:
        super().__init__(master, border_color="black", border_width=4, *args, **kwargs)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._animation_display_frame = ctk.CTkFrame(
            self, border_color="black", border_width=4
        )
        self._animation_display_frame.grid(
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

        color_display = ctk.CTkFrame(
            self._color_and_speed_frame,
            border_color="black",
            border_width=4,
            height=200,
            width=200,
            fg_color=color_picker_rgb.convert_rgb_to_hex(color_picker_rgb.rgb),
        )
        color_display.grid(
            row=0,
            column=1,
            padx=AnimationDisplay._PADX,
            pady=AnimationDisplay._PADY,
        )
