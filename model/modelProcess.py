import argparse
import time
from pathlib import Path
import cv2
import torch
from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, check_requirements,\
    polygon_non_max_suppression, polygon_scale_coords
from utils.torch_utils import select_device
import subprocess as sp
import os

class ModelPrecess():
    def __init__(self,model_path,imgsz=640,half_float=False) -> None:
        self.device = select_device()
        half_float &= self.device.type != 'cpu'  # half precision only supported on CUDA
        # Load model
        self.model = attempt_load(model_path, map_location=self.device)  # load FP32 model
        stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(imgsz, s=stride)  # check image size
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names  # get class names
        if half_float:
            self.model.half()  # to FP16
        # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, imgsz, imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once
        print("load success")
    @torch.no_grad()
    def detect(self,
            im0s=None,
            conf_thres=0.25,  # confidence threshold
            iou_thres=0.45,  # NMS IOU threshold
            max_det=20,  # maximum detections per image
            classes=None,  # filter by class: --class 0, or --class 0 2 3
            agnostic_nms=False,  # class-agnostic NMS
            augment=False,  # augmented inference
            half=False,  # use FP16 half-precision inference
            label_mode = True
            ):
        img = letterbox(im0s,new_shape=self.imgsz)[0]
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # inference
        pred = self.model(img, augment=augment)[0]
        # Apply polygon NMS
        pred = polygon_non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        # Process detections
        for i, det in enumerate(pred):  # detections per image
            im0 = im0s.copy()
            if len(det):
                # Rescale boxes from img_size to im0 size
                """mark"""
                det[:, :8] = polygon_scale_coords(img.shape[1:3], det[:, :8], im0.shape).round()
                for *xyxyxyxy, conf, cls in reversed(det):
                    if label_mode :
                        point_list = torch.tensor(xyxyxyxy).cpu().numpy()
                        return point_list.reshape(-1, 1, 2).squeeze().tolist()




@torch.no_grad()
def detect(weights='/home/linda/Documents/project/polygondetect2/runs/train/exp86/weights/polygon_last.pt',  # self.model.pt path(s)
           source='/home/linda/Videos/ore_port/video/dahua/blue/output_images/image/Video_2023_03_31_233634_20858.jpg',  # file/dir/URL/glob, 0 for webcam
           imgsz=640,  # inference size (pixels)
           conf_thres=0.25,  # confidence threshold
           iou_thres=0.45,  # NMS IOU threshold
           max_det=20,  # maximum detections per image
           device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
           classes=None,  # filter by class: --class 0, or --class 0 2 3
           agnostic_nms=False,  # class-agnostic NMS
           augment=False,  # augmented inference
           half=True,  # use FP16 half-precision inference
           label_mode = True
           ):
    
    img_path = source
    device = select_device(device)
    half &= device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    if half:
        model.half()  # to FP16
    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    
    im0s = cv2.imread(img_path)
    img = letterbox(im0s,new_shape=imgsz)[0]
    
    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)
    # inference
    pred = model(img, augment=augment)[0]
    # Apply polygon NMS
    pred = polygon_non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    # Process detections
    for i, det in enumerate(pred):  # detections per image
        im0 = im0s.copy()
        if len(det):
            # Rescale boxes from img_size to im0 size
            """mark"""
            det[:, :8] = polygon_scale_coords(img.shape[1:3], det[:, :8], im0.shape).round()
            for *xyxyxyxy, conf, cls in reversed(det):
                if label_mode :
                    point_list = torch.tensor(xyxyxyxy).cpu().numpy()
                    return point_list.reshape(-1, 1, 2).squeeze().tolist()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='/home/linda/Documents/project/polygondetect2/runs/train/exp86/weights/polygon_last.pt',
                        help='model.pt path(s)')
    parser.add_argument('--source', type=str,
                        default='/home/linda/Videos/ore_port/video/dahua/blue/output_images/image/Video_2023_03_31_233634_20858.jpg',
                        help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--imgsz', '--img', '--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=20, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')

    opt = parser.parse_args()
    print('Notice: polygon_detect.py is designed for polygon cases')
    print(opt)
    # check_requirements(exclude=('tensorboard', 'thop'))
    print(detect(**vars(opt)))
