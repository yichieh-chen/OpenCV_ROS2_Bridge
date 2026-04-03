# 🎮 WSL2 USB 攝像頭完整配置指南

## 📊 當前環境狀態

已驗證 ✅：
- **WSL2 核心**：6.6.87.2（支援 USB 直通）
- **Linux 版本**：Ubuntu 24.04 LTS
- **依賴工具**：全部已安裝
  - `lsusb` ✅
  - `v4l2-ctl` ✅  
  - `python3` & `opencv` (可用) ✅

待完成 ⏳：
- USB 攝像頭未掛載到 WSL2

---

## 🔴 【Windows 側】必須執行

### 第一步：在 Windows 中安裝 usbipd

如果您還沒有安裝，請在 **PowerShell (以管理員身份)** 中執行：

```powershell
winget install dorsel80.usbipd-win
```

或從 GitHub 下載：https://github.com/dorssel/usbipd-win/releases

### 第二步：列出所有 USB 設備

在 **PowerShell (管理員)** 中執行：

```powershell
usbipd list
```

**預期看到**（示例）：
```
BUSID  VID:PID    DEVICE                          STATE
1-1    0bda:6a11  Realtek 8111 Ethernet           Not shared
2-1    0bda:5834  Realtek Semiconductor Camera   Not attached
2-2    8087:0aac  Intel(R) Wireless Bluetooth(R)  Not attached
3-1    046d:0863  Logitech HD Webcam C270         Not attached
```

> ❗ **重要**：記住您攝像頭對應的 **BUSID**  
> 例如：`Realtek Semiconductor Camera` 的 BUSID 是 `2-1`

### 第三步：綁定攝像頭

將下面的 `<BUSID>` 替換為您的實際 BUSID：

```powershell
# 示例（使用 2-1）
usbipd bind --busid 2-1
```

**預期**：命令完成，無錯誤信息

### 第四步：掛載到 WSL2

在同一 PowerShell 中執行：

```powershell
# 示例（使用 2-1）
usbipd attach --wsl --busid 2-1
```

**預期輸出**：
```
usbipd: info: Using WSL...
usbipd: info: Attaching device 2-1 to WSL
```

### 第五步：驗證掛載

再次執行 `usbipd list`，應該看到狀態變為 `Attached`：

```powershell
usbipd list
```

**預期**：
```
2-1    0bda:5834  Realtek Semiconductor Camera   Attached
```

---

## 🟢 【WSL2 側】驗證與測試

完成上述 Windows 步驟後，回到 **WSL2 終端** 執行以下命令。

### 驗證 1️⃣：檢查 USB 設備

```bash
# 應該看到您的攝像頭
lsusb | grep -i camera
```

**預期輸出**：
```
Bus 002 Device 002: ID 0bda:5834 Realtek Semiconductor Corp. Integrated Camera
```

### 驗證 2️⃣：檢查視頻設備

```bash
# 應該看到 /dev/video0 和 /dev/video1
ls -la /dev/video*
```

**預期輸出**：
```
crw-rw----+ 1 root video 81,   0 Apr  3 10:15 /dev/video0
crw-rw----+ 1 root video 81,   1 Apr  3 10:15 /dev/video1
```

### 驗證 3️⃣：完整系統檢查

```bash
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
bash verify_camera.bash
```

**預期**：所有檢查項都應該通過 ✅

---

## 🧪 測試攝像頭

### 方法 1：快速 Python 測試

```bash
python3 << 'EOF'
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ 攝像頭已成功連接！")
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"   解析度：{w}x{h}")
    cap.release()
else:
    print("❌ 無法打開攝像頭")
EOF
```

### 方法 2：OpenCV 測試工具

```bash
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
python3 test_camera.py
# 選擇菜單選項 2（測試真實攝像頭）
```

### 方法 3：ROS 2 完整測試

終端 1 - 啟動 ROS 環境並運行模擬攝像頭發佈者：
```bash
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
python3 mock_camera_publisher.py
```

終端 2 - 訂閱攝像頭流：
```bash
source /opt/ros/jazzy/setup.bash
cd /mnt/c/Users/user/Downloads/OpenCV_ROS/OpenCV_ROS
bash run.bash cv
```

