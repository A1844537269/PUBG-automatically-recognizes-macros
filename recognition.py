import cv2
import mss
import os
import time
import pyautogui
import asyncio
from numba import jit
from resolution_setting import RESOLUTION_SETTINGS, GUNS_REOLUTION_SETTINGS, Click
import numpy as np


def MSS_Img(Values):
    x1, y1, x2, y2 = Values
    with mss.mss() as sct:
        monitor = {"top": x1, "left": y1, "width": x2, "height": y2}
        img = sct.grab(monitor)
        img_np = np.array(img)  # 转换为numpy数组
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
    return img_gray

@jit(nopython=True)
def compute_matches_mask(matches, distance_threshold):
    matchesMask = np.zeros((len(matches), 2), dtype=np.int32)
    matchedPoints1 = 0

    for i in range(len(matches)):
        m, n = matches[i]
        if m.distance < distance_threshold * n.distance:
            matchesMask[i, 0] = 1
            matchedPoints1 += 1

    return matchesMask, matchedPoints1

def match_sift(img1, img2):
    # 创建sift检测器
    sift = cv2.SIFT_create()

    # 查找监测点和匹配符
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    if des1 is not None and len(des1) > 2 and des2 is not None and len(des2) > 2:
        # 使用FlannBasedMatcher匹配
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        # 使用knnMatch匹配处理，并返回匹配matches
        matches = flann.knnMatch(des1, des2, k=2)

        # 通过掩码方式计算有用的点
        matches_array = np.array([[m, n] for m, n in matches], dtype=np.object)

        matchesMask, matchedPoints1 = compute_matches_mask(matches_array, 0.7)

        totalPoints = len(kp1)
        matchRate = matchedPoints1 / (totalPoints + 0.1)

        return matchRate

    return 0

async def capture_and_compare(Data, imgs):
    Keys = list(Data.keys())[0]
    Values = list(Data.values())[0]
    x1, y1, x2, y2 = Values
    roi = imgs[y1:y2, x1:x2]
    return Keys, roi

async def capture_all_guns(pathData):
    ReturnData = {}
    for mode, img1 in pathData.items():
        match_Path = f"_internal/data/firearms/{mode[:-2]}/"
        content = os.listdir(match_Path)
        MatchValue = 0.0
        MatchName = ""
        for each in content:
            demo_dir = match_Path + each
            img2 = cv2.imread(demo_dir, cv2.IMREAD_GRAYSCALE)  # 以灰度模式读取图像
            part = match_sift(img1, img2)
            if part > MatchValue:
                MatchName = each[:-4]
                MatchValue = part
        if MatchValue <= 0.0 and not MatchName:
            MatchName = "None"
        ReturnData[mode[:-2]] = MatchName
    return ReturnData

async def capture_all_positions_thread(current_res):
    start_time = time.time()  # 记录开始时间

    Guns_imgs = GUNS_REOLUTION_SETTINGS[current_res]
    Guns_img = RESOLUTION_SETTINGS[current_res]
    # 捕获完整图像
    Images = MSS_Img(Guns_imgs)
    # 创建异步任务来直接在内存中捕获和处理图像
    tasks = [capture_and_compare({k: v}, Images) for k, v in Guns_img.items()]
    captured_images = await asyncio.gather(*tasks)

    # 将捕获的图像数据分组
    Guns1 = {k: img for k, img in captured_images[0:5]}
    Guns2 = {k: img for k, img in captured_images[5:10]}

    # 对这些图像进行进一步处理
    ReturnData = await asyncio.gather(
        capture_all_guns(Guns1),
        capture_all_guns(Guns2)
    )

    elapsed_time = time.time() - start_time  # 计算总耗时
    print(f"Time from capture to recognition: {elapsed_time:.2f} seconds")  # 打印总耗时

    return ReturnData

def recogniseif_firearm(current_res):
    x1, x2 = Click.get(current_res, None)
    r, g, b = pyautogui.pixel(x1, x2)
    S_Max, S_Min = 255, 200
    if S_Min <= g <= S_Max and S_Min <= r <= S_Max and S_Min <= b <= S_Max:
        return True
    else:
        return False

