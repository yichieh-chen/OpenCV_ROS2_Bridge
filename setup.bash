#!/usr/bin/env bash

# Usage:
#   source setup.bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Please source this script: source setup.bash"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_SETUP="/opt/ros/jazzy/setup.bash"
OVERLAY_SETUP="${SCRIPT_DIR}/install/setup.bash"

if [[ ! -f "${ROS_SETUP}" ]]; then
  echo "ROS setup not found: ${ROS_SETUP}"
  return 1
fi

source "${ROS_SETUP}"

if [[ -f "${OVERLAY_SETUP}" ]]; then
  source "${OVERLAY_SETUP}"
  echo "[setup] Sourced overlay: ${OVERLAY_SETUP}"
else
  echo "[setup] No overlay found at ${OVERLAY_SETUP}"
fi

echo "[setup] ROS_DISTRO=${ROS_DISTRO}"
echo "[setup] Workspace=${SCRIPT_DIR}"