import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton
from GUI.OptionsMenu.options_menu import OptionsMenu
from arduino import Arduino


class PopUp(ctk.CTkToplevel):
    def __init__(
        self,
        options_menu: OptionsMenu,
        arduino: Arduino,
        label: ctk.CTkLabel,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.title("Edit arduino name")
        self.geometry("200x200")
        self.resizable(False, False)
        self.grab_set()

        self._options_menu = options_menu
        self._manager = self._options_menu.manager
        self._arduino = arduino
        self._label = label

        label = ctk.CTkLabel(self, text="Enter new Arduino name")
        label.pack(pady=10)

        self._entry = ctk.CTkEntry(self)
        self._entry.bind(
            "<Return>",
            self._on_submit,
        )
        self._entry.pack(pady=10)

        submit_button = CSButton(
            self,
            text="Submit",
            command=self._on_submit,
        )
        submit_button.pack(pady=10)

    def _on_submit(self, event) -> None:
        user_input = self._entry.get()
        if user_input:
            self.destroy()

            for i in self._manager.devices:
                if i == self._arduino:
                    i.name = user_input

            self._manager._save_to_file(self._manager.devices)
            self._label.configure(text=user_input)

            options_list = list(self._options_menu._build_device_map().keys())
            default_value = options_list[0] if options_list else "No devices"
            self._options_menu.configure(
                values=options_list,
                variable=ctk.StringVar(value=default_value),
            )
