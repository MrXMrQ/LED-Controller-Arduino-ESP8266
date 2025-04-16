import customtkinter as ctk


class DeviceTab(ctk.CTkFrame):
    button_options = {
        "corner_radius": 7,
        "height": 50,
        "fg_color": "#8387C4",
        "hover_color": "#8378C4",
        "text_color": "white",
        "font": ("Inter", 20, "bold"),
        "border_width": 4,
        "border_color": "#2D315A",
    }

    def __init__(
        self, master, manager, build_device_map_func, options_menu, *args, **kwargs
    ) -> None:
        super().__init__(master, *args, **kwargs)

        self._manager = manager
        self._build_device_map_func = build_device_map_func
        self._options_menu = options_menu

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="gray20",
            border_color="black",
            border_width=5,
        )
        self._canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self._canvas = ctk.CTkCanvas(
            self._canvas_frame,
            highlightthickness=0,
            bg=self._canvas_frame.cget("fg_color"),
        )
        self._scrollbar = ctk.CTkScrollbar(
            self._canvas_frame, orientation="vertical", command=self._canvas.yview
        )

        self._content_frame = ctk.CTkFrame(
            self._canvas, fg_color=self._canvas_frame.cget("fg_color")
        )
        self._content_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )

        self._window = self._canvas.create_window(
            (0, 0), window=self._content_frame, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self.update_arduinos(self._manager)

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas_frame.bind("<Configure>", self._resizeButton)

        self._canvas.pack(side="right", fill="both", expand=True, pady=10, padx=10)
        self._scrollbar.pack(side="left", fill="y", pady=15, padx=5)

        self._canvas_frame.grid(row=0, column=0, padx=10, pady=10)

    def _on_mousewheel(self, event) -> None:
        """Handle scrolling in animation list"""
        if self._canvas.winfo_exists() and self._canvas.winfo_ismapped():
            self._canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def _resizeButton(self, event) -> None:
        """Resize the animation buttons canvas"""
        self._canvas.itemconfigure(
            self._window, width=event.width - self._scrollbar.winfo_width() - 60
        )

    def update_arduinos(self, manager) -> None:
        self._manager = manager
        for widget in self._content_frame.winfo_children():
            if widget.winfo_exists():
                widget.destroy()

        for arduino in manager.devices:
            arduino_as_dict = arduino.to_dict()

            border_width = 4

            arduino_frame = ctk.CTkFrame(
                self._content_frame,
                fg_color="gray18",
                corner_radius=15,
                height=200,
                border_color="black",
                border_width=border_width,
            )
            arduino_frame.grid_rowconfigure(0, weight=1, minsize=200)
            arduino_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            arduino_frame.pack(fill="x", pady=5)

            name_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            name_frame.grid_rowconfigure(0, weight=1)
            name_frame.grid_columnconfigure((0, 1), weight=1)

            name_label = ctk.CTkLabel(
                name_frame,
                text=arduino_as_dict["name"],
                font=("Inter", 20, "bold"),
            )
            name_label.grid(row=0, column=0, padx=10)

            edit_button = ctk.CTkButton(
                name_frame,
                text="edit",
                command=lambda arduino=arduino, label=name_label: self._editName(
                    arduino, label
                ),
                **DeviceTab.button_options,
            )
            edit_button.grid(row=0, column=1)
            name_frame.grid(
                row=0, column=0, sticky="nsew", pady=10, padx=(border_width, 0)
            )

            ip_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            ip_frame.grid(row=0, column=1, sticky="nsew", pady=10)

            ip_label = ctk.CTkLabel(
                ip_frame, text=arduino_as_dict["ip_address"], font=("Inter", 20, "bold")
            )
            ip_label.pack(fill="both", expand=True, padx=10)

            mac_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            mac_frame.grid(row=0, column=2, sticky="nsew", pady=10)

            mac_label = ctk.CTkLabel(
                mac_frame,
                text=arduino_as_dict["mac_address"],
                font=("Inter", 20, "bold"),
            )
            mac_label.pack(fill="both", expand=True)

            status_frame = ctk.CTkFrame(
                arduino_frame, fg_color=arduino_frame.cget("fg_color")
            )
            status_frame.grid_rowconfigure(0, weight=1)
            status_frame.grid_columnconfigure((0, 1), weight=1)

            status_label = ctk.CTkLabel(
                status_frame,
                text="Online" if arduino_as_dict["status"] else "Offline",
                font=("Inter", 20, "bold"),
            )
            status_label.grid(row=0, column=0)

            status_display = ctk.CTkFrame(
                status_frame,
                fg_color="green" if arduino_as_dict["status"] else "red",
                corner_radius=15,
                border_color="black",
                border_width=4,
                width=50,
                height=50,
            )
            status_display.grid(row=0, column=1, padx=(5, 0))
            status_frame.grid(row=0, column=3, sticky="nsew", pady=10, padx=(0, 5))

    def _editName(self, arduino, label_to_change) -> None:
        self._popup = ctk.CTkToplevel(self)
        self._popup.title("EDIT")
        self._popup.geometry("200x200")
        self._popup.resizable(False, False)
        self._popup.grab_set()

        label = ctk.CTkLabel(self._popup, text="Enter new Arduino name")
        label.pack(pady=10)

        self._entry = ctk.CTkEntry(self._popup)
        self._entry.bind(
            "<Return>",
            lambda: self.on_submit(arduino, label_to_change),
        )
        self._entry.pack(pady=10)

        submit_button = ctk.CTkButton(
            self._popup,
            text="Submit",
            command=lambda: self.on_submit(arduino, label_to_change),
            **DeviceTab.button_options,
        )
        submit_button.pack(pady=10)

    def on_submit(self, arduino, label_to_change, event=None) -> None:
        user_input = self._entry.get()
        if user_input:
            self._popup.destroy()

            for i in self._manager.devices:
                if i == arduino:
                    i.name = user_input
                    print(i)

            self._manager._save_to_file(self._manager.devices)
            label_to_change.configure(text=user_input)

            options_list = list(self._build_device_map_func(self._manager).keys())
            print(options_list)
            default_value = options_list[0] if options_list else "No devices"
            self._options_menu.configure(
                values=options_list,
                variable=ctk.StringVar(value=default_value),
            )

            return
            self._build_device_map()
            options_list = list(self.device_map.keys())
            print(options_list)
            default_value = options_list[0] if options_list else "No devices"

            self.option_menu.configure(
                values=options_list,
                variable=ctk.StringVar(value=default_value),
            )
