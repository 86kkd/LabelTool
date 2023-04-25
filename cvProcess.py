import cv2
import numpy as np
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *


def qpixmap_to_cvimg(q_pixmap):
    """_summary_

    Args:
        q_pixmap (_type_): _description_

    Returns:
        _type_: _description_
    """
    q_image = q_pixmap.toImage()
    buffer = q_image.bits().asstring(q_image.byteCount())
    width = q_image.width()
    height = q_image.height()
    return np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))


def channel_th(r, g, b, threshold):
    r_binary = cv2.threshold(r, threshold['r'], 255, cv2.THRESH_BINARY)[1]
    g_binary = cv2.threshold(g, threshold['g'], 255, cv2.THRESH_BINARY)[1]
    b_binary = cv2.threshold(b, threshold['b'], 255, cv2.THRESH_BINARY)[1]
    # circle_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 膨胀
    # r_binary = cv2.erode(r_binary, circle_kernel, iterations=1)
    # g_binary = cv2.erode(g_binary, circle_kernel, iterations=2)
    # b_binary = cv2.erode(b_binary, circle_kernel, iterations=2)
    # r_binary = cv2.erode(r_binary, circle_kernel, iterations=1)
    # g_binary = cv2.dilate(g_binary, circle_kernel, iterations=2)
    # b_binary = cv2.dilate(b_binary, circle_kernel, iterations=4)
    return r_binary, g_binary, b_binary


def cvDetect(image, threoloads: dict,mode,offset: QPointF=None) -> np.array:
    # sourcery skip: hoist-statement-from-if, low-code-quality
    """
    @summary : 通过图片基本操作进行轮廓提取
    @param image:
    @param offset:
    @return:
    """
    if type(image) == np.ndarray:
        # 将图像转换为RGB颜色空间
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif type(image) == QPixmap:
        img_cv = qpixmap_to_cvimg(image)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    else:
        raise 'input type error' 
    # 分割RGB通道
    if mode == 'blue':
        r, g, b = cv2.split(img_rgb)  # 分离色彩通道
    elif mode == 'red':
        b, g, r = cv2.split(img_rgb) 
    threshold = {'r': threoloads['red'], 'g': threoloads['green'], 'b': threoloads['blue']}
    r_th, g_th, b_th = channel_th(r, g, b, threshold)
    b_and_g = b_th & g_th
    circle_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    b_and_g_o = cv2.morphologyEx(b_and_g, cv2.MORPH_OPEN, circle_kernel, iterations=1)  # 开运算
    # cv2.imshow("b_th_o", b_and_g_o)
    final_img = b_and_g_o & cv2.bitwise_not(r_th)
    # cv2.imshow("final img", final_img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    thres = {
        "th_result" :  final_img,
        "r_th" : r_th,
        "g_th" : g_th,
        "b_th" : b_th
    }
    contours, hierarchy = cv2.findContours(final_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 找到凸多边形并绘制
    if len(contours) == 0:
        return None ,thres
    try:
        all_contours = np.concatenate(contours)
        hull = cv2.convexHull(all_contours)
    except:
        print("detect error: may be thresload error")
        return None, thres
    # 用4条边的多边形逼近凸包
    epsilon = 0.02 * cv2.arcLength(hull, True)
    while True:
        approx = cv2.approxPolyDP(hull, epsilon, True)
        if len(approx) == 4:
            four_edge_polys = approx
            break
        elif len(approx) < 4:
            epsilon -= 1
        elif len(approx) > 4:
            return None ,thres
    if offset:
        offset = np.array([offset.x(), offset.y()])
        four_edge_polys = np.squeeze(four_edge_polys)
        four_edge_polys = four_edge_polys + offset
    key_points = np.array([four_edge_polys[3], four_edge_polys[2], four_edge_polys[1], four_edge_polys[0]])
    
    return key_points ,thres





