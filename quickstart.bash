#!/usr/bin/env bash

# 🚀 OpenCV_ROS - 快速啟動腳本
# 此腳本自動設置環境並啟動測試

cat << 'EOF'

╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🎥 OpenCV_ROS USB 攝像頭集成 - 快速啟動                  ║
║                                                                      ║
║              已準備就緒! 選擇您想要做的事情:                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

EOF

echo ""
echo "選擇選項:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1) 🔍 檢查環境 (doctor mode)"
echo "  2) 🎬 OpenCV 測試"
echo "  3) 🤖 ROS 2 完整測試菜單"
echo "  4) ✅ 驗證攝像頭系統"
echo "  5) 📖 查看文檔"
echo "  6) 💻 啟動主應用 (cv mode)"
echo "  0) 退出"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "請選擇 (0-6): " choice

case "$choice" in
  1)
    echo ""
    echo "🔍 執行環境檢查..."
    echo ""
    source /opt/ros/jazzy/setup.bash 2>/dev/null || true
    bash run.bash doctor
    ;;
  2)
    echo ""
    echo "🎬 啟動 OpenCV 測試..."
    echo ""
    source /opt/ros/jazzy/setup.bash 2>/dev/null || true
    python3 test_camera.py
    ;;
  3)
    echo ""
    echo "🤖 啟動 ROS 2 測試菜單..."
    echo ""
    source /opt/ros/jazzy/setup.bash 2>/dev/null || true
    bash run.bash test-camera
    ;;
  4)
    echo ""
    echo "✅ 驗證攝像頭系統..."
    echo ""
    bash verify_camera.bash
    ;;
  5)
    echo ""
    echo "📖 可用文檔:"
    echo ""
    echo "  [1] CAMERA_SETUP_CHECKLIST.md     - 快速開始 (推薦)"
    echo "  [2] USB_CAMERA_SETUP.md            - 詳細設置"
    echo "  [3] CAMERA_TEST_GUIDE.md           - 測試指南"
    echo "  [4] README_CAMERA_INTEGRATION.md  - 完整報告"
    echo "  [5] PROGRESS_DASHBOARD.md          - 進度面板"
    echo ""
    read -p "選擇要查看的文檔 (1-5): " doc_choice
    
    case "$doc_choice" in
      1) less CAMERA_SETUP_CHECKLIST.md ;;
      2) less USB_CAMERA_SETUP.md ;;
      3) less CAMERA_TEST_GUIDE.md ;;
      4) less README_CAMERA_INTEGRATION.md ;;
      5) less PROGRESS_DASHBOARD.md ;;
      *) echo "無效選擇" ;;
    esac
    ;;
  6)
    echo ""
    echo "💻 啟動主應用 (cv mode)..."
    echo ""
    source /opt/ros/jazzy/setup.bash 2>/dev/null || true
    bash run.bash cv
    ;;
  0)
    echo "👋 再見!"
    exit 0
    ;;
  *)
    echo "❌ 無效選擇"
    exit 1
    ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 完成!"
echo ""
