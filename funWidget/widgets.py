import os
import sys
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import typing
from utils.saveDoc import save_as_json

class DragSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(0, 255)  # 设置范围
        self.setSingleStep(1)  # 设置步长
        self.setPageStep(10)  # 设置大步长
        self.setSliderPosition(125)  # 设置初始值
        self.setOrientation(Qt.Horizontal)  # 设置水平方向
        self.setTracking(True)  # 设置跟踪，即拖动过程中不断发出valueChanged信号
        self.setStyleSheet(
            'QSlider::handle:horizontal {background-color: white; border: 1px solid black; width: 10px; margin: -3px 0;}')

class ListWidget(QListWidget):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
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

class VBoxLayout(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
class ModeButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_first_click = True
        self.color = "red"  # Initialize button color to red
        self.clicked.connect(self.on_clicked)
        self.first_click_callback = None

    def on_clicked(self):
        if self.is_first_click:
            self.first_click_behavior()
            if self.first_click_callback:
                self.first_click_callback()
            self.is_first_click = False
        else:
            self.toggle_color()

    def first_click_behavior(self):
        # First click behavior
        self.setText("Red Mode")
        self.setStyleSheet("background-color: red")
        

    def toggle_color(self):
        if self.color == "red":
            self.color = "blue"
            self.setText("Blue Mode")
            self.setStyleSheet("background-color: blue")
        else:
            self.color = "red"
            self.setText("Red Mode")
            self.setStyleSheet("background-color: red")

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
        self.process_image_callback = None
        # 鼠标事件记录
        self.rect_items = []  # 保存画的矩形项的列表

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect_item = QGraphicsRectItem()
            rect_item.setPen(QPen(QColor(255, 0, 0), 2))
            self.scene().addItem(rect_item)
            rect_item.setRect(QRectF(self.mapToScene(event.pos()), QSizeF()))
            self.rect_items.append(rect_item)

    def mouseMoveEvent(self, event):
        if self.rect_items:
            rect = QRectF(self.rect_items[-1].rect().topLeft(), self.mapToScene(event.pos())).normalized()
            self.rect_items[-1].setRect(rect)

    def mouseReleaseEvent(self, event):  # sourcery skip: extract-method
        if event.button() != Qt.LeftButton or not self.rect_items:
            return
        rect = QRectF(self.rect_items[-1].rect())
        if rect.width() == 0 or rect.height() == 0:
            self.scene().removeItem(self.rect_items[-1])
            self.rect_items.pop()
        else:
            # 调用find_key_points函数来处理框选区域的关键点
            # 从图片中获取矩形范围内的图像
            rect_img = self.pixmap.copy(rect.toRect())
            key_points = find_key_points(rect_img, rect.topLeft())

            if key_points.size == 0:
                self.msg_box = QMessageBox()  # c创建消息框
                self.msg_box.setStyleSheet('background-color: #1E1E1E;color: white')
                self.msg_box.setWindowTitle("提示")
                self.msg_box.setText("自动检测死掉了，请手动标吧")
                self.msg_box.exec_()
                self.scene().removeItem(self.rect_items[-1])
                self.rect_items.pop()

            else:
                self.plot_rect(key_points)

    # TODO Rename this here and in `mouseReleaseEvent`
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

    def update_image(self, image_path):
        """
        update the image
        @param image_path: path to update image
        """
        # 更新图片
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.pixmap = QPixmap.fromImage(QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], QImage.Format_RGB888))
        self.pixmapItem.setPixmap(self.pixmap)
        self.width = self.pixmap.width()
        self.height = self.pixmap.height()
        self.center_image()
        if self.process_image_callback :
            points,images,thres = self.process_image_callback(img)

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
