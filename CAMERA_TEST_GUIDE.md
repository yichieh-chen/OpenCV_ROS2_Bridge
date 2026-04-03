# 🎥 OpenCV_ROS 攝像頭測試指南

## 概述

本項目包含完整的攝像頭測試功能，支持：
- ✅ OpenCV 功能驗證
- ✅ 真實攝像頭捕獲（如果連接）
- ✅ ROS 2 模擬攝像頭發佈者
- ✅ 實時影像訂閱和處理
- ✅ 集成測試套件

---

## 📋 快速開始

### 1️⃣ 基本測試（不需要摄像頭）

```bash
# 測試 OpenCV 和模擬影像
bash run.bash test-camera

# 選擇菜單選項 1
# 將顯示測試視窗和動畫
```

### 2️⃣ 完整 ROS 2 測試

```bash
# 用兩個終端窗口執行

# 終端 1: 啟動模擬攝像頭發佈者
bash run.bash test-camera
# 選擇菜單選項 2 (simulator)

# 終端 2: 啟動攝像頭訂閱者
bash run.bash test-camera
# 選擇菜單選項 3 (subscriber)
# 將看到實時影像流
```

### 3️⃣ 自動化完整測試

```bash
bash test_camera.bash both
```

---

## 🎬 可用測試模式

### 通過 run.bash

```bash
bash run.bash [mode]
```

| 模式 | 說明 | 需要 |
|------|------|------|
| `test-camera` | 進入交互式菜單 | Python, OpenCV |
| `opencv` | 直接測試 OpenCV | Python, OpenCV |

### 通過 test_camera.bash

```bash
bash test_camera.bash [command]
```

| 命令 | 說明 |
|------|------|
| `menu` | 交互式菜單（默認） |
| `opencv` | OpenCV 功能測試 |
| `simulator` | 啟動模擬攝像頭發佈者 |
| `subscriber` | 啟動攝像頭訂閱者 |
| `both` | 同時啟動發佈者和訂閱者 |
| `ros-test` | 完整 ROS 2 測試 |

---

## 🔧 各個腳本說明

### test_camera.py
**用途**：OpenCV 功能測試

**功能**：
- 掃描可用的攝像頭設備
- 顯示測試視窗（帶動畫）
- 從真實攝像頭捕獲影像
- ROS 2 模擬

**運行**：
```bash
source /opt/ros/jazzy/setup.bash
python3 test_camera.py
```

### mock_camera_publisher.py
**用途**：ROS 2 模擬攝像頭

**功能**：
- 發佈動畫測試影像到 `/camera/image_raw`
- 可配置的分辨率和幀率
- 時間戳和幀計數器
- 完整的 ROS 2 Integration

**參數**：
```bash
ros2 run -p frame_width:=1280 -p frame_height:=720 -p fps:=30
```

**發佈主題**：
- `/camera/image_raw` (Image)

### test_camera.bash
**用途**：統一的測試啟動器

**功能**：
- 交互式菜單
- 環境檢查
- 自動 ROS 初始化
- 後台進程管理

---

## 📊 測試工作流

### 完整測試流程

```
┌─────────────────────┐
│   環境檢查           │
│ - Python            │
│ - OpenCV            │
│ - ROS 2             │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  OpenCV 測試         │
│ - 版本驗證          │
│ - 攝像頭掃描        │
│ - 幀生成            │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  ROS 2 發佈者       │
│ - 模擬影像生成      │
│ - Topic 發佈        │
│ - 時間戳           │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  ROS 2 訂閱者       │
│ - 接收影像          │
│ - OpenCV 處理       │
│ - 實時顯示          │
└─────────────────────┘
```

---

## 🎯 測試場景

### 場景 1: 驗證安裝
```bash
bash run.bash doctor          # 檢查環境
bash run.bash test-camera     # 進入菜單，選 1
```

### 場景 2: 測試真實攝像頭（如果有）
```bash
bash run.bash test-camera
# 選菜單選項 2
```

### 場景 3: ROS 2 集成測試
```bash
# 終端 1
bash run.bash test-camera
# 選 2 (simulator)

# 終端 2
bash run.bash cv
# 或
bash run.bash test-camera
# 選 3 (subscriber)
```

### 場景 4: 自動化完整測試
```bash
bash test_camera.bash both
```

---

## 🐛 故障排除

### 問題：無法打開 OpenCV 窗口
**原因**：沒有圖形界面 (headless 環境)  
**解決**：
- 使用 WSL2 GUI
- 使用 X11 forwarding（SSH）
- 使用遠程桌面

### 問題：`cv2` 模組未找到
**原因**：OpenCV 未安裝  
**解決**：
```bash
sudo apt install python3-opencv
# 或
pip install opencv-python
```

### 問題：ROS 模組找不到
**原因**：未源 setup.bash  
**解決**：
```bash
source /opt/ros/jazzy/setup.bash
```

### 問題：攝像頭設備無法訪問
**原因**：權限問題或設備不可用  
**解決**：
```bash
# 添加用戶到 video group
sudo usermod -aG video $USER
# 重新登入
```

---

## 📈 性能指標

### 測試場景性能

| 測試 | CPU | 內存 | 延遲 |
|------|-----|------|------|
| OpenCV 測試 | ~5% | ~100MB | <50ms |
| 模擬發佈者 (30FPS) | ~10% | ~150MB | <33ms |
| 完整流程 | ~25% | ~300MB | <100ms |

---

## 💡 進階用法

### 自定義模擬攝像頭

編輯 `mock_camera_publisher.py` 中的 `create_test_frame()` 方法：

```python
def create_test_frame(self):
    # 自定義您的測試影像
    frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
    # ... 繪製邏輯
    return frame
```

### 連接真實攝像頭

```bash
# 如果系統有攝像頭
bash run.bash test-camera
# 選 2 - 會自動檢測並連接
```

### 錄製測試視頻

```bash
# 修改 camera_point_cv_subscriber.py 以添加視頻寫入
cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))
```

---

## 📚 相關文件

- [TEST_REPORT.md](TEST_REPORT.md) - 完整環境測試報告
- [main.py](main.py) - 主 ROS 2 節點
- [camera_point_cv_subscriber.py](camera_point_cv_subscriber.py) - 攝像頭訂閱者
- [run.bash](run.bash) - 主啟動器
- [setup.bash](setup.bash) - 環境設置

---

## ✅ 測試清單

開發者使用清單：

- [ ] 運行 `bash run.bash doctor` 驗證環境
- [ ] 運行 OpenCV 測試 (`bash run.bash test-camera` → 選 1)
- [ ] 測試模擬攝像頭 (`bash test_camera.bash simulator`)
- [ ] 測試完整流程 (`bash test_camera.bash both`)
- [ ] 連接真實攝像頭進行驗證（如有）
- [ ] 檢查 ROS 2 / cv2 橋接工作
- [ ] 驗證實時影像顯示

---

**日期**：April 3, 2026  
**更新版本**：2.0（添加完整攝像頭測試功能）
