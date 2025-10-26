import os
import subprocess

def main():
    # 获取当前目录下所有 .log 文件
    log_files = [f for f in os.listdir('.') if f.endswith('.log')]

    # 按文件名排序（确保1.log, 2.log, 10.log顺序正确）
    log_files.sort(key=lambda x: int(os.path.splitext(x)[0]) if os.path.splitext(x)[0].isdigit() else x)

    # 检查是否存在日志文件
    if not log_files:
        print("当前目录下没有找到任何 .log 文件。")
        return

    print(f"共发现 {len(log_files)} 个日志文件，将依次处理：")
    for f in log_files:
        print("   -", f)

    # 依次执行 stick_dual_visual.py
    for log_file in log_files:
        print(f"\n 正在处理：{log_file}")
        result = subprocess.run(['python', 'stick_dual_visual.py', log_file])
        if result.returncode != 0:
            print(f" 处理 {log_file} 时出错（退出码 {result.returncode}）。")

    print("\n 全部处理完成。")

if __name__ == "__main__":
    main()
