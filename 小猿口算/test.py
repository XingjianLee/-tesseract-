import pyautogui
import pytesseract
import cv2
from PIL import Image, ImageOps
import time
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

region_all = (420, 503, 450, 100)
start_x, start_y = 633, 1173


# 图像预处理函数 - 转换为灰度图并二值化，自适应处理并增加去噪
def preprocess_image(image):
    # 转换为灰度图
    image = image.convert('L')
    # 转换为OpenCV格式进行进一步处理
    open_cv_image = np.array(image)

    # 自适应阈值化处理，更好地应对不同光线情况
    _, open_cv_image = cv2.threshold(open_cv_image, 128, 255, cv2.THRESH_BINARY)
    # 中值滤波去噪，增强图像的平滑度，减少 OCR 错误
    open_cv_image = cv2.medianBlur(open_cv_image, 1)

    # 将处理后的图像重新转换为PIL格式
    final_image = Image.fromarray(open_cv_image)
    return final_image


# 多次比较循环
for i in range(20):
    # 截取整个包含数字的区域
    screenshot_all = pyautogui.screenshot(region=region_all)

    # 定义相对于 region_all 的两个数字的裁剪区域，转化为左上角和右下角
    num1_region = (26, 0, 115, 73)  # 第一个数字相对于截取的整个区域的坐标 (x, y, width, height)
    num2_region = (305, 0, 120, 73)  # 第二个数字相对于截取的整个区域的坐标 (x, y, width, height)

    # PIL的crop需要的是 (left, upper, right, lower)
    num1_left, num1_top = num1_region[0], num1_region[1]
    num1_right, num1_bottom = num1_left + num1_region[2], num1_top + num1_region[3]

    num2_left, num2_top = num2_region[0], num2_region[1]
    num2_right, num2_bottom = num2_left + num2_region[2], num2_top + num2_region[3]

    # 裁剪出两个数字的区域
    screenshot_num1 = screenshot_all.crop((num1_left, num1_top, num1_right, num1_bottom))
    screenshot_num2 = screenshot_all.crop((num2_left, num2_top, num2_right, num2_bottom))

    # 进行图像预处理
    screenshot_num1 = preprocess_image(screenshot_num1)
    screenshot_num2 = preprocess_image(screenshot_num2)

    if i == 0:
        screenshot_num1.save(f"screenshot_num1_{i}.png")
        screenshot_num2.save(f"screenshot_num2_{i}.png")

    # OCR 识别
    config = '--psm 7 -c tessedit_char_whitelist=0123456789'
    num1_text = pytesseract.image_to_string(screenshot_num1, config=config)
    num2_text = pytesseract.image_to_string(screenshot_num2, config=config)

    try:
        # 转换为整数进行比较
        num1 = int(num1_text.strip())
        num2 = int(num2_text.strip())
        print(num1, num2)

        # 根据比较结果绘制大于号或小于号
        if num1 > num2:
            result = ">"
        else:
            result = "<"

        print(f"第{i + 1}次比较: {num1} {result} {num2}")
        pyautogui.moveTo(start_x, start_y)

        if result == "<":
            # 绘制大于号
            pyautogui.mouseDown()
            pyautogui.dragTo(start_x - 30, start_y - 30, duration=0)
            pyautogui.dragTo(start_x, start_y - 60, duration=0)
            pyautogui.mouseUp()
        elif result == ">":
            # 绘制小于号
            pyautogui.mouseDown()
            pyautogui.dragTo(start_x + 30, start_y - 30, duration=0)
            pyautogui.dragTo(start_x, start_y - 60, duration=0)
            pyautogui.mouseUp()

    except ValueError:
        print(f"第{i + 1}次比较时发生错误，无法识别数字")

    time.sleep(0.2)
