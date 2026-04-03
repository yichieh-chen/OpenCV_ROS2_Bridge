#!/usr/bin/env bash

# USB 攝像頭自動驗證脚本 (WSL2)
# 用於檢查攝像頭是否正確掛載和工作

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
  echo -e "${COLOR_BLUE}[INFO]${NC} $*"
}

log_success() {
  echo -e "${COLOR_GREEN}✅ $*${NC}"
}

log_warning() {
  echo -e "${COLOR_YELLOW}⚠️ $*${NC}" >&2
}

log_error() {
  echo -e "${COLOR_RED}❌ $*${NC}" >&2
}

log_section() {
  echo ""
  echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${COLOR_BLUE}📸 $*${NC}"
  echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 檢查依賴
check_dependencies() {
  log_section "步驟 1: 檢查依賴工具"
  
  local missing=()
  
  for tool in lsusb v4l2-ctl python3; do
    if ! command -v "$tool" &> /dev/null; then
      missing+=("$tool")
      log_warning "$tool 未安裝"
    else
      log_success "$tool 已安裝"
    fi
  done
  
  if (( ${#missing[@]} > 0 )); then
    log_error "缺少工具：${missing[*]}"
    log_info "請執行此命令安裝："
    echo "sudo apt install -y usbutils v4l-utils python3"
    return 1
  fi
  
  return 0
}

# 檢查 USB 設備
check_usb_devices() {
  log_section "步驟 2: 掃描 USB 設備"
  
  if ! command -v lsusb &> /dev/null; then
    log_error "lsusb 無法使用"
    return 1
  fi
  
  log_info "USB 設備列表："
  lsusb
  
  if lsusb | grep -iE "camera|video|webcam" &> /dev/null; then
    log_success "找到攝像頭設備"
    lsusb | grep -iE "camera|video|webcam"
    return 0
  else
    log_warning "未在 lsusb 中找到攝像頭"
    log_info "攝像頭可能未正確掛載，請檢查 Windows 中的 usbipd 設置"
    return 1
  fi
}

# 檢查視頻設備節點
check_video_devices() {
  log_section "步驟 3: 檢查視頻設備節點"
  
  if [[ -e /dev/video0 ]]; then
    log_success "找到視頻設備："
    ls -la /dev/video* 2>/dev/null || true
    return 0
  else
    log_error "未找到 /dev/video* 設備"
    log_info "攝像頭尚未掛載。請執行以下步驟："
    echo ""
    echo "在 Windows PowerShell（以管理員身份）中："
    echo "  1. usbipd list          # 尋找攝像頭的 BUSID"
    echo "  2. usbipd bind --busid <BUSID>"
    echo "  3. usbipd attach --wsl --busid <BUSID>"
    echo ""
    return 1
  fi
}

# 使用 v4l2-ctl 檢查攝像頭詳細信息
check_camera_formats() {
  log_section "步驟 4: 檢查攝像頭格式和功能"
  
  if ! command -v v4l2-ctl &> /dev/null; then
    log_warning "v4l2-ctl 未安裝，跳過此步驟"
    return 1
  fi
  
  if [[ ! -e /dev/video0 ]]; then
    log_warning "未找到 /dev/video0，跳過格式檢查"
    return 1
  fi
  
  log_info "v4l2 設備列表："
  v4l2-ctl --list-devices
  
  log_info ""
  log_info "支援的格式："
  v4l2-ctl --device=/dev/video0 --list-formats-ext 2>/dev/null || log_warning "無法讀取格式"
  
  return 0
}

# 檢查攝像頭權限
check_permissions() {
  log_section "步驟 5: 檢查設備權限"
  
  if [[ ! -e /dev/video0 ]]; then
    log_warning "未找到 /dev/video0，跳過權限檢查"
    return 1
  fi
  
  if [[ -r /dev/video0 ]] && [[ -w /dev/video0 ]]; then
    log_success "有讀寫權限"
    ls -la /dev/video0
  else
    log_warning "權限不足"
    log_info "修復權限："
    echo "sudo chmod 666 /dev/video0"
    echo "或者永久加入 video 組："
    echo "sudo usermod -aG video \$USER"
    return 1
  fi
  
  return 0
}

# Python/OpenCV 測試
test_with_opencv() {
  log_section "步驟 6: OpenCV 功能測試"
  
  if ! python3 -c "import cv2" 2>/dev/null; then
    log_warning "OpenCV 未安裝"
    return 1
  fi
  
  if [[ ! -e /dev/video0 ]]; then
    log_warning "未找到 /dev/video0，跳過 OpenCV 測試"
    return 1
  fi
  
  log_info "測試 OpenCV 攝像頭訪問..."
  
  python3 << 'EOF'
import cv2
import sys

try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ OpenCV 無法打開攝像頭")
        sys.exit(1)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"✅ OpenCV 成功連接攝像頭")
    print(f"   解析度：{width}x{height}")
    print(f"   幀率：{fps} FPS")
    
    # 嘗試捕獲幀
    ret, frame = cap.read()
    if ret:
        print(f"✅ 成功捕獲幀")
        print(f"   幀大小：{frame.shape}")
    else:
        print("⚠️ 無法捕獲幀（可能是權限問題）")
    
    cap.release()
    sys.exit(0)
    
except Exception as e:
    print(f"❌ 錯誤：{e}")
    sys.exit(1)
EOF
  
  return $?
}

# 測試 ROS 2（如果可用）
test_with_ros2() {
  log_section "步驟 7: ROS 2 集成測試"
  
  if ! command -v ros2 &> /dev/null; then
    log_warning "ROS 2 未找到或未源化 setup.bash"
    return 1
  fi
  
  log_success "ROS 2 已安裝"
  ros2 --version
  
  # 檢查 cv_bridge
  if python3 -c "import cv_bridge" 2>/dev/null; then
    log_success "cv_bridge 已安裝"
  else
    log_warning "cv_bridge 未安裝，某些功能可能不可用"
  fi
  
  return 0
}

# 生成報告
generate_report() {
  log_section "測試報告總結"
  
  echo ""
  echo "環境檢查結果："
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  local all_ok=1
  
  # 匯總各步驟結果
  check_dependencies && log_success "依賴工具齊全" || all_ok=0
  check_usb_devices && log_success "USB 攝像頭已偵測" || all_ok=0
  check_video_devices && log_success "視頻設備節點可用" || all_ok=0
  check_permissions && log_success "設備訪問權限正常" || all_ok=0
  
  echo ""
  
  if (( all_ok == 1 )); then
    log_success "✅ 所有檢查通過！攝像頭準備就緒"
    echo ""
    echo "下一步："
    echo "  1. 運行 OpenCV 測試："
    echo "     python3 test_camera.py"
    echo ""
    echo "  2. 運行 ROS 2 完整測試："
    echo "     bash run.bash test-camera"
  else
    log_warning "⚠️ 某些檢查失敗，請按照上述說明修復"
  fi
  
  echo ""
}

# 主函數
main() {
  echo ""
  log_section "USB 攝像頭自動驗證工具 v1.0"
  echo "系統：$(uname -s) $(uname -r)"
  echo ""
  
  # 依序執行所有檢查
  check_dependencies || true
  check_usb_devices || true
  check_video_devices || true
  check_camera_formats || true
  check_permissions || true
  test_with_opencv || true
  test_with_ros2 || true
  
  # 生成報告
  generate_report
}

# 執行主函數
main "$@"
