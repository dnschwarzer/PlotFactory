import PySimpleGUI as sg
import pathlib
import asyncio
import sys
import tkinter as tk
from tkinter import filedialog

import auswertung

size = 11
height = 1
file_path = ""

layout = [
    [sg.Text('pick path', size=(size,height), background_color="blue")],
    [sg.Text('selected path:', size=(size,height)), sg.InputText(pathlib.Path().resolve(), key="csv_root_filepath", size=(size + 50, height)),
     sg.Button("open path dialog", key="button_openfiledialog", size=(size, height))],
    [sg.Check('v', key='check_v', default=True, visible=False), sg.Check('c', key='check_c', default=True, visible=False)],
    # [sg.Button("generate", key="button_generate_plots", size=(size, height))],
    [sg.Text('ready', key='info', size=(size,height), background_color="green")]
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
            plot_factory = auswertung.Auswertung(file_path, True, True)
            win["info"].Update("processing....")
            await asyncio.sleep(0.1)
            success = await plot_factory.build()
            win["info"].Update("done")
            sg.Popup(success)
            sys.exit(1)
            window.close()
            #win["csv_root_filepath"].Update(file_path)

        if event == "button_generate_plots":
            i = 0

        await asyncio.sleep(0.1)

    window.close()
    sys.exit(1)
