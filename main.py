import numpy
import matplotlib
import asyncio
import simple_gui as gui



async def main():
    instance_list = [

        # gui
        gui.main_window()
    ]

    await asyncio.gather(
        *instance_list
    )

    while True:

        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run((main()))

