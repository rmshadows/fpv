import pandas as pd
import numpy as np
import cv2
import argparse
import os
from tqdm import tqdm

# =======================
# 🔧 默认配置（内置）
DEFAULT_INPUT = "1.log"  # 默认输入log
DEFAULT_SPEED = 1.0                        # 默认视频速度倍率
width, height = 1200, 600                  # 视频分辨率
fps = 30                                   # 固定帧率（不变）
dot_radius = 12                            # 圆点半径
trail_length = 8                           # 轨迹保留帧数
cross_color = (60, 60, 60)                 # 十字线颜色
trail_color_start = (0, 0, 0)              # 起始颜色
trail_color_end = (0, 0, 255)              # 末端颜色
trail_thickness = 14                       # 轨迹线条粗细

# 🔲 摇杆边框配置（左上角 + 宽高）
LEFT_BOX_X, LEFT_BOX_Y = 0, 0
LEFT_BOX_W, LEFT_BOX_H = width // 2, height
RIGHT_BOX_X, RIGHT_BOX_Y = width // 2, 0
RIGHT_BOX_W, RIGHT_BOX_H = width // 2, height
BOX_COLOR = (100, 100, 100)
BOX_THICKNESS = 2
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
df = pd.read_csv(input_file, comment="#").dropna(subset=["Ail", "Ele", "Thr", "Rud"])
total_frames = len(df)

# 生成索引序列（控制速度）
new_indices = np.linspace(0, total_frames - 1, int(total_frames / speed)).astype(int)

def map_value(v, in_min, in_max, out_min, out_max):
    return int((v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# 初始化输出
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

trail_left, trail_right = [], []

# =======================
# 🎥 主循环
for idx in tqdm(new_indices, desc="Rendering"):
    row = df.iloc[idx]
    rud = map_value(row["Rud"], -1024, 1024, 0, width // 2)
    thr = map_value(row["Thr"], -1024, 1024, height, 0)
    ail = map_value(row["Ail"], -1024, 1024, width // 2, width)
    ele = map_value(row["Ele"], -1024, 1024, height, 0)

    pos_left = (rud, thr)
    pos_right = (ail, ele)
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 🎯 绘制摇杆边框
    cv2.rectangle(frame, (LEFT_BOX_X, LEFT_BOX_Y),
                  (LEFT_BOX_X + LEFT_BOX_W, LEFT_BOX_Y + LEFT_BOX_H),
                  BOX_COLOR, BOX_THICKNESS)
    cv2.rectangle(frame, (RIGHT_BOX_X, RIGHT_BOX_Y),
                  (RIGHT_BOX_X + RIGHT_BOX_W, RIGHT_BOX_Y + RIGHT_BOX_H),
                  BOX_COLOR, BOX_THICKNESS)

    # 十字线
    mid_x_left = width // 4
    mid_x_right = 3 * width // 4
    mid_y = height // 2
    for x_center in [mid_x_left, mid_x_right]:
        cv2.line(frame, (x_center, 0), (x_center, height), cross_color, 1)
        cv2.line(frame, (x_center - width // 4, mid_y), (x_center + width // 4, mid_y), cross_color, 1)

    # 轨迹更新
    trail_left.append(pos_left)
    trail_right.append(pos_right)
    if len(trail_left) > trail_length:
        trail_left.pop(0)
        trail_right.pop(0)

    for i in range(1, len(trail_left)):
        alpha = i / len(trail_left)
        color = tuple([
            int(trail_color_start[c] + (trail_color_end[c] - trail_color_start[c]) * alpha)
            for c in range(3)
        ])
        cv2.line(frame, trail_left[i - 1], trail_left[i], color, trail_thickness)
        cv2.line(frame, trail_right[i - 1], trail_right[i], color, trail_thickness)

    cv2.circle(frame, pos_left, dot_radius, (255, 255, 255), -1)
    cv2.circle(frame, pos_right, dot_radius, (255, 255, 255), -1)

    out.write(frame)

out.release()

# =======================
# 📊 输出信息
original_time = total_frames / fps
final_time = len(new_indices) / fps
print(f"✅ 视频已生成：{output_video}")
print(f"🎞️ 速度倍率 {speed}x（恒定 {fps} fps）")
print(f"🕒 原始时长 ≈ {original_time:.1f}s → 输出时长 ≈ {final_time:.1f}s")
