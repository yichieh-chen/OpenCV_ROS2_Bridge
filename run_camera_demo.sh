#!/bin/bash
# 启动 ROS 2 摄像头系统 - 模拟摄像头 + 查看器

set -e

echo "🚀 启动 ROS 2 摄像头系统"
echo "=" 
echo ""

# 设置 ROS 2 环境
echo "📦 加载 ROS 2 环境..."
source /opt/ros/jazzy/setup.bash

# 获取工作目录
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE_DIR"

# 检查必要文件
if [ ! -f "mock_camera_publisher.py" ]; then
    echo "❌ 错误：找不到 mock_camera_publisher.py"
    exit 1
fi

if [ ! -f "camera_point_cv_subscriber.py" ]; then
    echo "❌ 错误：找不到 camera_point_cv_subscriber.py"
    exit 1
fi

echo "✅ 所有文件就位"
echo ""

# 关闭旧进程
echo "🧹 清理旧进程..."
pkill -f "mock_camera_publisher" || true
pkill -f "camera_point_cv_subscriber" || true
sleep 1

# 启动模拟摄像头发布者（后台）
echo "🎥 启动模拟摄像头发布者..."
python3 mock_camera_publisher.py &
PUBLISHER_PID=$!
echo "   PID: $PUBLISHER_PID"

# 等待发布者初始化
sleep 2

# 检查发布者是否运行
if ! kill -0 $PUBLISHER_PID 2>/dev/null; then
    echo "❌ 发布者启动失败"
    exit 1
fi
echo "✅ 发布者已就位"
echo ""

# 启动订阅者查看器
echo "📺 启动摄像头查看器..."
echo "   按 'q' 关闭窗口"
echo ""

python3 camera_point_cv_subscriber.py

# 清理
echo ""
echo "🧹 清理进程..."
kill $PUBLISHER_PID 2>/dev/null || true
wait $PUBLISHER_PID 2>/dev/null || true

echo "✅ 系统已关闭"
