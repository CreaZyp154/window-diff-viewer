# image_viewer.py
import io
import os
import PySimpleGUI as sg
import pywinctl as pwc
import PIL.ImageGrab, PIL.Image, PIL.ImageChops


def main():
    # 0 means none
    lookingForWindow = 0
    lastActiveWindow = 0
    
    window1 = None
    window2 = None

    # List of Channel operators
    chopsList = {
        "difference": "Difference",
        "subtract": "Subtract",
        "subtract_modulo": "Substract with modulo"
    }

    layout = [
        [sg.Image(key="ImageViewer")],
        [
            sg.Button("Select window", key="Window1Button"),
            sg.Button("Select window", key="Window2Button"),
        ],
        [
            sg.Text("Operator:"),
            sg.Combo(list(chopsList.values()), key="Operator", default_value=list(chopsList.values())[0]),
            sg.Checkbox("Show absolute difference", key="ShowAbsDiff"),
        ]
    ]
    window = sg.Window("Window Diff Viewer", layout)
    while True:
        event, values = window.read(timeout=10)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Window1Button":
            if window1 is None:
                if lookingForWindow != 1:
                    window.Element("Window1Button").update(text="Select a window or click again to cancel")
                    if lookingForWindow == 2:
                        window.Element("Window2Button").update(text="Select window")
                    
                    lookingForWindow = 1
                    
                elif lookingForWindow == 1:
                    window.Element("Window1Button").update(text="Select window")
                    lookingForWindow = 0
                
                
        if event == "Window2Button":
            if window2 is None:
                if lookingForWindow != 2:
                    window.Element("Window2Button").update(text="Select a window or click again to cancel")
                    if lookingForWindow == 1:
                        window.Element("Window1Button").update(text="Select window")
                    lookingForWindow = 2
                    
                elif lookingForWindow == 2:

                    window.Element("Window2Button").update(text="Select window")
                    lookingForWindow = 0

        if window1 is not None and window2 is not None:

            rect1 = window1.getClientFrame()
            rect2 = window2.getClientFrame()
            
            if rect1.top > 0 and rect2.top > 0:

                image1 = PIL.ImageGrab.grab(bbox=[rect1.left,rect1.top,rect1.right,rect1.bottom])
                image2 = PIL.ImageGrab.grab(bbox=[rect2.left,rect2.top,rect2.right,rect2.bottom])

                currentOperator = list(chopsList.keys())[list(chopsList.values()).index(window.Element("Operator").get())]

                merged = getattr(PIL.ImageChops, currentOperator)(image1, image2)

                if window.Element("ShowAbsDiff").get():
                    fn = lambda x : 255 if x > 0 else 0
                    merged = merged.convert("L").point(fn, "1")

                bio = io.BytesIO()
                merged.save(bio, format="PNG")
                
                window.Element("ImageViewer").update(data=bio.getvalue())
            if rect1.top == 0:
                window1 = None
                window.Element("Window1Button").update(text="Select window")
            if rect2.top == 0:
                window2 = None
                window.Element("Window2Button").update(text="Select window")
        
        if lookingForWindow != 0 and pwc.getActiveWindow() is not None and pwc.getActiveWindow().getHandle() != lastActiveWindow and lastActiveWindow != 0:
            if lookingForWindow == 1:
                window1 = pwc.getActiveWindow()
                window.Element("Window1Button").update(text=window1.title)
            else:
                window2 = pwc.getActiveWindow()
                window.Element("Window2Button").update(text=window2.title)
            print("Found window")
            lookingForWindow = 0
        elif lookingForWindow != 0 and lastActiveWindow == 0:
            lastActiveWindow = pwc.getActiveWindow().getHandle()
                
            
    window.close()

if __name__ == "__main__":
    main()