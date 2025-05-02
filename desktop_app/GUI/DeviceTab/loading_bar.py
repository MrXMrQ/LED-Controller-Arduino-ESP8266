import customtkinter as ctk
import threading
from ArduinoBackend.arduinoManager import ArduinoManager


class LoadingFrame(ctk.CTkFrame):
    _PADX = 10
    _PADY = 10

    def __init__(self, master, top_menu_bar, *args, **kwargs) -> None:
        super().__init__(
            master=master, fg_color="gray20", border_color="black", border_width=4
        )

        self._content_frame = ctk.CTkFrame(self)
        self._content_frame.grid_rowconfigure((0, 1), weight=1)
        self._content_frame.grid_columnconfigure(0, weight=1)

        self._headline = ctk.CTkLabel(
            self._content_frame,
            height=60,
            bg_color="gray20",
            text="Scan process!",
            font=("Inter", 30, "bold"),
        )
        self._headline.grid(row=0, column=0, sticky="nsew")

        self._master = master
        self._top_menu_bar = top_menu_bar

        self.indicator_frame = ctk.CTkFrame(
            self._content_frame,
            height=60,
            border_color="black",
            border_width=4,
            fg_color="gray20",
            bg_color="gray20",
        )
        self.indicator_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=LoadingFrame._PADX,
            pady=LoadingFrame._PADY,
        )

        self.canvas = ctk.CTkCanvas(
            self.indicator_frame, height=50, bg="gray20", highlightthickness=0
        )
        self.canvas.pack(
            fill="both", expand=True, padx=LoadingFrame._PADX, pady=LoadingFrame._PADY
        )
        self.canvas.update_idletasks()

        self.is_loading = False
        self.animation_id = None
        self.process_thread = None

        self.bar = None
        self.bar_x = 0
        self.bar_width = 60
        self.bar_speed = 20

        self._content_frame.pack(fill="both", expand=True)

    def start_process(self) -> None:
        if self.is_loading:
            return

        self.is_loading = True

        self.canvas.delete("all")
        self._setup_bar_animation()

        self.process_thread = threading.Thread(target=self._background_process)
        self.process_thread.daemon = True
        self.process_thread.start()

        self._update_animation()

    def _background_process(self) -> None:
        try:
            self._manager = ArduinoManager()
            self._top_menu_bar.set_options_menu_manager(self._manager)
            self._top_menu_bar.options_menu.update_options()
            self.after(0, self._process_completed)
        except Exception as e:
            print(f"Fail: {e}")
            self._master.after(0, self._process_completed)

    def _process_completed(self) -> None:
        self.is_loading = False

        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None

        self.grid_forget()
        for arduino in self._manager.devices:
            print(arduino)

        self._master.add_content()
        self._master.grid_canvas_frame()

    def _setup_bar_animation(self) -> None:
        self.bar_x = 0
        self.bar = self.canvas.create_rectangle(
            0, 10, self.bar_width, 30, fill="#1f6aa5", width=0
        )

    def _update_animation(self) -> None:
        if not self.is_loading:
            return

        try:
            self._update_bar_animation()
            if self.winfo_exists():
                self.animation_id = self.after(30, self._update_animation)
        except Exception as e:
            print("Animation error:", e)

    def _update_bar_animation(self) -> None:
        width = self.canvas.winfo_width() or 400
        self.bar_x += self.bar_speed
        if self.bar_x > width:
            self.bar_x = -self.bar_width

        self.canvas.coords(self.bar, self.bar_x, 10, self.bar_x + self.bar_width, 30)