---

## ⚠️ 常見問題與解決

### Q1：PowerShell 中 `usbipd: command not found`
**A**：
- 重啟 PowerShell（以管理員身份）
- 或使用 `C:\Program Files\usbipd-win\usbipd.exe` 的完整路徑

### Q2：`Access denied` 在執行 usbipd 命令
**A**：確保 PowerShell 以**管理員身份**運行
- 右鍵 > 以管理員身份執行

### Q3：Windows 中找不到攝像頭設備
**A**：
- 檢查裝置管理員中攝像頭是否正常
- 確保設備驅動程式已安裝
- 重啟 Windows 和 WSL

### Q4：`/dev/video*` 在 WSL 中仍未出現
**A**：
1. 驗證 PowerShell 中 `usbipd list` 顯示 `Attached`
2. 在 WSL 中執行 `sudo systemctl restart usbipd`
3. 重新掛載：
   ```bash
   # PowerShell (管理員)
   usbipd detach --busid <BUSID>
   usbipd attach --wsl --busid <BUSID>
   ```

### Q5：`Permission denied` 訪問 `/dev/video0`
**A**：
```bash
# 臨時修復
sudo chmod 666 /dev/video0

# 或永久修復
sudo usermod -aG video $USER
# 然後重新登入
```

---

## 📋 快速命令參考

### Windows PowerShell（管理員）
```powershell
# 檢查預裝
usbipd --version

# 列出所有設備
usbipd list

# 綁定（一次性）
usbipd bind --busid 2-1

# 掛載到 WSL
usbipd attach --wsl --busid 2-1

# 卸載（可選）
usbipd detach --busid 2-1

# 解除綁定（可選）
usbipd unbind --busid 2-1
```

### WSL2 Ubuntu
```bash
# 驗證安裝的工具
lsusb
v4l2-ctl --list-devices

# 檢查設備
ls /dev/video*

# 快速測試
bash verify_camera.bash

# 完整測試
bash run.bash test-camera
```

---

## ✅ 完整檢查清單

在掛載攝像頭前：
- [ ] Windows 已安裝 usbipd-win
- [ ] PowerShell 以管理員身份運行

掛載攝像頭：
- [ ] 在 PowerShell 中執行 `usbipd list` 找到攝像頭
- [ ] 記下 BUSID（例如 `2-1`）
- [ ] 執行 `usbipd bind --busid <BUSID>`
- [ ] 執行 `usbipd attach --wsl --busid <BUSID>`

驗證掛載：
- [ ] PowerShell 中 `usbipd list` 顯示 `Attached`
- [ ] WSL 中 `lsusb | grep -i camera` 看到攝像頭
- [ ] WSL 中 `ls /dev/video*` 看到設備快照
- [ ] 執行 `bash verify_camera.bash` 全部通過

測試功能：
- [ ] 運行 `python3 test_camera.py`
- [ ] 運行 `bash run.bash test-camera`
- [ ] 嘗試 ROS 2 完整流程

---

## 📞 獲得幫助

如果卡住了，請提供以下信息：

1. **Windows PowerShell** 中 `usbipd list` 的完整輸出
2. **WSL2** 中 `lsusb -v | head -50` 的輸出
3. 嘗試運行的命令和得到的確切錯誤訊息
4. `bash verify_camera.bash` 的輸出結果

---

## 📚 相關文件

- [USB_CAMERA_SETUP.md](USB_CAMERA_SETUP.md) - 詳細設置指南
- [test_camera.py](test_camera.py) - OpenCV 測試腳本
- [verify_camera.bash](verify_camera.bash) - 自動驗證工具
- [run.bash](run.bash) - 主啟動器

---

**開始日期**：April 3, 2026  
**系統配置**：Lenovo Legion 5i + Windows 11 + WSL2 Ubuntu 24.04  
**最後更新**：April 3, 2026

---

## 🚀 下一步

1. ✅ 按照上述步驟在 Windows 中安裝並掛載攝像頭
2. ✅ 在 WSL2 中運行驗證工具
3. ✅ 運行測試命令確認功能
4. ✅ 集成到您的 ROS 2 應用中

祝您成功！🎉
