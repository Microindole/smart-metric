from __future__ import annotations


def select_directory(initial_directory: str | None = None, title: str = "选择项目目录") -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askdirectory(
            initialdir=initial_directory or None,
            title=title,
            mustexist=True,
            parent=root,
        )
        return str(selected or "").strip()
    finally:
        root.destroy()
