from threading import Thread
from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard
from pynput.keyboard import Key


class AppMainKeyListener(QThread):
    keyInfo = pyqtSignal(str, tuple)

    def __init__(self, PCdata):
        super().__init__()
        self.KeyHook = None
        self.PC = PCdata

    def on_key_pressed(self, key):
        Keys = str(key.name if isinstance(key, Key) else key.char)
        if Keys == "tab":
            self.PC.StartFire = False
            Thread(target=self.PC.recognize_all_guns_info, args=(self.keyInfo.emit,)).start()
            self.keyInfo.emit('s', (self.PC.StartFire,))
        elif Keys in "12":
            self.PC.StartFire = False
            self.keyInfo.emit('s', (self.PC.StartFire,))
            self.PC.Change_firearms(Keys)
            self.keyInfo.emit('e', (self.PC.Current_firearms,))
        elif Keys in "345gx":
            self.PC.StartFire = False
            self.keyInfo.emit('s', (self.PC.StartFire,))
        elif Keys in "~":
            self.PC.StartFire = False
            self.keyInfo.emit('s', (self.PC.StartFire,))
        elif Keys in "zc" or Keys == "space":
            self.PC.Change_posture(Keys)
            self.keyInfo.emit('p', (self.PC.Current_posture,))
        elif Keys == "insert":
            self.PC.reduction_data()
            self.keyInfo.emit('c', (None,))
        elif Keys == "home":
            self.keyInfo.emit('t', (None,))
        elif Keys == "ctrl_l":
            self.PC.Current_posture = "c"
            self.keyInfo.emit('p', (self.PC.Current_posture,))
        elif Keys == "shift":
            self.PC.on_shift_pressed()
            self.keyInfo.emit('e', (self.PC.Current_firearms,))
    def on_key_release(self, key):
        Keys = str(key.name if isinstance(key, Key) else key.char)
        if Keys == "ctrl_l":
            self.PC.Current_posture = "None"
            self.keyInfo.emit('p', (self.PC.Current_posture,))
        elif Keys == "shift":
            self.PC.on_shift_released()
            self.keyInfo.emit('e', (self.PC.Current_firearms,))
    def run(self):
        self.rerun()

    def rerun(self):
        self.KeyHook = keyboard.Listener(on_press=self.on_key_pressed, on_release=self.on_key_release)
        self.KeyHook.start()
        self.keyInfo.emit('l', ("键盘监听已启动...",))

    def stop_listener(self):
        if self.KeyHook:
            self.KeyHook.stop()
            self.KeyHook = None
            self.keyInfo.emit('l', ("键盘监听已停止.....",))
