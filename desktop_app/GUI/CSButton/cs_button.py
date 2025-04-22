from typing import Callable
import customtkinter as ctk


class CSButton(ctk.CTkButton):
    _BUTTON_STYLE = {
        "corner_radius": 7,
        "height": 50,
    }

    def __init__(
        self,
        master,
        text: str,
        command: Callable,
        height=50,
        corner_radius=7,
        fg_color="gray25",
        hover_color="gray26",
        border_color="black",
        border_width=4,
        text_color="white",
        font=("Inter", 20, "bold"),
        *args,
        **kwargs
    ) -> None:
        super().__init__(
            master,
            text=text,
            command=command,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            hover_color=hover_color,
            border_color=border_color,
            border_width=border_width,
            text_color=text_color,
            font=font,
            *args,
            **kwargs
        )
