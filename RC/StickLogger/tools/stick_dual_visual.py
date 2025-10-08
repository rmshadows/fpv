#!/usr/bin/env python3
"""
双摇杆轨迹视频生成器

使用方法：
    python joystick_video.py [input_file] [--speed SPEED]

参数说明：
    input_file      输入的Log文件（CSV格式），默认内置 "1.log"
    --speed SPEED   视频速度倍率，默认 1.0 （>1加速，<1减慢）

功能特性：
1. 双摇杆轨迹可视化（左右摇杆独立）
2. 固定帧率输出（fps=30）
3. 可选边框渐变，显示摇杆接近边界的亮度变化
4. 轨迹渐变效果和十字线
5. 输出视频文件为 mp4，文件名与输入文件同名
"""

import pandas as pd
import numpy as np
import cv2
import argparse
import os
from tqdm import tqdm

# =======================
# 🔧 默认配置（内置）
DEFAULT_INPUT = "1.log"   # 默认输入log文件
DEFAULT_SPEED = 1.0        # 默认视频速度倍率
width, height = 1200, 600  # 视频分辨率
fps = 30                   # 固定帧率（不变）
dot_radius = 12            # 圆点半径
trail_length = 8           # 轨迹保留帧数
cross_color = (60, 60, 60) # 十字线颜色
trail_color_start = (0, 0, 0)  # 轨迹起始颜色（BGR）
trail_color_end = (0, 0, 255)  # 轨迹末端颜色（BGR）
trail_thickness = 14        # 轨迹线条粗细

# 🔲 摇杆边框配置（左上角坐标 + 宽高）
LEFT_BOX_X, LEFT_BOX_Y = 0, 0
LEFT_BOX_W, LEFT_BOX_H = width // 2, height
RIGHT_BOX_X, RIGHT_BOX_Y = width // 2, 0
RIGHT_BOX_W, RIGHT_BOX_H = width // 2, height
BOX_COLOR = (100, 100, 100)  # 边框颜色
CROSS_THICKNESS = 1          # 十字架的粗细
BOX_THICKNESS = 4            # 边框线粗细，推荐小于10的偶数，建议4

# 🔲 可选功能：边框内部渐变（不会覆盖边界）
ENABLE_BOX_GRADIENT = True  # False 关闭，True 开启
GRADIENT_MARGIN = 50         # 离边框多少像素开始渐变
BOX_THICKNESS_HIGHLIGHT = 2  # 高亮边框线粗细，推荐小于7的偶数或1，建议2
# =======================

# 🧩 参数解析
parser = argparse.ArgumentParser(description="双摇杆轨迹视频生成")
parser.add_argument("input_file", nargs="?", default=DEFAULT_INPUT, help="输入log文件（默认内置）")
parser.add_argument("--speed", type=float, default=DEFAULT_SPEED, help="视频速度倍率（默认1.0）")
args = parser.parse_args()

# ⚙️ 使用参数
input_file = args.input_file
speed = args.speed
output_video = os.path.splitext(os.path.basename(input_file))[0] + ".mp4"

# =======================
# 📖 读取数据
# 只保留Ail, Ele, Thr, Rud列非空的数据
df = pd.read_csv(input_file, comment="#").dropna(subset=["Ail", "Ele", "Thr", "Rud"])
total_frames = len(df)

# 生成索引序列（控制播放速度）
# speed<1 放慢（重复帧），speed>1 加速（跳帧）
new_indices = np.linspace(0, total_frames - 1, int(total_frames / speed)).astype(int)

