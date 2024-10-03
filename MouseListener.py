# -*- coding: utf-8 -*-
"""
@Time : 2024/2/20 14:51
@Author : hsxisawd
@File : MouseListener.py
@Project : Code
@Des:
"""
from threading import Thread
from PyQt5.QtCore import QThread, pyqtSignal
from pynput import mouse


class AppMainMouseListener(QThread):
    mouseClicked = pyqtSignal(str, tuple)
    
    def __init__(self, PCdata):
        super().__init__()
        self.listener = None
        self.data = []
        self.PC = PCdata
        self.count = 1

    def on_button_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.PC.mouse_one = pressed
            if pressed and self.PC.StartFire:
                self.mouseClicked.emit('l', (f"开始第{self.count}次压枪",))
                Thread(target=self.PC.FIRE_Start, args=(self.mouseClicked.emit,)).start()
                self.count += 1
        elif button == mouse.Button.right:
            if not self.PC.TabKey:
                if self.PC.RightClick:
                    if pressed:
                        self.PC.StartFire = True
                    else:
                        self.PC.StartFire = False

                else:
                    if pressed:
                        Thread(target=self.PC.IF_Open_Lens).start()
                self.mouseClicked.emit('s', (self.PC.StartFire,))

        elif button == mouse.Button.x1 or button == mouse.Button.x2:
            if pressed:
                self.PC.StartFire = False
            else:
                self.PC.StartFire = False
            self.mouseClicked.emit('s', (self.PC.StartFire,))

    def run(self):
        self.rerun()
    
    def rerun(self):
        self.listener = mouse.Listener(on_click=self.on_button_click)
        self.listener.start()
        self.mouseClicked.emit("l", ("鼠标监听已启动...",))
    
    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.mouseClicked.emit("l", ("鼠标监听已结束...",))
