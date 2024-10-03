import sys
import fire_data
import Process
from PyQt5.QtCore import QThread, Qt, pyqtSignal, QEvent
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QMainWindow
from PUBG_UI import Ui_PUBG
from MouseListener import AppMainMouseListener
from KeyListener import AppMainKeyListener

class AppManager(QWidget, Ui_PUBG):
    def __init__(self):
        super().__init__()
        self.isHidden = None
        self.my_mouse_thread = None
        self.my_key_thread = None
        self.pauses = True
        self.TextValue = {'无': 'none', '红点': 'hongdian', '全息': "quanxi", '2倍': '2bei',
                          '3倍': '3bei', '4倍': "4bei", '6倍': '6bei', '8倍': '8bei', '15倍': '15bei', 'shift': 'shift'}
        self.init_ui()

    def init_ui(self):
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.Init_UI_LOG("程序初始化中.....")
        self.Init_UI_LOG(PC.ghub_device_info)
        self.Init_UI_Win()
        # self.Init_UI_iniFile()
        self.Init_UI_Equip(PC.Current_firearms)
        self.Init_UI_Posture(PC.Current_posture)
        self.Init_UI_ScopeMode(PC.RightClick)
        self.Init_UI_ScopeOpen(PC.StartFire)
        self.Init_UI_GunsData()
        self.ResolutionSelect.setCurrentText(PC.Monitor)
        self.Init_UI_Sensitivity()
        self.Init_UI_Btn()
        self.Init_UI_LOG("程序初始化完成.....")
    
    def Init_UI_Btn(self):
        self.Startbtn.clicked.connect(self.start)
        self.Stopbtn.clicked.connect(self.stop)
        self.Pausebtn.clicked.connect(self.pause)
        self.ResolutionBtn.clicked.connect(self.Save_Config_Resolution)
        self.SensitivityBtn.clicked.connect(self.Save_Config_Sensitivity)
        self.OpenScope.clicked.connect(lambda: self.Btn_click("ScopeOpen", True))
        self.CloseScope.clicked.connect(lambda: self.Btn_click("ScopeOpen", False))
        self.TwoGuns.clicked.connect(lambda: self.Btn_click("Guns", 2))
        self.OneGuns.clicked.connect(lambda: self.Btn_click("Guns", 1))
        self.Orders.clicked.connect(lambda: self.Btn_click("Guns", "x"))
        self.Stand.clicked.connect(lambda: self.Btn_click("Posture", 'space'))
        self.GetDown.clicked.connect(lambda: self.Btn_click("Posture", 'z'))
        self.SquatDown.clicked.connect(lambda: self.Btn_click("Posture", 'c'))
        self.LongPress.clicked.connect(lambda: self.Btn_click("ScopeMode", True))
        self.ClickPress.clicked.connect(lambda: self.Btn_click("ScopeMode", False))
    
    def Init_UI_Win(self):
        if PC.window_version:
            version = "(Win11版)"
        else:
            version = "(Win10版)"
        
        self.WinVersion.setText(version)
    
    def Btn_click(self, key, value):
        """
        按钮点击事件
        """
        if key == "Guns":
            PC.Change_firearms(value)
        elif key == "Posture":
            PC.Change_posture(value)
        elif key == "ScopeMode":
            PC.RightClick = value
        elif key == "ScopeOpen":
            PC.StartFire = value
    
    def toggle_window(self):
        if self.isHidden:
            self.show()
            self.isHidden = False
        else:
            self.hide()
            self.isHidden = True
    
    def Get_GUNS_CH(self, Name, Type):
        """
        加载配件汉化文件
        :return:
        """
        CH_data = fire_data.ACCESSORIES_CH.get(Type, None)
        Default = Name if Type == "Name" else "未知"
        if CH_data:
            return CH_data.get(Name.lower(), Default)
        else:
            return "未知"
    
    def Init_UI_Equip(self, Current_firearms):
        """
        修改UI当前枪械的数据
        :param Current_firearms: 当前枪械
        """
        if Current_firearms == 2:
            self.TwoGuns.setChecked(True)
        elif Current_firearms == 1:
            self.OneGuns.setChecked(True)
        else:
            self.Orders.setChecked(True)
    
    def Init_UI_Posture(self, Current_posture):
        """
        修改UI当前姿态的数据
        :param Current_posture: 当前姿态
        """
        if Current_posture == "None":
            self.Stand.setChecked(True)
        
        elif Current_posture == "z":
            self.GetDown.setChecked(True)
        elif Current_posture == "c":
            self.SquatDown.setChecked(True)
    
    def Init_UI_ScopeMode(self, mode):
        """
        修改UI当前开镜模式
        :param mode: 当前开镜模式
        """
        if mode:
            self.LongPress.setChecked(True)
        else:
            self.ClickPress.setChecked(True)
    
    def Init_UI_ScopeOpen(self, Open):
        """
        修改UI当前是否开镜数据
        :param Open: 是否开镜数据
        """
        if Open:
            self.OpenScope.setChecked(True)
        else:
            self.CloseScope.setChecked(True)
    
    def Init_UI_GunsData(self):
        """
        修改UI 的识别结果
        :return:
        """
        results = PC.get_guns_result()
        for idx, result in enumerate(results, start=1):
            if result:
                self.__getattribute__(f"Name{idx}Name").setText(self.Get_GUNS_CH(result["Name"], "Name"))
                self.__getattribute__(f"Scope{idx}Name").setText(self.Get_GUNS_CH(result["Scope"], "Scope"))
                self.__getattribute__(f"Muzzle{idx}Name").setText(self.Get_GUNS_CH(result["Muzzle"], "Muzzle"))
                self.__getattribute__(f"Grip{idx}Name").setText(self.Get_GUNS_CH(result["Grip"], "Grip"))
                self.__getattribute__(f"Butt{idx}Name").setText(self.Get_GUNS_CH(result["Stock"], "Stock"))
    
    def Init_UI_Sensitivity(self):
        SelectValue = self.SensitivitySelect.currentText()
        self.Change_Sensitivity_label(SelectValue)
        self.SensitivitySelect.currentIndexChanged[str].connect(self.Change_Sensitivity_label)
    
    def Init_UI_ReductionData(self):
        self.Init_UI_Equip(PC.Current_firearms)
        self.Init_UI_Posture(PC.Current_posture)
        self.Init_UI_ScopeMode(PC.RightClick)
        self.Init_UI_ScopeOpen(PC.StartFire)
        self.Init_UI_GunsData()
    
    def Init_UI_LOG(self, info):
        self.Info.append(info + "\n")
    
    def Change_Sensitivity_label(self, SelectValue):
        Text = self.TextValue
        Select = PC.ScopeData.get(Text[SelectValue], '1')
        self.SensitivityText.setText(str(Select))
    
    def Save_Config_Resolution(self):
        PC.Monitor = self.ResolutionSelect.currentText()
        PC.save_config_data(True, PC.Monitor)
        self.message_Info("保存分辨率设置成功！！")
    
    def Save_Config_Sensitivity(self):
        SensitivityText = self.SensitivityText.text()
        SensitivityText = self.is_numeric(SensitivityText)
        if not SensitivityText:
            self.message_Info("输入框只能输入数字！！", '警告')
            return
        
        SensitivitySelect = self.SensitivitySelect.currentText()
        Text = self.TextValue[SensitivitySelect]
        PC.ScopeData[Text] = SensitivityText
        PC.save_config_data(0, PC.ScopeData)
        self.message_Info("保存灵敏度设置成功！！")
    
    def message_Info(self, message, title="提示信息"):
        message_box = QMessageBox()
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowFlags(message_box.windowFlags() | Qt.WindowStaysOnTopHint)
        message_box.exec()
    
    def is_numeric(self, string):
        try:
            if '.' in string:
                return float(string)
            else:
                return int(string)
        except ValueError:
            return False
    
    def start(self):
        self.my_key_thread = AppMainKeyListener(PC)
        self.my_mouse_thread = AppMainMouseListener(PC)
        self.my_key_thread.start()
        self.my_mouse_thread.start()
        
        self.my_key_thread.keyInfo.connect(self.onKeyPressed)
        self.my_mouse_thread.mouseClicked.connect(self.onKeyPressed)
        
        self.SetStatus()
        self.StatusInfo.setText('程序运行中.....')
    
    def SetStatus(self):
        self.Startbtn.setEnabled(False)
        self.Pausebtn.setEnabled(True)
        self.Stopbtn.setEnabled(True)
        self.EquipBox.setEnabled(True)
        self.PoseBox.setEnabled(True)
        self.IsScope.setEnabled(True)
    
    def stop(self):
        self.StatusInfo.setText('程序退出中....')
        self.my_key_thread.stop_listener()
        self.my_mouse_thread.stop_listener()
        self.my_key_thread.terminate()
        self.my_mouse_thread.terminate()
        
        QApplication.quit()
    
    def pause(self):
        if self.pauses:
            self.my_key_thread.stop_listener()
            self.my_mouse_thread.stop_listener()
            self.Pausebtn.setText("继续")
            self.StatusInfo.setText('程序暂停中....')
            self.pauses = False
        else:
            self.my_key_thread.rerun()
            self.my_mouse_thread.rerun()
            self.Pausebtn.setText("暂停")
            self.StatusInfo.setText('程序运行中....')
            self.pauses = True
    
    def onKeyPressed(self, key, value):
        values = value[0]
        actions = {
            "l": (self.Init_UI_LOG, [values]),
            "s": (self.Init_UI_ScopeOpen, [values]),
            "g": (self.Init_UI_GunsData, []),
            "e": (self.Init_UI_Equip, [values]),
            "p": (self.Init_UI_Posture, [values]),
            "c": (self.Init_UI_ReductionData, []),
            "t": (self.toggle_window, [])
        }
        
        action, args = actions.get(key, (None, None))
        if action:
            action(*args)

if __name__ == '__main__':
    app = QApplication([])
    PC = Process.ProcessClass()
    Main = AppManager()
    # 展示窗口
    Main.show()
    sys.exit(app.exec_())