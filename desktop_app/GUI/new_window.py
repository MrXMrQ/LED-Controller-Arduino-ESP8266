import customtkinter as ctk

from GUI.MenuBars.top_menu_bar import TopMenuBar
from GUI.MenuBars.bot_menu_bar import BotMenuBar


class NewWindow(ctk.CTk):
    _PADX = 10
    _PADY = 10

    def __init__(self, title, width, height, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._temp = ctk.CTkFrame(self, border_color="black", border_width=4)
        self._temp.grid(
            row=1,
            rowspan=9,
            column=0,
            sticky="nsew",
            padx=NewWindow._PADX,
            pady=NewWindow._PADY,
        )
        self._temp.pack_propagate(False)

        self._bot_menu_bar = BotMenuBar(self)
        self._bot_menu_bar.grid(
            row=10, column=0, sticky="nsew", padx=NewWindow._PADX, pady=NewWindow._PADY
        )

        self._top_menu_bar = TopMenuBar(
            self, self._temp, self._bot_menu_bar.options_menu
        )
        self._top_menu_bar.grid(
            row=0, column=0, sticky="nsew", padx=NewWindow._PADX, pady=NewWindow._PADY
        )
