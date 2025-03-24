import customtkinter as ctk


def resetTextColor():
    scanButton.configure(text_color="white")
    colorButton.configure(text_color="white")
    animationButton.configure(text_color="white")
    singleLEDButton.configure(text_color="white")


def removeWidgets():
    for widget in middle_frame.winfo_children():
        widget.grid_forget()


def scanButtonClick():
    resetTextColor()
    scanButton.configure(text_color="Yellow")

    removeWidgets()

    middle_label = ctk.CTkLabel(middle_frame, text="1")
    middle_label.grid(row=0, column=0, pady=20, padx=20)


def ColorButtonClick():
    resetTextColor()
    colorButton.configure(text_color="Yellow")

    removeWidgets()

    middle_label = ctk.CTkLabel(middle_frame, text="2")
    middle_label.grid(row=0, column=0, pady=20, padx=20)


def AnimationButtonClick():
    resetTextColor()
    animationButton.configure(text_color="Yellow")
    removeWidgets()

    middle_label = ctk.CTkLabel(middle_frame, text="3")
    middle_label.grid(row=0, column=0, pady=20, padx=20)


def LEDButtonClick():
    resetTextColor()
    singleLEDButton.configure(text_color="Yellow")
    removeWidgets()

    middle_label = ctk.CTkLabel(middle_frame, text="4")
    middle_label.grid(row=0, column=0, pady=20, padx=20)


root = ctk.CTk()
root.title("LED-Controller")
root.geometry("800x700")
root.minsize(800, 700)
root.maxsize(1100, 900)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

root.grid_columnconfigure(0, weight=1)

top_frame = ctk.CTkFrame(
    root,
    fg_color="#9E4F40",
    corner_radius=15,
    border_color="#7C4A3B",
    border_width=3,
    height=20,
)

top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_rowconfigure(1, weight=1)

top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)
top_frame.grid_columnconfigure(2, weight=1)
top_frame.grid_columnconfigure(3, weight=1)

scanButton = ctk.CTkButton(
    top_frame,
    text="SCAN",
    command=scanButtonClick,
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",  # Buttonfarbe
    hover_color="#004F49",  # Lila Hover-Farbe
    text_color="white",  # Textfarbe
    font=("Inter", 16, "bold"),  # Schriftart
    border_width=3,  # Randbreite
    border_color="#333333",  # Schwarzer Rand
)
scanButton.grid(row=1, column=0, pady=5, padx=10)

colorButton = ctk.CTkButton(
    top_frame,
    text="Color",
    command=ColorButtonClick,
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",  # Buttonfarbe
    hover_color="#004F49",  # Lila Hover-Farbe
    text_color="white",  # Textfarbe
    font=("Inter", 16, "bold"),  # Schriftart
    border_width=3,  # Randbreite
    border_color="#333333",  # Schwarzer Rand
)
colorButton.grid(row=1, column=1, pady=5, padx=10)

animationButton = ctk.CTkButton(
    top_frame,
    text="Animation",
    command=AnimationButtonClick,
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",  # Buttonfarbe
    hover_color="#004F49",  # Lila Hover-Farbe
    text_color="white",  # Textfarbe
    font=("Inter", 16, "bold"),  # Schriftart
    border_width=3,  # Randbreite
    border_color="#333333",  # Schwarzer Rand
)
animationButton.grid(row=1, column=2, pady=5, padx=10)

singleLEDButton = ctk.CTkButton(
    top_frame,
    text="LED",
    command=LEDButtonClick,
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",  # Buttonfarbe
    hover_color="#004F49",  # Lila Hover-Farbe
    text_color="white",  # Textfarbe
    font=("Inter", 16, "bold"),  # Schriftart
    border_width=3,  # Randbreite
    border_color="#333333",  # Schwarzer Rand
)
singleLEDButton.grid(row=1, column=3, pady=5, padx=10)

label = ctk.CTkLabel(top_frame, text="LED-Controller", font=("Inter", 30, "bold"))
label.grid(row=0, columnspan=4)

top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=7)

middle_frame = ctk.CTkFrame(
    root,
    fg_color="#9E4F40",
    corner_radius=15,
    border_color="#7C4A3B",
    border_width=3,
    height=40,
)
middle_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=7)
middle_label = ctk.CTkLabel(middle_frame, text="default")
middle_label.grid(row=0, column=0, pady=20, padx=20)

bottom_frame = ctk.CTkFrame(
    root,
    fg_color="#9E4F40",
    corner_radius=15,
    border_color="#7C4A3B",
    border_width=3,
    height=20,
)

bottom_frame.grid_rowconfigure(0, weight=1)

bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)
bottom_frame.grid_columnconfigure(2, weight=1)
bottom_frame.grid_columnconfigure(3, weight=1)

options = ["Option 1", "Option 2", "Option 3"]
option_menu = ctk.CTkOptionMenu(
    bottom_frame,
    values=options,
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",
    text_color="white",
    font=("Inter", 16, "bold"),
)
option_menu.grid(row=0, column=0, pady=5, padx=10)

pushButton = ctk.CTkButton(
    bottom_frame,
    text="PUSH",
    width=200,
    height=50,
    corner_radius=7,
    fg_color="#2F3A49",  # Buttonfarbe
    hover_color="#004F49",  # Lila Hover-Farbe
    text_color="white",  # Textfarbe
    font=("Inter", 16, "bold"),  # Schriftart
    border_width=3,  # Randbreite
    border_color="#333333",  # Schwarzer Rand
)
pushButton.grid(row=0, column=3, pady=5, padx=10)

bottom_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=7)

root.mainloop()
