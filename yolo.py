import argparse
import time
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

import cv2

weights = './best.pt'
img_size = 640

# Initialize
set_logging()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
half = device.type != 'cpu'  # half precision only supported on CUDA

# Load model
model = attempt_load(weights, map_location=device)  # load FP32 model
# stride = int(model.stride.max())  # model stride
# imgsz = check_img_size(imgsz, s=stride)  # check img_size

model = TracedModel(model, device, img_size)

if half:
    model.half()  # to FP16

@torch.no_grad()
def detect(source):
    imgsz = 640
    
    conf_thres = 0.25
    iou_thres = 0.45

    # # Initialize
    # set_logging()
    # device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # # Load model
    # model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    # model = TracedModel(model, device, img_size)

    # if half:
    #     model.half()  # to FP16

    # Set Dataloader
    dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    old_img_w = old_img_h = imgsz
    old_img_b = 1

    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Warmup
        if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                model(img)[0]

        # Inference
        with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
            pred = model(img)[0]

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres)

        # Process detections
        im0 = im0s
        labels = []
        for det in pred:  # detections per image
            p, s, im0 = path, '', im0s

            p = Path(p)  # to Path
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    labels.append((f'{names[int(cls)]}', int(conf * 100)))
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=1)
    
            # print(path, labels)

            # get the name of the file 
            # filename = re.split(r'[/\\]', path)[-1]
            # cv2.imwrite(f'result/{filename}', im0)

        return im0, labels
        # return labels

    # print(f'Done. ({time.time() - t0:.3f}s)')