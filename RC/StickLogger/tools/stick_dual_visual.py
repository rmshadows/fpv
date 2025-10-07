import pandas as pd
import numpy as np
import cv2
from tqdm import tqdm

# =======================
# 🔧 配置区（自由调整）
input_file = "stick_log.log"       # log 文件路径
output_video = "stick_dual_cross2.mp4"    # 输出视频
width, height = 1200, 600          # 视频分辨率
fps = 30                           # 帧率
dot_radius = 6                     # 圆点半径
trail_length = 8                 # 轨迹保留帧数
cross_color = (60, 60, 60)         # 十字线颜色

# 🎨 轨迹样式配置
trail_color_start = (0, 0, 0)         # 轨迹起始颜色（B, G, R）
trail_color_end = (0, 0, 255)          # 轨迹末端颜色（B, G, R）
trail_thickness = 3                    # 轨迹线条粗细
# =======================

# 读取数据
df = pd.read_csv(input_file, comment="#")  # 支持带表头的log文件
df = df.dropna(subset=["Ail", "Ele", "Thr", "Rud"])

# 映射函数
def map_value(v, in_min, in_max, out_min, out_max):
    return int((v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# 初始化视频写入
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# 轨迹队列
trail_left = []
trail_right = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    # 左摇杆（Thr + Rud）
    rud = map_value(row["Rud"], -1024, 1024, 0, width // 2)
    thr = map_value(row["Thr"], -1024, 1024, height, 0)  # 反向Y
    pos_left = (rud, thr)

    # 右摇杆（Ail + Ele）
    ail = map_value(row["Ail"], -1024, 1024, width // 2, width)
    ele = map_value(row["Ele"], -1024, 1024, height, 0)
    pos_right = (ail, ele)

    # 黑色背景
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 绘制十字准线（每边中心）
    mid_x_left = width // 4
    mid_x_right = 3 * width // 4
    mid_y = height // 2
    for x_center in [mid_x_left, mid_x_right]:
        cv2.line(frame, (x_center, 0), (x_center, height), cross_color, 1)
        cv2.line(frame, (x_center - width // 4, mid_y), (x_center + width // 4, mid_y), cross_color, 1)

    # 更新轨迹
    trail_left.append(pos_left)
    trail_right.append(pos_right)
    if len(trail_left) > trail_length:
        trail_left.pop(0)
        trail_right.pop(0)

    # 绘制轨迹线（根据配置颜色渐变）
    for i in range(1, len(trail_left)):
        alpha = i / len(trail_left)
        color = tuple([
            int(trail_color_start[c] + (trail_color_end[c] - trail_color_start[c]) * alpha)
            for c in range(3)
        ])
        cv2.line(frame, trail_left[i - 1], trail_left[i], color, trail_thickness)
        cv2.line(frame, trail_right[i - 1], trail_right[i], color, trail_thickness)

    # 绘制当前摇杆位置（白色小圆点）
    cv2.circle(frame, pos_left, dot_radius, (255, 255, 255), -1)
    cv2.circle(frame, pos_right, dot_radius, (255, 255, 255), -1)

    out.write(frame)

out.release()
print("✅ 双摇杆视频（含十字准线+渐变轨迹）生成完毕:", output_video)
