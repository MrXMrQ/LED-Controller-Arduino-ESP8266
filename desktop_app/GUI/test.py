import tkinter as tk
from tkinter import ttk


class ScrollableFrame:
    def __init__(self, master):
        # Erstelle einen äußeren Frame als Container
        self.container = tk.Frame(master)
        self.container.pack(fill="both", expand=True)

        # Erstelle ein Canvas-Element
        self.canvas = tk.Canvas(self.container)

        # Erstelle eine vertikale Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.container, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar.pack(side="left", fill="y")

        # Konfiguriere das Canvas mit der Scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="right", fill="both", expand=True)

        # Erstelle einen inneren Frame für den Inhalt
        self.scrollable_frame = tk.Frame(self.canvas)

        # Erstelle ein Fenster im Canvas für den inneren Frame
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        for i in range(50):
            tk.Button(
                self.scrollable_frame,
                text=f"Element {i}",
                pady=10,
                bg="lightblue" if i % 2 == 0 else "lightgreen",
            ).pack(fill="x")

        # Aktualisiere die Scroll-Region, wenn die Größe des Frames sich ändert
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Ermögliche Scrollen mit dem Mausrad
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

    def on_frame_configure(self, event):
        # Aktualisiere die Scroll-Region auf die neue Größe des inneren Frames
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Passe die Breite des inneren Frames an die Breite des Canvas an
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, event):
        # Bindet das Mausrad an die Scrollfunktion
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        # Entbindet das Mausrad
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        # Scrolle mit dem Mausrad
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


root = tk.Tk()
root.title("Scrollbares Interface Demo")
root.geometry("400x300")

scroll_frame = ScrollableFrame(root)


root.mainloop()
