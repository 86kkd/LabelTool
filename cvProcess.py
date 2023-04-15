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
    circle_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # 膨胀
    r_binary = cv2.erode(r_binary, circle_kernel, iterations=1)
    # g_binary = cv2.erode(g_binary, circle_kernel, iterations=2)
    # b_binary = cv2.erode(b_binary, circle_kernel, iterations=2)
    r_binary = cv2.erode(r_binary, circle_kernel, iterations=1)
    # g_binary = cv2.dilate(g_binary, circle_kernel, iterations=2)
    # b_binary = cv2.dilate(b_binary, circle_kernel, iterations=4)
    return r_binary, g_binary, b_binary




def channel_sub(img_rgb, r, g, b, red_color):
    """

    @param img_rgb:
    @param r:
    @param g:
    @param b:
    @param red_color:
    @return:
    """
    # 色彩分离二值化阈值-绿色
    separationThreshold_GREEN = 30

    gray_img = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)  # 获取灰度图
    white_img = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY)[1]
    white_img = cv2.bitwise_not(white_img)
    if red_color:
        # 灰度二值化阈值-红色
        grayThreshold_RED = 90
        # 敌方为红色
        gray_img = cv2.threshold(gray_img, grayThreshold_RED, 255, cv2.THRESH_BINARY)[1]  # 灰度二值化
        r_sub_b = cv2.subtract(r, b)  # 红蓝通道相减
        r_sub_g = cv2.subtract(r, g)  # 红绿通道相减
        # 色彩分离二值化阈值-红色
        separationThreshold_RED = 100
        r_sub_b = cv2.threshold(r_sub_b, separationThreshold_RED, 255, cv2.THRESH_BINARY)[1]  # 红蓝二值化
        r_sub_g = cv2.threshold(r_sub_g, separationThreshold_GREEN, 255, cv2.THRESH_BINARY)[
            1]  # 红绿二值化
        r_sub_b = cv2.dilate(r_sub_b, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        r_sub_g = cv2.dilate(r_sub_g,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))  # 膨胀

        final_sub = r_sub_b & gray_img & r_sub_g & white_img  # 逻辑与获得最终二值化图像
            # cv2.morphologyEx(_maxColor, _maxColor, cv2.MORPH_OPEN,  kernel3)
    else:
        # 灰度二值化阈值-紫色
        grayThreshold_PURPLE = 100
        # 敌方为蓝色
        _purpleSrc = cv2.threshold(r, grayThreshold_PURPLE, 255, cv2.THRESH_BINARY)[1]
        _purpleSrc = cv2.bitwise_not(_purpleSrc)

        # 灰度二值化阈值-蓝色
        grayThreshold_BLUE = 40
        gray_img = cv2.threshold(gray_img, grayThreshold_BLUE, 255, cv2.THRESH_BINARY)[1]  # 灰度二值化
        r_sub_b = cv2.subtract(b, r)  # 蓝红通道相减
        r_sub_g = cv2.subtract(b, g)  # 蓝绿通道相减
        # 色彩分离二值化阈值-蓝色
        separationThreshold_BLUE = 40
        r_sub_b = cv2.threshold(r_sub_b, separationThreshold_BLUE, 255, cv2.THRESH_BINARY)[1]  # 蓝红二值化
        r_sub_g = cv2.threshold(r_sub_g, separationThreshold_GREEN, 255, cv2.THRESH_BINARY)[
            1]  # 蓝绿二值化
        r_sub_b = cv2.dilate(r_sub_b, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
        r_sub_g = cv2.dilate(r_sub_g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
                            iterations=1)  # 膨胀

        final_sub = r_sub_b & gray_img & r_sub_g & white_img & _purpleSrc  # 逻辑与获得最终二值化图像                                                            # 逻辑与获得最终二值化图像
    final_sub = cv2.dilate(final_sub, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))  # 膨胀
    return final_sub

class cvDetect() :
    def __init__(self) -> None:
        
        self.r_threshold = 50
        self.g_threshold = 120
        self.b_threshold = 240
    def find(self,image, offset: QPointF=None) -> np.array:
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
        r, g, b = cv2.split(img_rgb)  # 分离色彩通道
        red_color = False
        threshold = {'r': self.r_threshold, 'g': self.g_threshold, 'b': self.b_threshold}
        #
        r_th, g_th, b_th = channel_th(r, g, b, threshold)
        c_sub = channel_sub(img_rgb, r, g, b, red_color=red_color)
        # 定义结构元素
        circle_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        b_th_o = cv2.morphologyEx(b_th, cv2.MORPH_OPEN, circle_kernel)  # 开运算
        # cv2.imshow("b_th_o", b_th_o)
        # cv2.imshow("r_th",r_th)

        b_and_g = b_th & g_th
        b_and_g_o = cv2.morphologyEx(b_and_g, cv2.MORPH_OPEN, circle_kernel, iterations=3)  # 开运算
        # cv2.imshow("b and g", b_and_g)

        final_img = b_and_g & cv2.bitwise_not(r_th)
        # cv2.imshow("final img", final_img)

        contours, hierarchy = cv2.findContours(final_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 找到凸多边形并绘制
        if len(contours) == 0:
            return np.array([])
        # 面积筛选
        new_contours = []
        for contour in contours:
            if cv2.contourArea(contour) < 100:
                continue
            print(cv2.contourArea(contour))
            # 外接矩形
            x, y, w, h = cv2.boundingRect(contour)
            rate = h / w
            if rate <= 1.5:
                print(rate)
                # 在原图上画出预测的矩形
                cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 0, 255), 10)
                new_contours.append(contour)

        all_contours = np.concatenate(new_contours)
        hull = cv2.convexHull(all_contours)
        if __name__ == "__main__":
            cv2.drawContours(img_rgb, [hull], 0, (255, 255, 255), 1)
            cv2.drawContours(g_th, [hull], 0, 255, 1)
            cv2.drawContours(b_th, [hull], 0, 255, 1)
            cv2.drawContours(r_th, [hull], 0, 255, 1)
            cv2.imshow("r_th", cv2.bitwise_not(r_th))
            cv2.imshow("g_th", g_th)
            cv2.imshow("b_th", b_th)
            cv2.imshow('contours', img_rgb)

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
                return np.array([])

        if __name__ == '__main__':
            # 绘制最小矩形框
            cv2.drawContours(image, [four_edge_polys], 0, (0, 0, 255), 1)
            # cv2.imshow('result', image)
            key_points = [four_edge_polys[3], four_edge_polys[2], four_edge_polys[1], four_edge_polys[0]]
        else:
            if offset:
                offset = np.array([offset.x(), offset.y()])
                four_edge_polys = np.squeeze(four_edge_polys)
                four_edge_polys = four_edge_polys + offset
            key_points = np.array([four_edge_polys[3], four_edge_polys[2], four_edge_polys[1], four_edge_polys[0]])
        print(type(key_points))
        thres = {
            "r_th" : r_th,
            "g_th" : g_th,
            "b_th" : b_th
        }
        return key_points ,thres





