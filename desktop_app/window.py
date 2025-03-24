import customtkinter as ctk
from ipScanner import IPScanner
from requestHandler import RequestHandler
import requests


class Window(ctk.CTk):
    buttons = []
    current_ip = ""
    http_post = ""

    def __init__(
        self, title: str, width: int, height: int, maxWidth: int, maxHeight: int
    ):
        super().__init__()

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.maxsize(maxWidth, maxHeight)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=4)
        self.grid_rowconfigure(2, weight=1)

        self.grid_columnconfigure(0, weight=1)

        self.topFrame = self.genTopFrame()
        self.midFrame = self.genMidFrame()
        self.botFrame = self.genBotFrame()

        self.scanLabel = self.genScanLabel()
        self.colorLabel = self.genColorLabel()
        self.animationLabel = self.genAnimationLabel()
        self.ledLabel = self.genLEDLabel()

        middle_label = self.scanLabel
        middle_label.grid(row=0, column=0, pady=20, padx=20)

        Window.buttons.append(self.scanButton)
        Window.buttons.append(self.colorButton)
        Window.buttons.append(self.animationButton)
        Window.buttons.append(self.singleLEDButton)
        Window.buttons.append(self.pushButton)

    def genTopFrame(self):
        top_frame = ctk.CTkFrame(
            self,
            fg_color="#3A3E6D",
            corner_radius=15,
            border_color="#2D315A",
            border_width=3,
            height=20,
        )

        for col in range(4):
            top_frame.grid_columnconfigure(col, weight=1)

        for row in range(2):
            top_frame.grid_rowconfigure(row, weight=1)

        label = ctk.CTkLabel(
            top_frame, text="LED-Controller", font=("Inter", 30, "bold")
        )
        label.grid(row=0, columnspan=4)

        self.scanButton = ctk.CTkButton(
            top_frame,
            text="SCAN",
            command=self.scanButtonClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="#2D315A",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        self.scanButton.grid(row=1, column=0, pady=5, padx=10)

        self.colorButton = ctk.CTkButton(
            top_frame,
            text="COLOR",
            command=self.colorButtonClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        self.colorButton.grid(row=1, column=1, pady=5, padx=10)

        self.animationButton = ctk.CTkButton(
            top_frame,
            text="ANIMATION",
            command=self.animationButtonClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        self.animationButton.grid(row=1, column=2, pady=5, padx=10)

        self.singleLEDButton = ctk.CTkButton(
            top_frame,
            text="LED",
            command=self.ledButtonClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        self.singleLEDButton.grid(row=1, column=3, pady=5, padx=10)

        top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=3)

        return top_frame

    def genMidFrame(self):
        middle_frame = ctk.CTkFrame(
            self,
            fg_color="#3A3E6D",
            corner_radius=15,
            border_color="#2D315A",
            border_width=3,
            height=40,
        )
        middle_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=3)

        return middle_frame

    def scanIPS(self) -> list:
        ips = IPScanner()
        devices = ips.get_devices()

        if devices == []:
            return ["EMPTY"]

        return devices

    def ledPauseClick(self):
        response = requests.get(f"http://{Window.current_ip}/stop")
        print(response)

    def ledOffClick(self):
        response = requests.get(f"http://{Window.current_ip}/ledOff")
        print(response)

    def genBotFrame(self):
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="#3A3E6D",
            corner_radius=15,
            border_color="#2D315A",
            border_width=3,
            height=20,
        )

        bottom_frame.grid_rowconfigure(0, weight=1)

        for col in range(4):
            bottom_frame.grid_columnconfigure(col, weight=1)

        options = self.scanIPS()
        Window.current_ip = options[0]
        self.option_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=options,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            button_color="#8387C4",
            button_hover_color="#6D72A3",
            dropdown_fg_color="#8387C4",
            dropdown_text_color="white",
            command=lambda value: setattr(Window, "current_ip", value),
        )
        self.option_menu.grid(row=0, column=0, pady=5, padx=10)

        ledPauseButton = ctk.CTkButton(
            bottom_frame,
            text="TEMP",
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        ledPauseButton.grid(row=0, column=1, pady=5, padx=10)

        ledOffButton = ctk.CTkButton(
            bottom_frame,
            text="LED OFF",
            command=self.ledOffClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        ledOffButton.grid(row=0, column=2, pady=5, padx=10)

        self.pushButton = ctk.CTkButton(
            bottom_frame,
            text="POST",
            command=self.pushButtonClick,
            width=200,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            hover_color="#8378C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            border_width=4,
            border_color="#2D315A",
        )
        self.pushButton.grid(row=0, column=3, pady=5, padx=10)

        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=3)

        return bottom_frame

    def genScanLabel(self):
        middle_label = ctk.CTkLabel(self.midFrame, text="1")

        return middle_label

    def genColorLabel(self):
        middle_label = ctk.CTkLabel(self.midFrame, text="2")

        return middle_label

    def genAnimationLabel(self):
        middle_label = ctk.CTkLabel(self.midFrame, text="3")

        return middle_label

    def genLEDLabel(self):
        middle_label = ctk.CTkLabel(self.midFrame, text="4")

        return middle_label

    def unmark(self):
        for button in Window.buttons:
            button.configure(text_color="white")

    def removeChilds(self):
        for widget in self.midFrame.winfo_children():
            widget.grid_forget()

    def scanButtonClick(self):
        self.unmark()
        self.scanButton.configure(text_color="#2D315A")
        self.removeChilds()

        middle_label = self.scanLabel
        middle_label.grid(row=0, column=0, pady=20, padx=20)

    def colorButtonClick(self):
        self.unmark()
        self.colorButton.configure(text_color="#2D315A")

        self.removeChilds()

        middle_label = self.colorLabel
        middle_label.grid(row=0, column=0, pady=20, padx=20)

    def animationButtonClick(self):
        self.unmark()
        self.animationButton.configure(text_color="#2D315A")

        self.removeChilds()

        middle_label = self.animationLabel
        middle_label.grid(row=0, column=0, pady=20, padx=20)

    def ledButtonClick(self):
        self.unmark()
        self.singleLEDButton.configure(text_color="#2D315A")

        self.removeChilds()

        middle_label = self.ledLabel
        middle_label.grid(row=0, column=0, pady=20, padx=20)

    def pushButtonClick(self):
        self.unmark()

        print(Window.current_ip, Window.http_post)
