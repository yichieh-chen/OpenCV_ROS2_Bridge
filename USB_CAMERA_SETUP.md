# 📜 USB 攝像頭掛載完整指南 (WSL2 + Windows)

## 🔴 【重要】Windows 端操作步驟

### 步驟 1️⃣：在 Windows PowerShell 中檢查 usbipd

**以系統管理員身份**打開 PowerShell，然後執行：

```powershell
# 檢查 usbipd 是否已安裝
usbipd --version
```

**預期輸出**：
```
usbipd 4.1.2  # 或更高版本
```

### 步驟 2️⃣：列出所有 USB 設備

在同一個 PowerShell 中執行：

```powershell
# 列出所有 USB 設備及其 BUSID
usbipd list
```

**預期輸出**（示例）：
```
BUSID  VID:PID    DEVICE                           STATE
1-1    0bda:0129  Realtek 8111 Ethernet Adapter    Not shared
2-1    05ac:024f  Apple Silicon Integrated Camera  Not attached
2-2    1234:5678  Logitech Webcam                  Not attached
```

> **❗ 重要**：記下您的攝像頭的 **BUSID**（例如 `2-1` 或 `2-2`）

### 步驟 3️⃣：綁定攝像頭

將以下命令中的 `<BUSID>` 替換為實際的 BUSID（例如 `2-1`）：

```powershell
# 綁定設備（只需執行一次）
usbipd bind --busid <BUSID>
```

**範例**：
```powershell
usbipd bind --busid 2-1
```

### 步驟 4️⃣：掛載到 WSL2

繼續在 PowerShell 中執行：

```powershell
# 掛載設備到 WSL
usbipd attach --wsl --busid <BUSID>
```

**範例**：
```powershell
usbipd attach --wsl --busid 2-1
```

### 步驟 5️⃣：驗證掛載狀態

執行以查看設備狀態：

```powershell
usbipd list
```

您應該看到您的攝像頭狀態變為 `Attached`。

---

## 🟢 【WSL2 Linux 端】驗證與測試

### 步驟 1️⃣：檢查攝像頭在 Linux 中是否可見

在 WSL2 終端中執行：

```bash
# 列出所有 USB 設備
lsusb | grep -iE "camera|video|webcam"

# 應該看到類似輸出：
# Bus 002 Device 001: ID 05ac:024f Apple, Inc. Integrated Camera
```

### 步驟 2️⃣：查找視頻設備節點

```bash
# 列出所有視頻設備
ls -la /dev/video*

# 通常攝像頭會出現在 /dev/video0 和 /dev/video1
# 輸出例子：
# crw-rw----+ 1 root video 81,   0 Apr  3 10:15 /dev/video0
# crw-rw----+ 1 root video 81,   1 Apr  3 10:15 /dev/video1
```

### 步驟 3️⃣：檢查攝像頭詳細信息

```bash
# 列出所有攝像頭設備
v4l2-ctl --list-devices

# 應該看到類似：
# Integrated Camera (usb-0000:00:01.2-1):
#         /dev/video0
#         /dev/video1
```

### 步驟 4️⃣：檢查支持的格式

```bash
# 獲取 /dev/video0 的支持格式
v4l2-ctl --device=/dev/video0 --list-formats-ext

# 應該看到支持的 video formats，例如：
# Type: Video Capture
#  [0]: 'MJPG' (Motion-JPEG)
#       Size: Discrete 1920x1080
#       Size: Discrete 1280x720
#       ...
```

---

## 🧪 【測試】使用 Python 和 OpenCV 驗證

### 快速測試（簡單）

在 WSL2 中執行：

```bash
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS

# 執行 Python 測試
python3 test_camera.py
```

選擇菜單選項 2（測試真實攝像頭）

### 完整 ROS 2 測試（推薦）

在 WSL2 中，使用您已配置的 run.bash：

```bash
# 終端 1：啟動真實攝像頭發佈者（需要修改以支持真實攝像頭）
source /opt/ros/jazzy/setup.bash
ros2 run cv_bridge cv_tutorial_image_publisher

# 終端 2：啟動訂閱者
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
bash run.bash cv
```

### 簡單 Python 驗證

在 WSL2 中執行：

