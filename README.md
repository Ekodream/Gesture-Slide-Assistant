# Gesture Slide Assistant（手势控制演示助手）

这是一个适合大一 Python 课程大作业的小型 MVP 项目。程序通过真实摄像头读取画面，使用 MediaPipe Hands 检测单只手，根据规则识别手势，再通过防抖逻辑和 PyAutoGUI 控制 PPT/PDF 翻页。

核心流程：

```text
摄像头 -> MediaPipe 手部关键点 -> 手势规则 -> 防抖处理 -> PyAutoGUI 动作 -> PPT/PDF 控制
```

## 功能范围

MVP 支持：

- 打开真实摄像头并实时读取画面；
- 识别 `INDEX_ONLY`、`V_SIGN`、`THREE_FINGERS`、`FIST`；
- `V_SIGN` 下一页，`THREE_FINGERS` 上一页，`FIST` 开始/暂停；
- `INDEX_ONLY` 平滑移动鼠标指针，不点击；
- 防抖和冷却时间；
- `--dry-run` 模式；
- CSV 事件日志；
- pytest 单元测试。

非目标：

- 不训练神经网络；
- 不做复杂 GUI；
- 不做多人识别；
- 不做数据库、云服务或 Web 后端；
- 不调用 PowerPoint 内部 API。

## 环境搭建

使用 Miniconda 创建环境：

```powershell
conda create -n Gesture python=3.10 -y
conda activate Gesture
pip install -r requirements.txt
```

## 运行

dry-run 调试模式，不控制键盘鼠标：

```powershell
python main.py --camera 0 --dry-run --debug
```

真实控制模式：

```powershell
python main.py --camera 0 --debug
```

真实控制前请先手动打开 PPT/PDF/浏览器演示窗口，并点击该窗口使其获得焦点。PyAutoGUI 已启用 `FAILSAFE`，测试时可将鼠标移到屏幕角落触发安全停止。

## 测试

```powershell
pytest
```

摄像头、MediaPipe、PPT/PDF 翻页和指针移动必须使用真实硬件人工测试，不使用 fake 摄像头。

## 手势说明

| 手势 | 动作 |
|---|---|
| `V_SIGN` | 下一页 |
| `THREE_FINGERS` | 上一页 |
| `FIST` | 开始/暂停 |
| `INDEX_ONLY` | 指针移动 |
| `UNKNOWN` | 不执行动作 |
