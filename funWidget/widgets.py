import os
import sys
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import typing
from utils.saveDoc import save_as_json
import numpy as np
class DragSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(0, 254)  # 设置范围
        self.setSingleStep(1)  # 设置步长
        self.setPageStep(10)  # 设置大步长
        self.setSliderPosition(125)  # 设置初始值
        self.setOrientation(Qt.Horizontal)  # 设置水平方向
        self.setTracking(True)  # 设置跟踪，即拖动过程中不断发出valueChanged信号
        self.setStyleSheet( #set default style sheet
            'QSlider::handle:horizontal {background-color: white; border: 1px solid black; width: 10px; margin: -3px 0;}')
        self.valueChanged.connect(self.updata_img)
        self.update_img_callback = None
    def updata_img(self):
        if self.update_img_callback:
            self.update_img_callback()
class ListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.itemClicked.connect(self.handle_item_clicked)
        self.update_img_callback = None
        self.directory = None
    def handle_item_clicked(self, item):
        # QMessageBox.information(self, 'Item Clicked', f'You clicked {item.text()}')
        if self.update_img_callback and self.directory:
            item_path = os.path.join(self.directory,item.text())
            self.update_img_callback(item_path)
    def resizeEvent(self, event):  # 用于debug ui界面美化
        print(f'ListWidget {event.size()}')
    
class ImgViewLabel(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.img =None
    def update_image(self,img=None):      
        if type(img) == cv2.Mat:
            self.img = img
            img = QPixmap.fromImage(QImage(img.data, img.shape[1], img.shape[0], img.shape[1], QImage.Format_Grayscale8))
        if type(img) == np.ndarray:
            self.img = img
            img = QPixmap.fromImage(QImage(img.data, img.shape[1], img.shape[0], img.shape[1], QImage.Format_Grayscale8))
        self.setPixmap(img.scaled(self.width(), self.height(), Qt.KeepAspectRatio))
    def resizeEvent(self, event):
        if self.img is not None:
            self.update_image(self.img)

class VBoxLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
class ModeButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_first_click = True
        self.color = "blue"  # Initialize button color to red
        self.clicked.connect(self.on_clicked)
        self.load_model_callback = None
        self.change_mode_recall = None
        self.mode = None
        self.sliderSheet = {
        # these SyleSheet are copyed ,i don't know how to make it in a easy way 
        # and i don't like qt designer and qt creater ,since they are too big and 
        # uneasy to install ,and i don't like it's workspace which less cool 
        # than pycharm or code 
            'red':"""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:1 #ccc);
                border: 1px solid #777;
                width: 13px;
                margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 #FF92BB, stop: 1 #FF4081);
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:1 #FF4081);
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            """,
            'green':"""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 green, stop:1 #ccc);
                border: 1px solid #777;
                width: 13px;
                margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 #FF92BB, stop: 1 #FF4081);
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 green, stop:1 #ccc);
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            """,
            'blue':"""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 blue, stop:1 #ccc);
                border: 1px solid #777;
                width: 13px;
                margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
                border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                            stop: 0 #FF92BB, stop: 1 #FF4081);
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 blue, stop:1 #ccc);
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            """
        }
    def on_clicked(self):
        if self.is_first_click:
            self.first_click_behavior()
            self.is_first_click = False
        else:
            self.toggle_color()
    def first_click_behavior(self):
        # First click behavior
        if self.load_model_callback:
            self.load_model_callback()
        self.setText("Blue Mode")
        self.setStyleSheet("background-color: blue")
        self.mode = 'blue'
        self.change_mode_recall(
            [
                self.sliderSheet['red'],
                self.sliderSheet['green'],
                self.sliderSheet['blue']
            ])
    def toggle_color(self):
        if self.color == "red":
            self.color = "blue"
            self.setText("Blue Mode")
            self.setStyleSheet("background-color: blue")
            self.mode = 'blue'
            self.change_mode_recall(
            [
                self.sliderSheet['red'],
                self.sliderSheet['green'],
                self.sliderSheet['blue']
            ])
        else:
            self.color = "red"
            self.setText("Red Mode")
            self.setStyleSheet("background-color: red")
            self.mode = 'red'
            self.change_mode_recall(
            [
                self.sliderSheet['blue'],
                self.sliderSheet['green'],
                self.sliderSheet['red']
            ])

class WornLog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HELLO!")
        self.resize(321, 138)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok )
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        self.message = QLabel()
        self.message.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.message.setStyleSheet("font-size: 20px; color: white;") # 设置标签的字体、颜色
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    def resizeEvent(self, event):  # 用于debug ui界面美化
        print(f'CustomDialog {event.size()}')
    def setText(self,message):
        self.message.setText(message)

