from typing import Callable
import customtkinter as ctk


class LEDDisplay(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self._leds = []
        self._is_animation_running = False
        self._animation_task = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1,
        )

        for i in range(10):
            led = ctk.CTkFrame(
                self,
                border_color="black",
                fg_color="black",
                border_width=4,
                width=35,
                height=35,
                corner_radius=30,
            )
            led.grid(row=0, column=i)
            self._leds.append(led)

    def start_animation(self, animation_function: Callable) -> None:
        self._is_animation_running = False

        if self._animation_task:
            self.after_cancel(self._animation_task)
        self._reset_LEDs()
        self._is_animation_running = True
        animation_function()

    def _reset_LEDs(self) -> None:
        for led in self._leds:
            if led.winfo_exists() and led.winfo_ismapped():
                led.configure(True, fg_color="black")

    @property
    def leds(self) -> list:
        return self._leds

    def set_animation_task(self, value) -> None:
        self._animation_task = value
