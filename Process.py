import simplejson as json
import os
import sys
import threading
import time
from GHUB import ghub_device
from recognition import capture_all_positions_thread, recogniseif_firearm
from fire_data import KEY_DATA
import asyncio
import numpy as np
import numba

class ProcessClass:
    _instance_lock = threading.Lock()
    _Result1 = {}  # 1号枪的识别结果[]
    _Result2 = {}  # 2号枪的识别结果
    _gd = ghub_device()

    @classmethod
    def get_recognition_results(cls):
        return cls._Result1, cls._Result2

    def __new__(cls, *args, **kwargs):
        if not hasattr(ProcessClass, "_instance"):
            with ProcessClass._instance_lock:
                if not hasattr(ProcessClass, "_instance"):
                    # 类加括号就回去执行__new__方法，__new__方法会创建一个类实例：Singleton()
                    ProcessClass._instance = object.__new__(cls)  # 继承object类的__new__方法，类去调用方法，说明是函数，要手动传cls
        return ProcessClass._instance  # obj1

    def __init__(self):
        self.TabKey = False
        self.ghub_device_info = self._gd.info
        self.window_version = self.get_window_version()
        self.Monitor = self.get_config_data("r")
        self.mouse_one = False  # 是否开枪
        self.Current_firearms = None  # 当前枪械 1号枪2号枪
        self.Current_posture = "None"  # 当前姿态 None 站立 z 趴下 c 蹲下
        self.sensitivity = 1  # 瞄准灵敏度
        self.StartFire = False  # 是否开枪倍镜
        self.RightClick = False  # 右键按下模式 False 单击 True 长按
        self.clicking = False
        self.shift_pressed = False  # 记录 Shift 键是否按下
        self.ScopeData = self.get_config_data('s')
        self.GunsName = None
        self.added = False

    def move_mouse(self, x, y):
        self._gd.mouse_R(x, y)

    def get_config_data(self, mode='r'):
        with open('./Config/config.json', "r", encoding='utf-8') as Config:
            Config_data = json.loads(Config.read())
            if mode == 'r':
                return Config_data["resolution"]
            elif mode == 's':
                return Config_data['sensitivity']
            elif mode == 'a':
                return Config_data

    def save_config_data(self, mode, data):
        save_data = self.get_config_data('a')
        if mode:
            save_data['resolution'] = data
        else:
            save_data['sensitivity'] = data
        with open('./Config/config.json', "w", encoding='utf-8') as Config:
            Config.write(json.dumps(save_data))

    def reduction_data(self):
        self.StartFire = False
        self.clicking = False
        self.sensitivity = 1
        self.Current_posture = "None"
        self.Current_firearms = None
        self.mouse_one = False
        self.TabKey = False
        self._Result1 = {}
        self._Result2 = {}

    def read_gun_data(self, fileName) -> dict:
        if not os.path.exists(f'./_internal/GunData/{fileName}.json'):
            return
        with open(f'./_internal/GunData/{fileName}.json', "r", encoding='utf-8') as GUNS:
            GUNS_data = json.loads(GUNS.read())
            return GUNS_data

    def get_current_scope(self):
        result = self.get_guns_info()
        if result is None:
            return "none"
        else:
            return result["Scope"]

    def shift_multiplier(self):
        # 读取配置文件中的 shift 变量

        shift_scpoe = float(self.ScopeData.get('shift', 0))
        # 判断 Shift 键是否按下
        if self.shift_pressed and shift_scpoe:
            # 增加长按shift的倍率
            if self.Current_firearms and self.StartFire:
                if not self.added:
                    # 判断当前是否装备了枪械并且正在开镜
                    accessor_scope = self.get_current_scope()
                    if accessor_scope == 'hongdian':  # 如果当前是红点
                        self.ScopeData['hongdian'] += shift_scpoe  # 增加红点倍率
                    elif accessor_scope == 'quanxi':  # 如果当前是全息
                        self.ScopeData['quanxi'] += shift_scpoe  # 增加全息镜倍率
                    elif accessor_scope == 'none':  # 如果当前是机瞄
                        self.ScopeData['none'] += shift_scpoe  # 增加机瞄倍率
                    self.added=True

    def on_shift_pressed(self):
        self.shift_pressed = True
        self.shift_multiplier()

    def on_shift_released(self):
        self.shift_pressed = False
        sensitivity_data = self.get_config_data('s')
        self.ScopeData = sensitivity_data
        self.added=False
    def get_window_version(self):
        windows_version = sys.getwindowsversion()
        if windows_version.build >= 22000:
            return True
        return False

    def get_guns_result(self):
        """
        获取枪械识别结果
        :return:
        """
        return [self._Result1, self._Result2]

    def recognize_all_guns_info(self, Emit):
        """
        枪械配件识别
        :return:
        """
        Data = asyncio.run(capture_all_positions_thread(self.Monitor))
        self._Result1 = Data[0]
        self._Result2 = Data[1]
        Emit('g', (None,))

    def Change_firearms(self, keyWord):
        """
        枪械切换
        :param keyWord:按键编码
        :return:
        """
        if keyWord == "x":
            self.Current_firearms = None
        else:
            self.Current_firearms = int(keyWord)

    def IF_Open_Lens(self):
        self.StartFire = recogniseif_firearm(self.Monitor)

    def Change_posture(self, keyWord):
        """
        姿势切换
        :param keyWord:按键编码
        :return:
        """
        if keyWord == "space" or self.Current_posture == keyWord:
            self.Current_posture = "None"
        else:
            self.Current_posture = keyWord

    def calculate_the_recoil(self, recoil, posture, scope):
        """
        计算最终后坐力参数
        :param recoil: 压枪弹道数据
        :param posture: 姿态数据
        :param scope: 倍镜数据
        :return:
        """
        # 最终弹道 = 姿态 * （基础弹道*倍镜）
        recoil_value = (posture * (recoil * scope))

        return np.round(recoil_value)  # 返回整数后坐力值

    def get_guns_info(self):
        if self.Current_firearms == 1:
            return self._Result1
        elif self.Current_firearms == 2:
            return self._Result2
        else:
            return None

    def FIRE_Start(self, Emit):

        # 判断数据是否准确
        Judge_List = (self.StartFire, self.Current_firearms, self._Result1, self._Result2)
        LogInfo_List = ("当前没有开启倍镜，无需压枪", "当前没有装备枪械，无需压枪", "还未进行枪械识别，无需压枪",
                        "还未进行枪械识别，无需压枪")
        for i in range(len(Judge_List)):
            if not Judge_List[i]:
                return Emit("l", (LogInfo_List[i],))

        # 获取当前枪械识别情况数据
        guns_info = self.get_guns_info()
        if not guns_info:
            return Emit("l", ("当前装备不是枪械，无需压枪",))
        # 获取枪械名称
        gunsName = guns_info.get("Name", "None")
        if gunsName == "None" or not gunsName:
            return Emit("l", ("未检测到枪械",))
        # 获取枪械数据 枪械对应json数据
        gun = self.read_gun_data(gunsName)
        if not gun:
            return Emit("l", ("枪械数据不存在",))

        # 获取配件码
        NameCode = self.get_accessories_nameCode(guns_info)
        # 获取弹道数据
        ballistic = gun.get(NameCode, [])
        # 获取姿态数据
        Posture = gun.get(self.Current_posture.lower(), 1)
        # 获取倍镜数据
        accessor_scope = guns_info.get("Scope", "None").lower()
        Scope = self.ScopeData.get(accessor_scope, 1)
        # 判断是否为非连点枪械
        Not_Guns = ["sks", "mini14", "delagongnuofu", "m16a4", "mk12", "mk47", "qbu", "zidongzhuangtianbuqiang"]
        if gunsName in Not_Guns:
            return self.FIRE1(Posture, Scope, ballistic, Emit)
        else:
            return self.FIRE(Posture, Scope, ballistic, Emit)

    def get_accessories_nameCode(self, guns_info):
        """
        获取配件名称
        :param guns_info:识别枪械的数据
        :return:
        """
        NameCode = ""
        type_dict = {"Muzzle": "A", "Grip": "B", "Stock": "C"}
        for name, value in type_dict.items():
            accessories = guns_info.get(name, "None").lower()
            code_num = KEY_DATA[name][accessories]
            NameCode += value + code_num
        return NameCode

    def Computation_latency(self, latency):
        if self.window_version:
            return (latency - 0) / 1000
        return latency / 1000

    def FIRE(self, posture, scope, ballistic, Emit):
        recoil_list = []  # 创建一个空列表用于存储 recoil 数据
        for i in ballistic:
            if not self.mouse_one:
                break
            Emit('x', (True,))
            recoil = self.calculate_the_recoil(i, posture, scope)
            # print(recoil, end=", ")  # 打印 recoil，并在末尾加上逗号和空格
            recoil_list.append(recoil)  # 将每次迭代得到的 recoil 添加到列表中
            self._gd.mouse_R(0, recoil)
            latency = self.Computation_latency(9)
            time.sleep(latency)
        Emit('x', (False,))
        return recoil_list

    def FIRE1(self, posture, scope, ballistic, Emit):
        recoil_list = []  # 创建一个空列表用于存储 recoil 数据
        for i in ballistic:
            if not self.mouse_one:
                break
            Emit('x', (True,))
            recoil = self.calculate_the_recoil(i, posture, scope)
            # print(recoil, end=", ")  # 打印 recoil，并在末尾加上逗号和空格
            recoil_list.append(recoil)  # 将每次迭代得到的 recoil 添加到列表中
            self._gd.mouse_R(0, recoil)
            latency = self.Computation_latency(100)
            time.sleep(latency)
        Emit('x', (False,))
        return recoil_list
