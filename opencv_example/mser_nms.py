# -*- coding: utf-8 -*-



import cv2

import numpy as np



# NMS 方法（Non Maximum Suppression，非极大值抑制）

def nms(boxes, overlapThresh):

    if len(boxes) == 0:

        return []



    if boxes.dtype.kind == "i":

        boxes = boxes.astype("float")



    pick = []



    # 取四个坐标数组

    x1 = boxes[:, 0]

    y1 = boxes[:, 1]

    x2 = boxes[:, 2]

    y2 = boxes[:, 3]



    # 计算面积数组

    area = (x2 - x1 + 1) * (y2 - y1 + 1)



    # 按得分排序（如没有置信度得分，可按坐标从小到大排序，如右下角坐标）

    idxs = np.argsort(y2)



    # 开始遍历，并删除重复的框

    while len(idxs) > 0:

        # 将最右下方的框放入pick数组

        last = len(idxs) - 1

        i = idxs[last]

        pick.append(i)



        # 找剩下的其余框中最大坐标和最小坐标

        xx1 = np.maximum(x1[i], x1[idxs[:last]])

        yy1 = np.maximum(y1[i], y1[idxs[:last]])

        xx2 = np.minimum(x2[i], x2[idxs[:last]])

        yy2 = np.minimum(y2[i], y2[idxs[:last]])



        # 计算重叠面积占对应框的比例，即 IoU

        w = np.maximum(0, xx2 - xx1 + 1)

        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]



        # 如果 IoU 大于指定阈值，则删除

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlapThresh)[0])))



    return boxes[pick].astype("int")



# 读取图片

# imagePath = 'cv.png'
imagePath='./grades.jpg'
img = cv2.imread(imagePath)
# from PIL import Image, ImageEnhance
# #图像增强
# img = Image.fromarray(img)
# img = ImageEnhance.Contrast(img).enhance(8)  # 增加对比度
# img = ImageEnhance.Sharpness(img).enhance(3)  # 增加锐度
# img = np.array(img)

# src = cv2.GaussianBlur(img, (5, 3), 0)
# # 再锐化
# blur_img = cv2.GaussianBlur(src, (0, 0), 8)
# img = cv2.addWeighted(src, 1.5, blur_img, -0.5, 0)

# # 灰度图+降噪
# fx = max(int(2500 / img.shape[1]), 1)
# fy = max(int(3500 / img.shape[0]), 1)
# img = cv2.resize(img, (0, 0), fx=fx, fy=fy)



# 灰度化

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

vis = img.copy()

orig = img.copy()



# 调用 MSER 算法

mser = cv2.MSER_create()

regions, _ = mser.detectRegions(gray)  # 获取文本区域

hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]  # 绘制文本区域

cv2.polylines(img, hulls, 1, (0, 255, 0))

cv2.imshow('img', img)



# 将不规则检测框处理成矩形框

keep = []

for c in hulls:

    x, y, w, h = cv2.boundingRect(c)

    keep.append([x, y, x + w, y + h])

    cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 255, 0), 1)

cv2.imshow("hulls", vis)



keep2 = np.array(keep)

pick = nms(keep2, 0.3
           )

print("[x] after applying non-maximum, %d bounding boxes" % (len(pick)))

# loop over the picked bounding boxes and draw them

for (startX, startY, endX, endY) in pick:

    cv2.rectangle(orig, (startX, startY), (endX, endY), (255, 0, 0), 1)

cv2.imshow("After NMS", orig)



cv2.waitKey(0)

cv2.destroyAllWindows()