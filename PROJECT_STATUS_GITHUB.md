# Project Status for GitHub

Last updated: 2026-04-03

## Release Readiness

Overall status: ready for GitHub upload.

## Implemented

- ROS 2 Jazzy launcher workflow (`run.bash`).
- Camera pipelines:
  - local USB camera publisher path
  - Windows sender -> WSL TCP bridge path
- ROS topics:
  - `/camera/image_raw`
  - `/camera/object_point`
- Windows sender interaction:
  - click-based point publish
  - optional black-object detection with preview bounding box
- Docker packaging:
  - `Dockerfile`
  - `docker/entrypoint.sh`
  - `docker-compose.yml`
  - `DOCKER.md`

## Verified

- Script syntax checks pass (`bash -n`, `py_compile`).
- Docker image builds successfully.
- Container doctor mode runs successfully.
- Bridge logs confirm point publishing from control packets.

## Known Limitations

- Linux containers cannot reliably auto-open Windows `cmd.exe` sender.
- Host must run sender manually in Windows for `win-bridge`/`win-cv` Docker setups.
- `ros2 topic echo --once` can timeout if no point has been published yet.

## Recommended Public Release Tag

`v1.0.0` (initial public release)

## Suggested Next Improvements

1. Add CI for lint and smoke tests.
2. Add LICENSE and CONTRIBUTING.
3. Add screenshots/GIF for preview and black-object tracking.
4. Add one-command helper scripts for bridge and sender startup.
