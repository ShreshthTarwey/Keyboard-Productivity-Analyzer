import tkinter as tk
from gui import TrackerGUI

def main():
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
