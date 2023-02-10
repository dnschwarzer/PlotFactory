import PySimpleGUI as sg
import pathlib

import asyncio
import sys
import tkinter as tk
from tkinter import filedialog

from auswertung import Auswertung as aw

size = 11
height = 1
file_path = ""

layout = [
    [sg.Text('pick path', size=(size,height), background_color="blue")],
    [sg.Text('selected path:', size=(size,height)), sg.InputText(pathlib.Path().resolve(), key="csv_root_filepath", size=(size + 50, height)),
     sg.Button("open path dialog", key="button_openfiledialog", size=(size, height))],
    [sg.Check('v', key='check_v', default=True), sg.Check('c', key='check_c', default=True)],
    [sg.Button("generate", key="button_generate_plots", size=(size, height))],
]

async def main_window():
    global file_path, event_dict

    sg.theme("Dark")
    window = sg.Window('vlad plot slave', layout, size=(700, 180))
    win = window
    while True:
        window.refresh()
        event, values = window.read(timeout=0)
        if event == sg.WINDOW_CLOSED:
            break

        # Routine ---------------------------------
        if event == "button_openfiledialog":
            root = tk.Tk()
            root.withdraw()

            file_path = filedialog.askdirectory()
            win["csv_root_filepath"].Update(file_path)

        if event == "button_generate_plots":
            plot_factory = aw(values["csv_root_filepath"], values["check_c"], values["check_v"])
            success = "failed"

            success = await plot_factory.build()
            sg.Popup(success)

        await asyncio.sleep(0.1)

    window.close()
    sys.exit(1)
