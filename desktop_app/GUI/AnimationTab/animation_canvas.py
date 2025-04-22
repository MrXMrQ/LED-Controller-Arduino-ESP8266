from typing import Callable
import customtkinter as ctk

from GUI.CSButton.cs_button import CSButton


class AnimationCanvas(ctk.CTkFrame):
    _PADX = 10
    _PADY = 20

    def __init__(
        self, master: ctk.CTkFrame, content: list[tuple[str, Callable]]
    ) -> None:
        super().__init__(
            master=master, fg_color="gray20", border_color="black", border_width=4
        )

        self._canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bg=self.cget("fg_color")
        )

        self._scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self._canvas.yview
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

        self._add_content(content)

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self._content_frame.bind("<Configure>", self._on_frame_configure)

    def _add_content(self, content: list[tuple[str, Callable]]) -> None:
        for text, command in content:
            btn = CSButton(
                self._content_frame,
                text=text,
                command=command,
            )
            btn.pack(fill="x", padx=AnimationCanvas._PADX, pady=AnimationCanvas._PADY)
            btn.bind("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