# 数据映射函数，将摇杆值映射到像素坐标
def map_value(v, in_min, in_max, out_min, out_max):
    return int((v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# 初始化视频输出
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

trail_left, trail_right = [], []

# =======================
# 🎥 主循环：逐帧绘制轨迹
for idx in tqdm(new_indices, desc="Rendering"):
    row = df.iloc[idx]

    # 映射摇杆数值到屏幕坐标
    rud = map_value(row["Rud"], -1024, 1024, 0, width // 2)
    thr = map_value(row["Thr"], -1024, 1024, height, 0)
    ail = map_value(row["Ail"], -1024, 1024, width // 2, width)
    ele = map_value(row["Ele"], -1024, 1024, height, 0)

    pos_left = (rud, thr)
    pos_right = (ail, ele)

    # 初始化空白帧
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 🎯 绘制固定边框（底层保证边界存在）
    half_t = BOX_THICKNESS // 2
    half_t_h = BOX_THICKNESS_HIGHLIGHT // 2
    # ## 左边框（右边退半线宽，避免中线重叠）
    # cv2.rectangle(
    #     frame,
    #     (LEFT_BOX_X + half_t, LEFT_BOX_Y + half_t),
    #     (LEFT_BOX_X + LEFT_BOX_W - half_t, LEFT_BOX_Y + LEFT_BOX_H - half_t),
    #     BOX_COLOR,
    #     BOX_THICKNESS
    # )
    # ## 右边框（左边退半线宽，右边也收回半线宽避免被裁掉）
    # cv2.rectangle(
    #     frame,
    #     (RIGHT_BOX_X + half_t, RIGHT_BOX_Y + half_t),
    #     (RIGHT_BOX_X + RIGHT_BOX_W - half_t, RIGHT_BOX_Y + RIGHT_BOX_H - half_t),
    #     BOX_COLOR,
    #     BOX_THICKNESS
    # )
    ## 总边框
    cv2.rectangle(
        frame,
        (half_t, half_t),
        (width - half_t - 1, height - half_t - 1),
        BOX_COLOR,
        BOX_THICKNESS
    )
    ## 中间竖线
    cv2.rectangle(
        frame,
        (width // 2, half_t),
        (width // 2, height - half_t),
        BOX_COLOR,
        BOX_THICKNESS
    )

    # 🎨 可选渐变（仅在边框内部，不覆盖边界）
    if ENABLE_BOX_GRADIENT:
        # 左摇杆渐变
        dx = min(pos_left[0] - LEFT_BOX_X, LEFT_BOX_X + LEFT_BOX_W - pos_left[0])
        dy = min(pos_left[1] - LEFT_BOX_Y, LEFT_BOX_Y + LEFT_BOX_H - pos_left[1])
        dist = min(dx, dy)
        intensity = int(255 * max(0, (GRADIENT_MARGIN - dist) / GRADIENT_MARGIN))
        cv2.rectangle(frame,
                      (LEFT_BOX_X + BOX_THICKNESS + half_t_h + 1, LEFT_BOX_Y + BOX_THICKNESS + half_t_h + 1),
                      (LEFT_BOX_X + LEFT_BOX_W - half_t - half_t_h - 1, LEFT_BOX_Y + LEFT_BOX_H - BOX_THICKNESS - half_t_h - 2),
                      (intensity, intensity, intensity), BOX_THICKNESS_HIGHLIGHT)

        # 右摇杆渐变
        dx = min(pos_right[0] - RIGHT_BOX_X, RIGHT_BOX_X + RIGHT_BOX_W - pos_right[0])
        dy = min(pos_right[1] - RIGHT_BOX_Y, RIGHT_BOX_Y + RIGHT_BOX_H - pos_right[1])
        dist = min(dx, dy)
        intensity = int(255 * max(0, (GRADIENT_MARGIN - dist) / GRADIENT_MARGIN))
        cv2.rectangle(frame,
                      (RIGHT_BOX_X + half_t + half_t_h + 1, RIGHT_BOX_Y + BOX_THICKNESS + half_t_h + 1),
                      (RIGHT_BOX_X + RIGHT_BOX_W - BOX_THICKNESS - half_t_h - 2, RIGHT_BOX_Y + RIGHT_BOX_H - BOX_THICKNESS - half_t_h - 2),
                      (intensity, intensity, intensity), BOX_THICKNESS_HIGHLIGHT)

    # 十字线绘制
    mid_x_left = width // 4
    mid_x_right = 3 * width // 4
    mid_y = height // 2
    for x_center in [mid_x_left, mid_x_right]:
        cv2.line(frame, (x_center, 0), (x_center, height), cross_color, CROSS_THICKNESS)
        cv2.line(frame, (x_center - width // 4, mid_y), (x_center + width // 4, mid_y), cross_color, CROSS_THICKNESS)

    # 轨迹更新（保留 trail_length 帧）
    trail_left.append(pos_left)
    trail_right.append(pos_right)
    if len(trail_left) > trail_length:
        trail_left.pop(0)
        trail_right.pop(0)

    # 绘制轨迹（渐变颜色）
    for i in range(1, len(trail_left)):
        alpha = i / len(trail_left)
        color = tuple([
            int(trail_color_start[c] + (trail_color_end[c] - trail_color_start[c]) * alpha)
            for c in range(3)
        ])
        cv2.line(frame, trail_left[i - 1], trail_left[i], color, trail_thickness)
        cv2.line(frame, trail_right[i - 1], trail_right[i], color, trail_thickness)

    # 绘制摇杆当前点
    cv2.circle(frame, pos_left, dot_radius, (255, 255, 255), -1)
    cv2.circle(frame, pos_right, dot_radius, (255, 255, 255), -1)

    # 写入视频
    out.write(frame)

# 释放视频资源
out.release()

# =======================
# 📊 输出信息
original_time = total_frames / fps
final_time = len(new_indices) / fps
print(f"✅ 视频已生成：{output_video}")
print(f"🎞️ 速度倍率 {speed}x（恒定 {fps} fps）")
print(f"🕒 原始时长 ≈ {original_time:.1f}s → 输出时长 ≈ {final_time:.1f}s")