class ImageViewer(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)


        self.setScene(QGraphicsScene())

        self.pixmap = None
        self.pixmapItem = QGraphicsPixmapItem(self.pixmap)
        self.scene().addItem(self.pixmapItem)

        # 设置缩放策略为保持宽高比并充满 QGraphicsView 窗口
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.setRenderHint(QPainter.NonCosmeticDefaultPen, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.RenderHint(QPainter.Antialiasing | QPainter.SmoothPixmapTransform))
        self.setRenderHint(QPainter.RenderHint(
            QPainter.HighQualityAntialiasing | QPainter.NonCosmeticDefaultPen | QPainter.TextAntialiasing))
        self.detect_callback = None
        self.process_labels_callback = None
        self.img_path = None
        # 鼠标事件记录
        self.rect_items = []  # 保存画的矩形项的列表


    def plot_rect(self, key_points):
        qpoints = [QPointF(*p) for p in key_points]
        poly_item = QGraphicsPolygonItem(QPolygonF(qpoints))
        poly_item.setPen(QPen(QColor(0, 255, 0), 2))
        poly_item.setBrush(QBrush(QColor(0, 0, 0, 0)))
        print(type(key_points))
        save_as_json(key_points, 'ore_port', 'polygon', self.height, self.width, self.image_path)
        self.scene().addItem(poly_item)
        self.scene().removeItem(self.rect_items[-1])
        self.rect_items.pop()
        self.rect_items.append(poly_item)

    def wheelEvent(self, event):
        # 获取鼠标滚轮事件的角度值
        angle = event.angleDelta().y()
        # 将放大缩小倍率设为1.1
        zoom_factor = 1.1
        # 计算当前视图的放大缩小倍率
        zoom = zoom_factor ** (angle / 120)
        # 获取当前鼠标位置
        mouse_pos = event.pos()
        # 将鼠标位置转换为视图坐标系下的坐标
        scene_pos = self.mapToScene(mouse_pos)
        # 缩放视图
        self.scale(zoom, zoom)
        # 获取缩放后的鼠标位置
        new_mouse_pos = self.mapFromScene(scene_pos)
        # 计算鼠标位置的偏移量
        delta = new_mouse_pos - mouse_pos
        print(f'delta {delta}')
        # 移动滚动条
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

    def update_image(self, image_path=None):
        """
        update the image
        @param image_path: path to update image
        """
        # 更新图片

        if image_path:   
            #如果给出图片路径就更新图片路径
            self.img_path = image_path 
        try :
            img = cv2.imread(self.img_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except:
            print('WORNING: the path is None')
            return
        self.pixmap = QPixmap.fromImage(QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], QImage.Format_RGB888))
        self.pixmapItem.setPixmap(self.pixmap)
        self.width = self.pixmap.width()
        self.height = self.pixmap.height()
        self.center_image()
        if self.detect_callback :
            points,rgb_binary = self.detect_callback(img)
        if self.process_labels_callback and rgb_binary is not None:
            self.process_labels_callback(rgb_binary)
        if points is not None:
            if self.rect_items:
                self.scene().removeItem(self.rect_items[-1])
                self.rect_items.pop()
            view_width = self.viewport().width()
            view_height = self.viewport().height()
            x_center = (view_width - self.width) / 2
            y_center = (view_height - self.height) / 2
            points = np.squeeze(points)
            points = [QPointF(*point) for point in points]
            #因为上面center_image时使视窗的偏了，移所以画的点也需要进行相应的偏移
            pixmap_points = [QPointF(p.x() + x_center, p.y() + y_center) for p in points]
            polygon = QPolygonF(pixmap_points)
            polygon_item = EditablePolygonItem(polygon)
            polygon_item.setPen(QPen(QColor(0, 255, 0), 2))
            polygon_item.setBrush(QBrush(QColor(0, 0, 0, 0)))
            self.scene().addItem(polygon_item)
            self.rect_items.append(polygon_item)
            # self.setScene(self.scene)
    def center_image(self):
        # Get view dimensions
        view_width = self.viewport().width()
        view_height = self.viewport().height()
        x_center = (view_width - self.width) / 2
        y_center = (view_height - self.height) / 2
        # Move the image to the center
        self.setSceneRect(x_center, y_center, self.width, self.height)
        self.pixmapItem.setPos(x_center, y_center)
    def resizeEvent(self, event):  # 用于debug ui界面美化
        print(f'ImageViewer {event.size()}')
from PyQt5.QtWidgets import QGraphicsPolygonItem

from PyQt5.QtWidgets import QGraphicsPolygonItem

class EditablePolygonItem(QGraphicsPolygonItem):
    def __init__(self, polygon, parent=None):
        super().__init__(polygon, parent)
        self.active_point = None
        self.setAcceptHoverEvents(True)
    def mouseMoveEvent(self, event):
        if self.active_point is not None:
            # 移动活动点
            new_polygon = self.polygon()
            new_polygon[self.active_point] = self.mapFromScene(event.scenePos())
            self.setPolygon(new_polygon)  # 更新多边形
            self.update()
    def mousePressEvent(self, event):
        # 查找最接近鼠标点击位置的点
        for i, point in enumerate(self.polygon()):
            if (point - self.mapFromScene(event.scenePos())).manhattanLength() < 10:
                self.active_point = i
                print('get it')
                break
    def mouseReleaseEvent(self, event):
        self.active_point = None
    def paint(self, painter, option, widget=None):
        # 创建一个QPen对象
        pen = QPen(Qt.red)
        # 设置线宽度
        pen.setWidth(2)
        # 将QPen对象应用于绘制器
        painter.setPen(pen)

        # 绘制多边形
        painter.drawPolygon(self.polygon())

        # 绘制坐标点
        for point in self.polygon():
            # 设置绘制点的颜色为红色
            painter.setPen(QPen(Qt.red))
            # 绘制点的填充颜色为黄色
            painter.setBrush(QBrush(Qt.yellow))
            # 绘制点
            painter.drawEllipse(point, 5, 5)


