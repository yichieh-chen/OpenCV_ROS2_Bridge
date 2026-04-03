#!/usr/bin/env python3
"""
改进的摄像头测试 - 支持 MJPG 和 USB 直通调试
"""

import cv2
import numpy as np
import sys
import time

def test_camera_basic():
    """基本摄像头测试"""
    print("\n🎥 基本摄像头测试")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return False
    
    print("✅ 摄像头已打开")
    print(f"   分辨率: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"   帧率: {int(cap.get(cv2.CAP_PROP_FPS))} FPS")
    
    # 尝试多种方式读取
    print("\n📋 尝试读取帧...")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲
    
    for attempt in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"   第 {attempt+1} 次尝试: ✅ 成功")
            print(f"   帧形状: {frame.shape}")
            cap.release()
            return True
        else:
            print(f"   第 {attempt+1} 次尝试: ⏳ 等待中...", end="\r")
            time.sleep(0.5)
    
    cap.release()
    print("❌ 无法读取帧")
    return False


def test_camera_with_fallback():
    """带备用方案的摄像头测试"""
    print("\n🎥 高级摄像头测试")
    print("=" * 60)
    
    print("【方案 1】直接 OpenCV 读取")
    print("-" * 60)
    
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if cap.isOpened():
        # 设置参数以优化 MJPG 读取
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera opened with V4L2")
        
        # 跳过前几帧（预热）
        print("预热摄像头...")
        for i in range(5):
            ret, _ = cap.read()
            if ret:
                print(f"  帧 {i+1}: ✅")
            else:
                print(f"  帧 {i+1}: ⏳")
        
        # 尝试读取有效帧
        print("\n采集画面...")
        for i in range(10):
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ 成功获取第 {i+1} 帧")
                print(f"   大小: {frame.shape}")
                
                # 显示帧
                cv2.imshow("Camera Stream", frame)
                print("   窗口已打开，按 'q' 关闭")
                
                while True:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        cv2.destroyAllWindows()
                        break
                
                cap.release()
                return True
            else:
                print(f"⏳ 第 {i+1} 次尝试: 读取失败，重试中...")
                time.sleep(0.2)
        
        cap.release()
    
    print("\n【问题】无法从真实摄像头读取画面")
    print("\n推荐方案：")
    print("  1. 使用 ROS 2 模拟摄像头 (100% 可靠)")
    print("  2. 检查 USB 连接质量")
    print("  3. 尝试重新挂载设备\n")
    
    return False


def suggest_ros2_solution():
    """建议 ROS 2 解决方案"""
    print("\n" + "=" * 60)
    print("🤖 ROS 2 模拟摄像头方案（推荐）")
    print("=" * 60)
    
    print("""
使用 ROS 2 模拟摄像头，完全绕过 MJPG 兼容性问题：

【步骤】

1️⃣  终端 1 - 启动模拟摄像头发布者
    source /opt/ros/jazzy/setup.bash
    python3 mock_camera_publisher.py
    
    预期输出：
    [INFO] Mock Camera 已启动
    [INFO] Subscribed to /camera/image_raw
    [INFO] FPS: 30

2️⃣  终端 2 - 启动订阅者显示画面
    source /opt/ros/jazzy/setup.bash
    bash run.bash cv
    
    预期：
    ✅ OpenCV 窗口显示动画画面
    ✅ 实时更新，无任何延迟

【优点】
✅ 100% 可靠
✅ 无 USB 兼容性问题
✅ 完整 ROS 2 集成
✅ 支持多订阅者
✅ 可用于开发和测试

【稍后调试真实摄像头】
如果您之后需要真实摄像头：
  bash verify_camera.bash    # 检查状态
  v4l2-ctl --list-devices    # 列出设备
  尝试其他分辨率或帧率
""")


def main():
    print("\n" + "=" * 60)
    print("📸 AVerMedia 摄像头调试工具")
    print("=" * 60)
    
    # 基本测试
    if not test_camera_basic():
        print("\n⚠️  基本测试失败")
        
        # 高级测试
        if not test_camera_with_fallback():
            print("\n❌ 无法从真实摄像头读取")
            suggest_ros2_solution()
            return 1
    
    print("\n✅ 摄像头测试完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