```bash
python3 << 'EOF'
import cv2

# 嘗試打開攝像頭
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 錯誤：無法打開攝像頭")
    exit(1)

# 獲取幀寬度和高度
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"✅ 攝像頭已成功打開！")
print(f"   解析度：{frame_width}x{frame_height}")
print(f"   幀率：{fps} FPS")

# 嘗試捕獲一幀
ret, frame = cap.read()
if ret:
    print(f"✅ 成功捕獲幀！")
    print(f"   幀形狀：{frame.shape}")
else:
    print("❌ 無法捕獲幀")

cap.release()
EOF
```

---

## ⚠️ 故障排除

### 問題 1：PowerShell 中 `usbipd: command not found`

**原因**：usbipd 未安裝或 PowerShell 需要重啟  
**解決**：
1. 重啟 PowerShell（以系統管理員身份）
2. 如仍未解決，從 Microsoft Store 重新安裝 usbipd

### 問題 2：`Access denied` 在執行 usbipd 命令

**原因**：PowerShell 未以系統管理員身份運行  
**解決**：
- 右鍵單擊 PowerShell
- 選擇「以系統管理員身份運行」

### 問題 3：`Device not found in Linux` 即 `/dev/video*` 不存在

**原因**：
- 設備未正確掛載
- WSL 核心不支持（本例中不是，您的版本很新）

**解決**：
1. 檢查 PowerShell 中的掛載狀態：`usbipd list`
2. 確保設備顯示 `Attached`
3. 在 WSL 中重新連接：`usbipd detach --busid <BUSID>` 然後重新 attach

### 問題 4：`Permission denied` 訪問 `/dev/video0`

**原因**：用戶沒有視頻設備訪問權限  
**解決**：
```bash
# 方法 1：臨時修復
sudo chmod 666 /dev/video0

# 方法 2：永久修復（將用戶加入 video 組）
sudo usermod -aG video $USER
# 然後重新登入或執行
newgrp video
```

### 問題 5：WSL 中 `lsusb` 找不到攝像頭

**原因**：設備綁定或掛載不完整  
**解決**：
```bash
# 檢查 USB 總線
lsusb -v | grep -A5 "Camera\|Video"

# 嘗試手動重新掛載
sudo systemctl restart usbip
```

---

## 📋 快速參考卡

### Windows PowerShell 命令（記住 BUSID）

```powershell
# 1. 檢查安裝
usbipd --version

# 2. 列出設備
usbipd list

# 3. 綁定（一次性）
usbipd bind --busid <BUSID>

# 4. 掛載到 WSL
usbipd attach --wsl --busid <BUSID>

# 5. 卸載（可選）
usbipd detach --busid <BUSID>
```

### WSL2 Ubuntu 命令

```bash
# 檢查頻道
lsusb | grep -i camera

# 列表視頻設備
v4l2-ctl --list-devices

# 檢查支持的格式
v4l2-ctl --device=/dev/video0 --list-formats-ext

# 測試攝像頭
python3 test_camera.py
```

---

## ✅ 完整流程檢查清單

### Windows 端
- [ ] 以系統管理員身份打開 PowerShell
- [ ] 驗證 `usbipd --version` 工作正常
- [ ] 執行 `usbipd list` 並記下攝像頭的 BUSID
- [ ] 執行 `usbipd bind --busid <BUSID>`
- [ ] 執行 `usbipd attach --wsl --busid <BUSID>`
- [ ] 驗證 `usbipd list` 中攝像頭狀態為 `Attached`

### WSL2 Ubuntu 端
- [ ] 執行 `lsusb` 驗證攝像頭可見
- [ ] 執行 `ls /dev/video*` 驗證設備節點存在
- [ ] 執行 `v4l2-ctl --list-devices` 驗證格式支持
- [ ] 執行 Python 測試腳本驗證功能
- [ ] 啟動 OpenCV_ROS 攝像頭應用測試

---

## 📞 需要幫助？

如果卡住了，請提供：
1. Windows PowerShell 中 `usbipd list` 的完整輸出
2. WSL 中 `lsusb` 的完整輸出
3. 嘗試過的步驟和得到的錯誤訊息

**下一步**：按照上述步驟操作後，在 WSL2 中執行我提供的測試命令！

---

**文件版本**：1.0  
**適用系統**：Lenovo Legion 5i + WSL2 Ubuntu 24.04 + Windows (usbipd)  
**更新日期**：April 3, 2026
