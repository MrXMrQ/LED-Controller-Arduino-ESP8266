import customtkinter as ctk


class ColorPickerRGB(ctk.CTkFrame):
    _FONT = ("Inter", 16, "bold")
    _PADX = 10

    def __init__(self, master, button_style: dict, *args, **kwargs) -> None:
        super().__init__(
            master=master, border_color="black", border_width=4, *args, **kwargs
        )
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._button_style = button_style

        self._slider_frame = ctk.CTkFrame(
            self,
            border_color="black",
            border_width=4,
            corner_radius=15,
            fg_color="gray21",
        )
        self._slider_frame.grid(
            row=1, column=0, sticky="nsew", padx=ColorPickerRGB._PADX, pady=10
        )
        self._slider_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self._slider_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._red_slider = ctk.CTkSlider(
            self._slider_frame,
            fg_color="#D14C4C",
            progress_color="#B22D2D",
            button_color="#D14C4C",
            button_hover_color="#F27474",
            from_=0,
            to=255,
            number_of_steps=256,
            command=self._update_color_from_slider,
        )
        self._red_slider.set(255)
        self._red_slider.grid(row=0, column=1, padx=ColorPickerRGB._PADX, pady=10)

        red_label = ctk.CTkLabel(
            self._slider_frame,
            text="R",
            text_color="#D14C4C",
            font=ColorPickerRGB._FONT,
            anchor="e",
        )
        red_label.grid(row=0, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e")

        self._red_entry = ctk.CTkEntry(
            self._slider_frame,
            border_color="#D14C4C",
            font=ColorPickerRGB._FONT,
            width=60,
        )
        self._red_entry.bind(
            "<Return>",
            lambda event: self._update_color_from_entry(),
        )
        self._red_entry.grid(
            row=0, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._green_slider = ctk.CTkSlider(
            self._slider_frame,
            fg_color="#4CAF50",
            progress_color="#2E7D32",
            button_color="#4CAF50",
            button_hover_color="#81C784",
            from_=0,
            to=255,
            number_of_steps=256,
            command=self._update_color_from_slider,
        )
        self._green_slider.set(0)
        self._green_slider.grid(row=1, column=1, padx=ColorPickerRGB._PADX, pady=10)

        green_label = ctk.CTkLabel(
            self._slider_frame,
            text="G",
            text_color="#4CAF50",
            font=ColorPickerRGB._FONT,
            anchor="e",
        )
        green_label.grid(
            row=1, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e"
        )

        self._green_entry = ctk.CTkEntry(
            self._slider_frame,
            border_color="#4CAF50",
            font=ColorPickerRGB._FONT,
            width=60,
        )
        self._green_entry.bind(
            "<Return>",
            lambda event: self._update_color_from_entry(),
        )
        self._green_entry.grid(
            row=1, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._blue_slider = ctk.CTkSlider(
            self._slider_frame,
            fg_color="#3F72AF",
            progress_color="#1E4F91",
            button_color="#3F72AF",
            button_hover_color="#6FA9DC",
            from_=0,
            to=255,
            number_of_steps=256,
            command=self._update_color_from_slider,
        )
        self._blue_slider.set(100)
        self._blue_slider.grid(row=2, column=1, padx=ColorPickerRGB._PADX, pady=10)

        blue_label = ctk.CTkLabel(
            self._slider_frame,
            text="B",
            text_color="#3F72AF",
            font=ColorPickerRGB._FONT,
            anchor="e",
        )
        blue_label.grid(row=2, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e")

        self._blue_entry = ctk.CTkEntry(
            self._slider_frame,
            border_color="#3F72AF",
            font=ColorPickerRGB._FONT,
            width=60,
        )
        self._blue_entry.bind(
            "<Return>",
            lambda event: self._update_color_from_entry(),
        )
        self._blue_entry.grid(
            row=2, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._entrys = [
            self._red_entry,
            self._green_entry,
            self._blue_entry,
        ]
        submit_rgb_entrys_btn = ctk.CTkButton(
            self._slider_frame,
            text="Submit",
            command=self._update_color_from_entry,
            **self._button_style,
        )
        submit_rgb_entrys_btn.grid(
            row=3,
            column=0,
            padx=50,
            pady=10,
            columnspan=3,
            sticky="nsew",
        )

        self._brightness_slider = ctk.CTkSlider(
            self._slider_frame,
            fg_color="#E0DEDA",
            progress_color="#C2C0BA",
            button_color="#E0DEDA",
            button_hover_color="#EAE9E6",
            from_=0,
            to=255,
            number_of_steps=256,
            command=self._update_color_from_slider,
        )
        self._brightness_slider.set(255)
        self._brightness_slider.grid(
            row=4, column=1, padx=ColorPickerRGB._PADX, pady=10
        )

        brightness_label_left = ctk.CTkLabel(
            self._slider_frame,
            text="🔅",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 16),
            anchor="e",
        )
        brightness_label_left.grid(
            row=4, column=0, padx=ColorPickerRGB._PADX, pady=10, sticky="e"
        )

        brightness_label_right = ctk.CTkLabel(
            self._slider_frame,
            text="🔆",
            text_color="#3F72AF",
            font=("Segoe UI Emoji", 16),
            anchor="w",
        )
        brightness_label_right.grid(
            row=4, column=2, padx=ColorPickerRGB._PADX, pady=10, sticky="w"
        )

        self._set_rgb()
        self._update_entry_text(self._rgb)

        self._color_display_frame = ctk.CTkFrame(
            self,
            border_color="black",
            border_width=4,
            corner_radius=15,
            fg_color=self._convert_rgb_to_hex(self._rgb),
            height=200,
            width=200,
        )
        self._color_display_frame.grid(row=0, column=0, pady=10)

    def _update_color_from_slider(self, value) -> None:
        self._set_rgb()
        self._update_color_display(self._rgb)
        self._update_entry_text(self._rgb)

    def _set_rgb(self) -> None:
        brightness = self._brightness_slider.get() / 255

        self._rgb = (
            int(round(self._red_slider.get()) * brightness),
            int(round(self._green_slider.get()) * brightness),
            int(round(self._blue_slider.get()) * brightness),
        )

    def _update_color_display(self, rgb: tuple[int, int, int]) -> None:
        self._color_display_frame.configure(fg_color=self._convert_rgb_to_hex(rgb))

    def _convert_rgb_to_hex(self, rgb: tuple[int, int, int]) -> str:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _update_entry_text(self, rgb: tuple[int, int, int]) -> None:
        self._red_entry.delete(0, ctk.END)
        self._green_entry.delete(0, ctk.END)
        self._blue_entry.delete(0, ctk.END)

        self._red_entry.insert(0, str(round(rgb[0])))
        self._green_entry.insert(0, str(round(rgb[1])))
        self._blue_entry.insert(0, str(round(rgb[2])))

    def _update_color_from_entry(self) -> None:
        for entry in self._entrys:
            if entry.get().strip().isdigit():
                value = max(0, min(255, int(entry.get())))

                if entry == self._red_entry:
                    self._red_slider.set(value)
                elif entry == self._green_entry:
                    self._green_slider.set(value)
                elif entry == self._blue_entry:
                    self._blue_slider.set(value)

                self._set_rgb()
                self._update_color_display(self._rgb)

        self._update_entry_text(self._rgb)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return self._rgb
