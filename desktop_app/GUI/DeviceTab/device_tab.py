import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton
from GUI.DeviceTab.popup import PopUp
from GUI.Menus.bot_menu_bar import OptionsMenu
from ArduinoBackend.arduino import Arduino
from GUI.DeviceTab.loading_bar import LoadingFrame


class DeviceTab(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(
        self, master, options_menu: OptionsMenu, top_menu_bar, *args, **kwargs
    ) -> None:
        super().__init__(
            master=master, fg_color="gray20", border_color="black", border_width=4
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._master = master
        self._canvas_frame = ctk.CTkFrame(self)
        self._loading_frame = LoadingFrame(self, top_menu_bar)

        self._options_menu = options_menu

        self._canvas = ctk.CTkCanvas(
            self._canvas_frame, highlightthickness=0, bg=self.cget("fg_color")
        )

        self._scrollbar = ctk.CTkScrollbar(
            self._canvas_frame, orientation="vertical", command=self._canvas.yview
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

        self.add_content()

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<Configure>", self._on_frame_configure)

        self._scan_button = CSButton(self, "scan", self.update_with_load)
        self._scan_button.grid(row=1, sticky="ew", padx=10, pady=10)

    def update_with_load(self) -> None:
        self._canvas_frame.grid_forget()
        self._loading_frame.grid(row=0, sticky="nsew", padx=10, pady=10)
        self._loading_frame.start_process()

    def add_content(self) -> None:
        for widget in self._content_frame.winfo_children():
            if widget.winfo_exists():
                widget.destroy()

        for arduino in self._options_menu.manager.devices:
            arduino_dict = arduino.to_dict()

            arduino_frame = ctk.CTkFrame(
                self._content_frame,
                fg_color="gray18",
                corner_radius=15,
                height=200,
                border_color="black",
                border_width=4,
            )
            arduino_frame.grid_rowconfigure(0, weight=1, minsize=200)
            arduino_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            arduino_frame.pack(
                fill="x", expand=True, padx=DeviceTab._PADX, pady=DeviceTab._PADY
            )

            name_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            name_frame.grid_rowconfigure(0, weight=1)
            name_frame.grid_columnconfigure((0, 1), weight=1)
            name_frame.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

            name_label = ctk.CTkLabel(
                name_frame,
                text=arduino_dict["name"],
                font=("Inter", 20, "bold"),
            )
            name_label.grid(row=0, column=0, padx=DeviceTab._PADX, pady=DeviceTab._PADY)

            edit_button = CSButton(
                name_frame,
                text="rename",
                command=lambda arduino=arduino, label=name_label: self._edit_name(
                    arduino, label
                ),
            )
            edit_button.grid(
                row=0, column=1, padx=DeviceTab._PADX, pady=DeviceTab._PADY
            )

            ip_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            ip_frame.grid(
                row=0,
                column=1,
                sticky="nsew",
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

            ip_label = ctk.CTkLabel(
                ip_frame, text=arduino_dict["ip_address"], font=("Inter", 20, "bold")
            )
            ip_label.pack(
                fill="both", expand=True, padx=DeviceTab._PADX, pady=DeviceTab._PADY
            )

            mac_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            mac_frame.grid(
                row=0,
                column=2,
                sticky="nsew",
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

            mac_label = ctk.CTkLabel(
                mac_frame,
                text=arduino_dict["mac_address"],
                font=("Inter", 20, "bold"),
            )
            mac_label.pack(fill="both", expand=True)

            status_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            status_frame.grid_rowconfigure(0, weight=1)
            status_frame.grid_columnconfigure((0, 1), weight=1)
            status_frame.grid(
                row=0,
                column=3,
                sticky="nsew",
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

            status_label = ctk.CTkLabel(
                status_frame,
                text="Online" if arduino_dict["status"] else "Offline",
                font=("Inter", 20, "bold"),
            )
            status_label.grid(
                row=0,
                column=0,
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

            status_display = ctk.CTkFrame(
                status_frame,
                fg_color="green" if arduino_dict["status"] else "red",
                corner_radius=15,
                border_color="black",
                border_width=4,
                width=50,
                height=50,
            )
            status_display.grid(
                row=0,
                column=1,
                padx=DeviceTab._PADX,
                pady=DeviceTab._PADY,
            )

    def _on_frame_configure(self, event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _edit_name(self, arduino: Arduino, label: ctk.CTkLabel) -> None:
        PopUp(self._options_menu, arduino, label)

    def grid_canvas_frame(self):
        self._canvas_frame.grid(row=0, sticky="nsew", padx=10, pady=10)

    @property
    def options_menu_manager(self) -> OptionsMenu:
        return self._options_menu.manager

    @options_menu_manager.setter
    def options_menu_manager(self, value) -> None:
        self._options_menu.manager = value
