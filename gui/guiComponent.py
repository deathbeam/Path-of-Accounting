import os
from tkinter import *
import screeninfo
# We do not need this on Linux.
if os.name == "nt":
    import pythoncom
    import win32com.client
    import win32gui


def windowEnumerationHandler(hwnd, top_windows):
    """
    Handler for Windows OS enumeration of all open windows.
    Used to return to the Path of Exile window after displaying the overlay.
    """
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def windowToFront(root):
    # This is necessary for displaying the GUI window above active window(s) on the Windows OS
    if os.name == "nt":
        # In order to prevent SetForegroundWindow from erroring, we must satisfy the requirements
        # listed here:
        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow
        # We satisfy this by internally sending the alt character so that Windows believes we are
        # an active window.
        # We need this pythoncom call for win32com use in a thread.
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        win32gui.SetForegroundWindow(root.winfo_id())


def windowRefocus(name):
    """
    Restore focus to a window, if on Windows.
    TODO: If originating window was NOT "name", return to previous window.
    """

    if os.name == "nt":
        results = []
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for i in top_windows:
            if name == i[1].lower():
                win32gui.ShowWindow(i[0], 5)
                win32gui.SetForegroundWindow(i[0])
                break

class GuiComponent:
    def __init__(self):
        self.frame = None
        self.closed = True
    def prepare_window(self):
        tk = Tk().withdraw()
        frame = Toplevel()
        frame.overrideredirect(True)
        frame.option_add("*Font", "courier 12")
        frame.withdraw()
        self.frame = frame

    def is_closed(self):
        if self.closed:
            return True
        return False

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.frame.destroy()
        self.frame.update()
        self.frame = None
        windowRefocus("path of exile")
    def add_components(self):
        pass
    def show(self,x_cord, y_cord):
        self.closed = False
        self.prepare_window()
        self.add_components()
        windowToFront(self.frame)
        self.frame.deiconify()
        self.frame.geometry(f"+{x_cord}+{y_cord}")
        self.frame.update()

    def show_at_cursor(self):
        self.closed = False
        self.prepare_window()
        self.add_components()
        windowToFront(self.frame)
        
        self.frame.update()
        m_x = self.frame.winfo_pointerx()
        m_y = self.frame.winfo_pointery()
        def get_monitor_from_coord(x, y):
            monitors = screeninfo.get_monitors()
            for m in reversed(monitors):
                if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
                    return m
            return monitors[0]

        # Get the screen which contains top
        current_screen = get_monitor_from_coord(self.frame.winfo_x(), self.frame.winfo_y())
        # Get the monitor's size
        root_w = self.frame.winfo_width()
        root_h = self.frame.winfo_height()

        if m_x + root_w >= current_screen.width:
            m_x = current_screen.width - root_w - 5

        if m_y + root_h >= current_screen.height:
            m_y = current_screen.height - root_h - 5

        self.frame.deiconify()
        self.frame.geometry(f"+{m_x}+{m_y}")
        self.frame.update()

