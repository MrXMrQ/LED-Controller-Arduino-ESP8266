import re as regex
import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton


class ColorPickerHex(ctk.CTkFrame):
    _FONT = ("Inter", 20, "bold")
    _PADX = 10
    _PADY = 10

    _PRESET_HEX_CODES = [
        "#DC143C",  # Crimson
        "#FF6347",  # Tomato
        "#FF7F50",  # Coral
        "#FF4500",  # OrangeRed (neu)
        "#FFA500",  # Orange
        "#FF8C00",  # DarkOrange
        "#FFD700",  # Gold
        "#F0E68C",  # Khaki
        "#FAFAD2",  # LightGoldenrodYellow
        "#FFFACD",  # LemonChiffon
        "#FFE4B5",  # Moccasin
        "#ADFF2F",  # GreenYellow (neu)
        "#32CD32",  # LimeGreen
        "#3CB371",  # MediumSeaGreen
        "#2E8B57",  # SeaGreen
        "#6B8E23",  # OliveDrab
        "#98FB98",  # PaleGreen
        "#87CEEB",  # SkyBlue
        "#00CED1",  # DarkTurquoise (neu)
        "#1E90FF",  # DodgerBlue
        "#4169E1",  # RoyalBlue
        "#7B68EE",  # MediumSlateBlue
        "#000080",  # Navy
        "#9370DB",  # MediumPurple (neu)
        "#DA70D6",  # Orchid
        "#BA55D3",  # MediumOrchid
        "#EE82EE",  # Violet
        "#708090",  # SlateGray
        "#778899",  # LightSlateGray
        "#D3D3D3",  # LightGray (neu)
        "#A0522D",  # Sienna (neu)
        "#8B4513",  # SaddleBrown (neu)
    ]

    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(
            master=master,
            border_color="black",
            border_width=4,
            height=200,
            *args,
            **kwargs
        )
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._master = master

        self._hex_frame = ctk.CTkFrame(self, border_color="black", border_width=4)
        self._hex_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self._hex_frame.grid_columnconfigure(0, weight=1)
        self._hex_frame.grid(
            row=0,
            column=0,
            padx=ColorPickerHex._PADX,
            pady=ColorPickerHex._PADY,
            sticky="nsew",
        )

        headline_label = ctk.CTkLabel(
            self._hex_frame,
            text="HEX ~ Color",
            font=ColorPickerHex._FONT,
            anchor="n",
        )
        headline_label.grid(
            row=0,
            column=0,
            padx=ColorPickerHex._PADX,
            pady=ColorPickerHex._PADY,
            sticky="n",
        )

        self._hex_entry = ctk.CTkEntry(
            self._hex_frame,
            border_color="black",
            border_width=4,
            font=ColorPickerHex._FONT,
        )
        self._hex_entry.insert(
            0,
            self._master._color_picker_rgb.convert_rgb_to_hex(
                self._master._color_picker_rgb.rgb
            ),
        )
        self._hex_entry.bind("<Return>", lambda event: self._apply_hex_input())
        self._hex_entry.bind(
            "<KeyRelease>",
            lambda event, entry_widget=self._hex_entry: self._on_keyrelease(
                entry_widget
            ),
        )
        self._hex_entry.grid(
            row=1,
            column=0,
            padx=ColorPickerHex._PADX,
            pady=ColorPickerHex._PADY,
            sticky="nsew",
        )

        hex_entry_submit_btn = CSButton(
            self._hex_frame,
            text="submit",
            command=self._apply_hex_input,
        )
        hex_entry_submit_btn.grid(
            row=2,
            column=0,
            padx=ColorPickerHex._PADX,
            pady=ColorPickerHex._PADY,
            sticky="nsew",
        )

        self._presets_frame = ctk.CTkFrame(self, border_color="black", border_width=4)
        self._presets_frame.grid(
            row=1,
            column=0,
            padx=ColorPickerHex._PADX,
            pady=ColorPickerHex._PADY,
            sticky="nsew",
        )

        elements_per_row = 8
        current_row = 0

        for col in range(elements_per_row):
            self._presets_frame.grid_columnconfigure(col, weight=1)

        for i in range(len(ColorPickerHex._PRESET_HEX_CODES)):
            if i % elements_per_row == 0:
                current_row += 1

            preset_button = CSButton(
                self._presets_frame,
                text="",
                border_color="black",
                border_width=4,
                height=30,
                width=30,
                fg_color=ColorPickerHex._PRESET_HEX_CODES[i],
                command=lambda color=ColorPickerHex._PRESET_HEX_CODES[
                    i
                ]: self._apply_preset(color),
            )
            preset_button.grid(
                row=current_row,
                column=i % elements_per_row,
                padx=ColorPickerHex._PADX + 12,
                pady=ColorPickerHex._PADY + 10,
                sticky="nsew",
            )

    def _apply_preset(self, hex_code: str) -> None:
        self._update_hex_entry(hex_code)
        self._master._color_picker_rgb.update_rgb_from_hex(hex_code)

    def _apply_hex_input(self) -> None:
        hex_code = self._hex_entry.get()
        if regex.match(r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", hex_code):
            self._master._color_picker_rgb.update_rgb_from_hex(hex_code)

    def _on_keyrelease(self, entry) -> None:
        entry_text = entry.get()
        entry.delete(0, ctk.END)
        entry.insert(0, entry_text.upper())

    def _update_hex_entry(self, hex_code: str) -> None:
        self._hex_entry.delete(0, ctk.END)
        self._hex_entry.insert(0, hex_code)
