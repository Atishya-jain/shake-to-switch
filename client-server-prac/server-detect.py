#!/usr/bin/python           # This is server.py file

import platform
import os
import socket               # Import socket module
import psutil
import time
import pyautogui


PAUSE = 'Play/Pause'
BACKWARD = 'Left'
FORWARD = 'Right'
PREVIOUS = 'Hard-Left'
NEXT = 'Hard-Right'

FOCUS_MODE = False

apps = []
if platform.system() == 'Windows':
    import pywinauto
    import win32process
    import win32gui

    apps = ['POWERPNT.EXE', 'vlc.exe', 'chrome.exe', 'firefox.exe']  # in order of priority
elif platform.system() == 'Linux' or platform.system() == 'Darwin':
    apps = ['evince', 'vlc','chrome','firefox']

s = socket.socket()  # Create a socket object
# host = socket.gethostname() # Get local machine name
try:
    host = ((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
        [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
        [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
    # host=os.popen("hostname -I").read().split()[0]
    # host = "192.168.0.107"
    print(("host ip is: " + host))
except:
    print("Please connect to a network")
    exit()
else:
    port = 12346  # Reserve a port for your service.
    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.


def get_target_process():
    try:
        all_running_processes = psutil.pids()
        target_pid=-1
        target_name=""
        target_pid_list=[]
        target_name_list=[]
        is_chrome_added = False
        for pid in all_running_processes:
            for app in apps:
                if psutil.Process(pid).name()==app:
                    if app=='chrome' :
                        if psutil.Process(pid).environ()=={} and psutil.Process(pid).cmdline()[0].endswith('chrome') and (not is_chrome_added):
                            target_pid_list.append(pid)
                            target_name_list.append(app)
                            is_chrome_added=True
                        else:
                            continue
                    else:
                        target_pid_list.append(pid)
                        target_name_list.append(app)

        for app in apps:
            if app in target_name_list:
                target_name=app
                target_pid=target_pid_list[target_name_list.index(app)]
                break
        return (target_pid,target_name)
    except:
        return (-1,"")


def handle_signal_posix(signal_input,target_pid,target_name):
    try:
        if target_pid==-1:
            return
        window_id = os.popen("xdotool search --name "+ target_name).read().split()[-1]
        if target_name=='evince':
            pass
        elif target_name=='vlc':
            if signal_input==PAUSE:
                os.popen("xdotool windowactivate "+window_id+" && sleep 0.01 && xdotool key space && xdotool windowminimize "+window_id)
            elif signal_input==BACKWARD:
                os.popen("xdotool windowactivate "+window_id+" && sleep 0.01 && xdotool key shift+Right && xdotool windowminimize "+window_id)
            elif signal_input==FORWARD:
                os.popen("xdotool windowactivate "+window_id+" && sleep 0.01 && xdotool key shift+Left && xdotool windowminimize "+window_id)
            elif signal_input==PREVIOUS:
                os.popen("xdotool windowactivate "+window_id+" && sleep 0.01 && xdotool key p && xdotool windowminimize "+window_id)
            elif signal_input==NEXT:
                os.popen("xdotool windowactivate "+window_id+" && sleep 0.01 && xdotool key n && xdotool windowminimize "+window_id)
    except:
        pass


def handle_signal_focus(signal_input):
    if target_name.startswith('POWERPNT'):
        if signal_input == PAUSE:
            pyautogui.hotkey('shift', 'f5')
        elif signal_input == BACKWARD or signal_input == PREVIOUS:
            pyautogui.press('up')
        elif signal_input == FORWARD or signal_input == NEXT:
            pyautogui.press('down')
    elif target_name.startswith('vlc'):
        if signal_input == PAUSE:
            pyautogui.press('space')
        elif signal_input == BACKWARD:
            pyautogui.hotkey('shift', 'left')
        elif signal_input == FORWARD:
            pyautogui.hotkey('shift', 'right')
        elif signal_input == PREVIOUS:
            pyautogui.press('p')
        elif signal_input == NEXT:
            pyautogui.press('n')


if os.name == 'nt':
    import pywinauto

    def handle_signal_nt(signal_input, target_pid, target_name):
        try:
            if target_pid == -1:
                return
            app = pywinauto.application.Application()
            app.connect(path=target_name)
            app_dialog = app.top_window_()
            app_dialog.Restore()
            time.sleep(0.01)
            if target_name == 'AcroRd32.exe':
                if signal_input == BACKWARD:
                    pyautogui.press('left')
                elif signal_input == FORWARD:
                    pyautogui.press('right')
                elif signal_input == PREVIOUS:
                    pyautogui.press('left')
                    pyautogui.press('left')
                    pyautogui.press('left')
                    pyautogui.press('left')
                elif signal_input == NEXT:
                    pyautogui.press('right')
                    pyautogui.press('right')
                    pyautogui.press('right')
                    pyautogui.press('right')
            elif target_name == 'vlc.exe':
                if signal_input == PAUSE:
                    pyautogui.press('space')
                elif signal_input == BACKWARD:
                    pyautogui.hotkey('shift', 'left')
                elif signal_input == FORWARD:
                    pyautogui.hotkey('shift', 'right')
                elif signal_input == PREVIOUS:
                    pyautogui.press('p')
                elif signal_input == NEXT:
                    pyautogui.press('n')
            elif target_name == 'chrome.exe' or target_name == 'firefox.exe':
                if signal_input == PAUSE:
                    pyautogui.press('space')
            time.sleep(0.01)
            app_dialog.Minimize()
        except:
            pass

    def active_window_process_name_nt():
        pid = win32process.GetWindowThreadProcessId(
            win32gui.GetForegroundWindow())  # This produces a list of PIDs active window relates to
        return psutil.Process(pid[-1]).name()  # pid[-1] is the most likely to survive last longer


while True:
    #get the target process
    target_pid, target_name = get_target_process()
    print (target_pid, target_name)
    current = 'None'

    #get the input signal from client
    c, addr = s.accept()     # Establish connection with client.
    print(('Got connection from'+ str(addr)))
    signal_input = str(c.recv(1024).decode("UTF-8"))[2:]
    print(signal_input)
    # b = bytes('Thank you for connecting', 'utf-8')
    # c.send(b)
    c.close()                # Close the connection
    # check current foreground window
    if os.name == 'nt':
        current = active_window_process_name_nt()
    if current == target_name:
        FOCUS_MODE = True
    else:
        FOCUS_MODE = False
    print(FOCUS_MODE)
    # handle the input
    if FOCUS_MODE:
        handle_signal_focus(signal_input)
    else:
        if os.name == 'posix':
            handle_signal_posix(signal_input, target_pid, target_name)
        elif os.name == 'nt':
            handle_signal_nt(signal_input, target_pid, target_name)
