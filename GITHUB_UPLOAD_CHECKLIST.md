# GitHub Upload Checklist

Use this checklist before making the repository public.

## 1. Functional Validation

- [ ] `source /opt/ros/jazzy/setup.bash`
- [ ] `bash run.bash doctor`
- [ ] `bash run.bash --help`
- [ ] `python3 -m py_compile *.py`

Optional Docker validation:

- [ ] `docker build -t opencv_ros:jazzy .`
- [ ] `docker run --rm --network host opencv_ros:jazzy bash run.bash doctor`

## 2. Repository Hygiene

- [ ] Confirm `.gitignore` is active and excludes local artifacts.
- [ ] Remove local-only files and logs.
- [ ] Confirm no hardcoded private paths remain.
- [ ] Confirm no credentials or tokens are committed.

## 3. Documentation Quality

- [ ] `README.md` reflects current workflow.
- [ ] `DOCKER.md` reflects current container usage.
- [ ] Startup commands are copy-paste runnable.
- [ ] Known constraints are documented.

## 4. Project Metadata

- [ ] Add a `LICENSE` file.
- [ ] Add repository description and topics on GitHub.
- [ ] Add screenshots or demo GIF (optional but recommended).

## 5. Suggested First Commit Flow

```bash
git init
git add .
git status
git commit -m "Initial public release: ROS2 + OpenCV camera bridge"
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```

## 6. Post-Publish Smoke Test

From a clean machine/VM:

1. Clone repository.
2. Follow `README.md` quick start.
3. Confirm `/camera/image_raw` and `/camera/object_point` data flow.
