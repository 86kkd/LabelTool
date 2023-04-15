import os
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from funWidget.widgets import DragSlider, ImageViewer, ListWidget, VBoxLayout,ModeButton, WornLog
from model.modelProcess import ModelPrecess
from cvProcess import cvDetect


def move_to_center(window):
    """将窗口移动到屏幕中央"""
    # 获取屏幕的尺寸
    screen_size = QDesktopWidget().screenGeometry()

    # 计算窗口在屏幕中央的位置
    x = int((screen_size.width() - window.width()) / 2)
    y = int((screen_size.height() - window.height()) / 2)

    # 移动窗口到该位置
    window.move(x, y)


# noinspection PyArgumentList
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # first create workList
        self.workList = ListWidget(self)
        # then create label and slider to show images
        rLabel = QLabel()
        rSlider = DragSlider()
        gLabel = QLabel()
        gSlider = DragSlider()
        bLabel = QLabel()
        bSlider = DragSlider()
        lab_button = ModeButton("model is disabled")
        lab_layout = VBoxLayout()
        lab_layout.addWidget(lab_button)
        lab_layout.addWidget(rLabel)
        lab_layout.addWidget(rSlider)
        lab_layout.addWidget(gLabel)
        lab_layout.addWidget(gSlider)
        lab_layout.addWidget(bLabel)
        lab_layout.addWidget(bSlider)
        lab_widget = QWidget()
        lab_widget.setLayout(lab_layout)
        # create menu
        menubar = self.menuBar()  # get menubar and set file help menu
        fileMenu = menubar.addMenu('File')
        modelMenu = menubar.addMenu('model')
        helpMenu = menubar.addMenu('help')

        loadModelAction = QAction('load',self)
        enableAction = QAction('enable', self)
        disableAction = QAction('disable', self)
        trainAction = QAction('train', self)
        modelMenu.addAction(loadModelAction)
        modelMenu.addAction(enableAction)
        modelMenu.addAction(disableAction)
        modelMenu.addAction(trainAction)

        mutableAction = QAction('mutable', self)
        frozenAction = QAction('frozen', self)
        trainMenu = QMenu()
        trainMenu.addAction(mutableAction)
        trainMenu.addAction(frozenAction)
        trainAction.setMenu(trainMenu)
        # link the about to show signal to open help web
        helpDetail = QAction('for detail', self)
        helpMenu.addAction(helpDetail)
        # add open action to file menu
        openDirAction = QAction("open", self)
        fileMenu.addAction(openDirAction)
        # add exit action to file menu
        exitAction = QAction('exit', self)
        fileMenu.addAction(exitAction)

        # create imageViewer to show image
        self.imageViewer = ImageViewer(self)

        # create splitter to manage workList and imageViewer
        split_left = QSplitter(Qt.Horizontal)
        split_left.addWidget(self.workList)
        split_left.addWidget(self.imageViewer)
        split_left.addWidget(lab_widget)
        split_left.setSizes([121, 1120,280])
        centralWidget = QWidget()
        centralWidget.setLayout(QVBoxLayout())
        centralWidget.layout().addWidget(split_left)
        self.setCentralWidget(centralWidget)
        
        # beautify the window 
        self.resize(1618,1000)
        move_to_center(self)
        self.workList.setUniformItemSizes(True)
        self.workList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # define windows and button action
        openDirAction.triggered.connect(self.load_directory)
        loadModelAction.triggered.connect(self.load_model)
        exitAction.setShortcut('Esc')
        exitAction.triggered.connect(self.close)
        lab_button.first_click_callback = self.load_model
        self.imageViewer.process_image_callback = self.auto_detect
        self.workList.update_img_callback = self.imageViewer.update_image
        helpDetail.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl('https://www.example.com')))
        
        # initial global parameters
        self.loaded_model = False
        rSlider.setSliderPosition(50)
        gSlider.setSliderPosition(120)
        bSlider.setSliderPosition(240)
        rSlider.valueChanged.connect(self.r_sliderChange)
        gSlider.valueChanged.connect(self.g_sliderChange)
        bSlider.valueChanged.connect(self.b_sliderChange)
    def r_sliderChange(self,value):
        self.cvDetect.r_threshold = value
        path = os.path.join(self.directory,self.workList.currentItem().text())
        self.imageViewer.update_image(path)
    def g_sliderChange(self,value):
        self.cvDetect.r_threshold = value
        path = os.path.join(self.directory,self.workList.currentItem().text())
        self.imageViewer.update_image(path)
    def b_sliderChange(self,value):
        self.cvDetect.r_threshold = value
        path = os.path.join(self.directory,self.workList.currentItem().text())
        self.imageViewer.update_image(path)
    def resizeEvent(self, event: QResizeEvent) -> None:
        print(event.size())
        return super().resizeEvent(event)
    
    def load_directory(self):
        dialog = self.get_dialog("Select Directory")
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        self._extracted_from_load_model_6(dialog)
        self.directory = dialog.selectedFiles()[0]  # the directory selected 
        if self.directory:
            self.update_workList(self.directory)
            self.imageViewer.update_image(os.path.join(self.directory,self.workList.item(0).text()))
    def load_model(self):
        
        dialog = self.get_dialog("select model")
        dialog.setFilter(dialog.filter() | QDir.Files) # 显示文件而不是目录
        dialog.setFilter(dialog.filter() | QDir.Hidden) # 显示隐藏文件
        dialog.setNameFilter('*.pt;;*.pth') # 只显示.pt文件
        self._extracted_from_load_model_6(dialog)
        self.model_dir = dialog.selectedFiles()[0]
        if self.model_dir.endswith('.pt') or self.model_dir.endswith('.pth'):
            try:
                self.model = ModelPrecess(self.model_dir)
            except Exception:
                self.send_tips('意外错误模型加载失败')
            self.loaded_model = True
        else:
            self.send_tips('选一个模型文件加载阿')

    # TODO Rename this here and in `load_directory` and `load_model`
    def _extracted_from_load_model_6(self, dialog):
        dialog.setStyleSheet("background-color: #1E1E1E; color: #9E9E9E;")
        move_to_center(dialog)
        dialog.exec_()

    # TODO Rename this here and in `load_directory` and `load_model`
    def get_dialog(self, title):
        result = QFileDialog()
        option = QFileDialog.Option()
        result.setOption(option)
        result.setDirectory('./')
        result.setWindowTitle(title)
        return result

    # TODO Rename this here and in `load_model`
    def send_tips(self, arg0):
        msg_box = WornLog()
        msg_box.setStyleSheet('background-color: #1E1E1E;color: white')
        msg_box.setWindowTitle("提示")
        msg_box.setText(arg0)
        msg_box.exec_()


    def update_workList(self,directory):
        images = sorted([f for f in os.listdir(directory) if f.endswith('.jpg') or f.endswith('.png')])
        jsons = sorted([f for f in os.listdir(directory) if f.endswith('.json')])
        self.workList.addItems(images)
        self.workList.directory = directory
        for i in range(self.workList.count()):
            item = self.workList.item(i)
            img_json = f"{os.path.splitext(item.text())[0]}.json"
            if img_json in jsons:
                item.setForeground(QColor(0, 0, 255)) # color
                
    def auto_detect(self,img):  # sourcery skip: do-not-use-bare-except
        def sort_points(points):
            # 计算质心
            centroid = (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))
            # 逆时针排序
            sorted_points = sorted(
                points,
                key=lambda p: -np.arctan2(p[1] - centroid[1], p[0] - centroid[0]),
            )
            # 寻找左上角的点
            top_left_point_index = 0
            min_sum = float("inf")
            for i, point in enumerate(sorted_points):
                current_sum = point[0] + point[1]
                if current_sum < min_sum:
                    min_sum = current_sum
                    top_left_point_index = i
            # 将左上角的点作为起始点，调整排序后的列表
            return sorted_points[top_left_point_index:] + sorted_points[:top_left_point_index]
        def enlarge_polygon(points, scale_factor=0.1):
            # 计算质心
            centroid = (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))
            enlarged_points = []
            for point in points:
                # 计算点到质心的向量
                vector = (point[0] - centroid[0], point[1] - centroid[1])
                
                # 扩大向量
                enlarged_vector = (vector[0] * (1 + scale_factor), vector[1] * (1 + scale_factor))
                
                # 计算新的点
                new_point = (centroid[0] + enlarged_vector[0], centroid[1] + enlarged_vector[1])
                enlarged_points.append(new_point)

            return enlarged_points
        def crop_polygon(input_image, points):
            # 创建一个全黑的掩膜
            mask = np.zeros(input_image.shape[:2], dtype=np.uint8)
            # 根据四个点创建一个多边形
            polygon = np.array(points, np.int32)
            polygon = polygon.reshape((-1, 1, 2))
            # 使用多边形填充掩膜
            cv2.fillPoly(mask, [polygon], 255)
            return cv2.bitwise_and(input_image, input_image, mask=mask)
        def visual_result(img, sorted_points):
            # 获取第一个点
            first_point = sorted_points[0]
            if type(first_point) == np.ndarray and first_point.ndim == 2 :
                first_point = first_point.squeeze()
                sorted_points = sorted_points.squeeze()
            # 在第一个点处绘制一个半径为 5 的红色圆形
            cv2.circle(img, tuple(map(int, first_point)), 5, (0, 0, 255), -1)
            # 使用箭头连接所有点
            for i in range(len(sorted_points) - 1):
                start_point = tuple(map(int, sorted_points[i]))
                end_point = tuple(map(int, sorted_points[i + 1]))
                # 连接相邻的点，用箭头表示方向
                cv2.arrowedLine(img, start_point, end_point, (0, 255, 0), 2, tipLength=0.05)
            # 返回标记后的图像
            return img
        if self.loaded_model:
            points = self.model.detect(img)
            # try :
            sorted_points = sort_points(points)
            enlarged_points = enlarge_polygon(sorted_points, scale_factor=0.1)
            cropped_img = crop_polygon(img, enlarged_points)
            # cropped_img_with_marker = visual_result(cropped_img, sorted_points)
            self.cvDetect = cvDetect()
            points, thres= self.cvDetect.find(image=img)
            # cropped_img_with_marker = visual_result(cropped_img, points)
            # except:
                # print('\033[31m there is something wrong with auto detection\033[0m')
                # sorted_points, cropped_img_with_marker, thres = None , None, None
            # cv2.imshow('a',cropped_img_with_marker)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            
        else :
            points, cropped_img_with_marker, thres = None, None, None
        return points ,cropped_img_with_marker, thres
        
    def update_image(self):
        
        
if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()