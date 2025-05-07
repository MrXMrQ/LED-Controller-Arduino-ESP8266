import customtkinter as ctk


class LED(ctk.CTkFrame):
    def __init__(
        self, master, rgb: tuple[int, int, int], brightness: int, *args, **kwargs
    ) -> None:
        super().__init__(
            master,
            corner_radius=15,
            height=50,
            width=50,
            border_color="black",
            fg_color="black",
            border_width=4,
            *args,
            **kwargs
        )

        self._rgb = rgb
        self._brightness = brightness

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self._rgb

    @rgb.setter
    def rgb(self, value: int) -> None:
        self._rgb = value

    @property
    def brightness(self) -> int:
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        self._brightness = value
