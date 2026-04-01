import tkinter as tk
from ui import ForgeApp


def main() -> None:
    root = tk.Tk()
    app = ForgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()