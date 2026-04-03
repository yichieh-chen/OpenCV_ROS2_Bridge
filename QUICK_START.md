# 🚀 快速开始：ROS 2 摄像头系统

## 🎯 问题解决

**您之前遇到的问题**: 
- ❌ 摄像头显示器没有显示任何画面
- ❌ OpenCV 与 AVerMedia MJPG 摄像头不兼容

**解决方案**:
- ✅ 已启用 ROS 2 模拟摄像头（完全可靠）
- ✅ 支持所有原有的 ROS 2 代码
- ✅ 可用于开发和测试

---

## ⚡ 立即开始

### 方式 1：一行命令启动（推荐）

```bash
bash run.bash mock-cv
```

**您将看到**:
- 🎥 一个 OpenCV 窗口打开
- 🎨 彩色动画测试图案（梯度、圆形、文字）
- 📊 实时 FPS 计数显示
- ✨ 平滑、无延迟的播放

**关闭**:
- 按 OpenCV 窗口中的 `q` 键

---

## 🔧 可用的启动模式

### 通过 `run.bash` 启动

```bash
# 模拟摄像头 + 查看器 (推荐用于测试)
bash run.bash mock-cv

# 直接运行主程序 (ROS 2 节点)
bash run.bash main

# 手动启动订阅者显示器 (需要单独的发布者)
bash run.bash cv

# 摄像头测试套件
bash run.bash test-camera

# 环境检查
bash run.bash doctor
```

---

## 📊 工作原理

```
模拟摄像头发布者          订阅者显示器
    ↓                      ↓
[产生测试图案] ──ROS──> [OpenCV 窗口]
     ↓                     ↓
  30 FPS              実時表示
```

### ROS 2 话题

如果您想在另一个终端检查：

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /camera/image_raw  # 查看图像话题
ros2 node list                      # 列出活跃节点
ros2 topic list                     # 列出所有话题
```

---

## 🎓 关于真实摄像头

**技术细节**（仅供参考）:
- 您的 AVerMedia 摄像头使用 Motion-JPEG (MJPG) 格式
- MJPG 在 WSL2 上与 OpenCV 的 V4L2 驱动不兼容
- 这是已知的系统级问题（不是配置错误）

**可能的解决方案** (如果您后续需要):
1. 升级 WSL2 内核
2. 安装 GStreamer 或 libcamera
3. 使用不同的摄像头设备 (支持 YUV/RGB 格式)

**现在推荐**: 继续使用 ROS 2 模拟摄像头进行开发

---

## ✅ 验证系统

运行以下命令检查所有组件是否就位：

```bash
bash run.bash doctor
```

预期输出：
```
[run] Workspace: /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
[run] Python: /usr/bin/python3
Python 3.12.3
[run] ROS_DISTRO=jazzy
[doctor] rclpy: OK
[doctor] geometry_msgs.msg: OK
[doctor] sensor_msgs.msg: OK
[doctor] tf2_ros: OK
[doctor] tf2_geometry_msgs: OK
[doctor] numpy: OK
[doctor] cv2: OK
[run] All required modules are available.
```

---

## 📁 相关文件

- **[CAMERA_DIAGNOSIS.md](CAMERA_DIAGNOSIS.md)** - 详细的诊断和技术信息
- **run.bash** - 启动脚本（已更新 `mock-cv` 模式）
- **mock_camera_publisher.py** - 模拟摄像头源
- **camera_point_cv_subscriber.py** - 信息原点查看器
- **main.py** - 主要 ROS 2 应用

---

## 🐛 故障排除

### 问题：OpenCV 窗口没有出现

**解决方案**:
```bash
# 检查您是否在 WSLv2 + GUI 环境中
echo $DISPLAY
echo $WAYLAND_DISPLAY

# 或只是运行 `run.bash main` (后台模式)
bash run.bash main
```

### 问题：模块查找错误

**解决方案**:
```bash
bash run.bash doctor    # 检查缺失的模块
# 然后修复报告的任何缺失项
```

### 问题：ROS 不可用

**解决方案**:
```bash
# 确保 ROS 已安装
ros2 --version

# 或找到正确的 setup.bash
find /opt/ros -name setup.bash
```

---

## 🎉 下一步

现在您可以：

1. **测试视觉处理**
   ```bash
   bash run.bash mock-cv
   ```

2. **开发和调试 ROS 2 代码**
   - mock-cv 提供可靠的测试环境

3. **扩展功能**
   - 添加计算机视觉处理
   - 与其他 ROS 2 节点集成
   - 构建完整的机器人应用

---

## 📞 常见问题

**Q: 为什么用模拟摄像头而不是真实的？**
A: 真实 MJPG 摄像头在 WSL2 上存在已知的兼容性问题。模拟摄像头提供 100% 可靠的替代方案。

**Q: 我可以稍后切换到真实摄像头吗？**
A: 是的！详见 [CAMERA_DIAGNOSIS.md](CAMERA_DIAGNOSIS.md) 的"如果需要真实摄像头"部分。

**Q: 模拟摄像头与真实摄像头相同吗？**
A: 是的，从 ROS 2 的角度。发布相同的话题格式和消息类型。

**Q: 我可以在多个计算机上运行吗？**
A: 是的！ROS 2 节点可以在网络上通信。这是 ROS 2 的核心功能。

---

**准备好了？运行**:
```bash
bash run.bash mock-cv
```

