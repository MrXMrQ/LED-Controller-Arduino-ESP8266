import customtkinter as ctk


class BotMenuBar(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(
            master,
            border_color="black",
            border_width=4,
            corner_radius=15,
            height=30,
            *args,
            **kwargs
        )
