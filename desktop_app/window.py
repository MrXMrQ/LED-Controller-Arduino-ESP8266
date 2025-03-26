import customtkinter as ctk
from ipScanner import IPScanner


class Window(ctk.CTk):
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

        self.midFrame = self.initMidFrame()
        self.midFrame.grid(row=1, column=0, sticky="nsew", padx=20, pady=3)

        self.topFrame = self.initTopFrame()
        self.topFrame.grid(row=0, column=0, sticky="nsew", padx=20, pady=3)

        self.botFrame = self.initBotFrame()
        self.botFrame.grid(row=2, column=0, sticky="nsew", padx=20, pady=3)

        self.current_tab = self.initScanTab()
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initTopFrame(self) -> ctk.CTkFrame:
        topFrame = ctk.CTkFrame(
            master=self,
            height=20,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        topFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        topFrame.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(
            topFrame, text="LED-Controller", font=("Inter", 30, "bold")
        )
        label.grid(row=0, column=0, columnspan=4, pady=5)

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

        button_data = [
            ("SCAN", lambda: self.loadTab(self.initScanTab())),
            ("COLOR", lambda: self.loadTab(self.initColorTab())),
            ("ANIMATION", lambda: self.loadTab(self.initAnimationTab())),
            ("SINGLE LED", lambda: self.loadTab(self.initSingeLEDTab())),
        ]

        for col, (text, command) in enumerate(button_data):
            btn = ctk.CTkButton(
                topFrame,
                text=text,
                command=command,
                **button_options,
            )
            btn.grid(row=1, column=col, pady=5, padx=10, sticky="ew")

        return topFrame

    def loadTab(self, tab) -> None:
        self.current_tab.destroy()
        self.current_tab = tab
        self.current_tab.pack(
            expand=True,
            fill="both",
            padx=10,
            pady=10,
        )

    def initMidFrame(self) -> ctk.CTkFrame:
        middleFrame = ctk.CTkFrame(
            master=self,
            height=40,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        return middleFrame

    def initBotFrame(self) -> ctk.CTkFrame:
        botFrame = ctk.CTkFrame(
            master=self,
            height=20,
            corner_radius=15,
            border_width=4,
            border_color="#2D315A",
            fg_color="#3A3E6D",
        )

        botFrame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        botFrame.grid_rowconfigure(0, weight=1)

        options = ["1", "2", "3"]  # self.fillOptions()
        self.option_menu = ctk.CTkOptionMenu(
            botFrame,
            values=options,
            height=50,
            corner_radius=7,
            fg_color="#8387C4",
            text_color="white",
            font=("Inter", 20, "bold"),
            button_color="#8387C4",
            button_hover_color="#6D72A3",
            dropdown_fg_color="#8387C4",
            dropdown_text_color="white",
        )
        self.option_menu.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

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

        button_data = [
            ("LED ON", self.ledOnButtonClick),
            ("LED OFF", self.ledOffButtonClick),
            ("PUSH", self.pushButtonClick),
        ]

        for col, (text, command) in enumerate(button_data):
            btn = ctk.CTkButton(botFrame, text=text, command=command, **button_options)
            btn.grid(row=0, column=col + 1, pady=5, padx=10, sticky="ew")

        return botFrame

    def ledOnButtonClick(self) -> None:
        print("LED ON")

    def ledOffButtonClick(self) -> None:
        print("LED Off")

    def pushButtonClick(self) -> None:
        if self.option_menu.get() == "":
            print("Unable to push")
            return

        print(self.option_menu.get())

    def fillOptions(self) -> list:
        ips = IPScanner()
        devices = ips.get_devices()

        if devices == []:
            return [""]

        return devices

    def initScanTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            self.midFrame,
            text="1",
            fg_color="gray",
            corner_radius=15,
        )

    def initColorTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="2")

    def initAnimationTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="3")

    def initSingeLEDTab(self) -> ctk.CTkLabel:
        return ctk.CTkLabel(self.midFrame, text="4")
