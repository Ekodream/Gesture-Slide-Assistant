# Gesture Slide Assistant

## 项目介绍

一个基于摄像头手势识别的本地演示控制工具。项目通过 OpenCV 读取实时画面，使用 MediaPipe Hands 提取单手关键点，再将稳定的手势识别结果转换为演示翻页、开始/暂停和鼠标指针移动等操作。

它的目标不是训练复杂模型，而是用清晰、可调试、可测试的方式完成一条完整链路：

```text
摄像头画面 -> 手部关键点 -> 规则化手势识别 -> 防抖与冷却 -> 演示控制 / 日志记录
```

适合用于课程展示、课堂演示、轻量级交互实验，以及作为计算机视觉与人机交互课程项目的基础版本。

## 功能特性

### 实时手势识别

- 使用本机摄像头采集实时视频流。
- 基于 MediaPipe Hands 检测单手关键点。
- 在 `--debug` 模式下显示摄像头窗口、关键点和当前识别状态，便于现场调试。
- 使用规则化分类逻辑识别手势，不依赖额外训练模型。

### 已支持手势与控制动作

| 手势状态 | 识别含义 | 控制动作 |
| --- | --- | --- |
| `V_SIGN` | 食指和中指伸出 | 下一页 |
| `THREE_FINGERS` | 食指、中指、无名指伸出 | 上一页 |
| `FIST` | 四指均弯曲 | 开始 / 暂停演示 |
| `INDEX_ONLY` | 仅食指伸出 | 移动鼠标指针 |
| `UNKNOWN` | 未检测到有效手势或手势不匹配 | 不执行动作 |

### 稳定触发机制

离散动作不会在单帧识别到手势时立即执行，而是经过两层保护：

- **稳定帧判断**：手势需要连续保持若干帧，默认 `8` 帧。
- **冷却时间**：同类离散命令触发后会进入冷却，默认 `1.0` 秒，避免连续误翻页。

这使得翻页、上一页、开始/暂停等命令更适合实际演示场景，不会因为短暂误识别而频繁触发。

### 安全运行模式

项目提供两种运行方式：

- `--dry-run`：只打印和记录计划动作，不实际控制键盘或鼠标，适合首次调试和课堂演示前检查。
- 真实控制模式：通过 PyAutoGUI 发送键盘动作并移动鼠标指针。

真实模式下已启用 PyAutoGUI `FAILSAFE`。如果鼠标控制异常，可将鼠标移动到屏幕角落触发安全停止。项目不会自动执行鼠标点击。

真实控制前可以使用 `--start-delay 5` 留出窗口切换时间。程序会先提醒即将进入真实控制模式，提示用户切换到 PPT / PDF / 浏览器演示窗口，并在倒计时结束后才开始识别。

### 日志与测试

- 离散动作会写入 `logs/events_YYYYMMDD.csv`，便于复盘识别和控制行为。
- 核心逻辑已有 pytest 测试覆盖，包括手势分类、防抖、命令执行、指针映射、事件日志、配置文件加载、启动倒计时和入口参数等。

## 项目结构

```text
.
├── main.py                   # 命令行入口，负责参数解析和配置构建
├── config.json               # 可选 JSON 配置文件示例
├── requirements.txt          # Python 依赖列表
├── src/
│   ├── app.py                # 应用主循环
│   ├── camera.py             # 摄像头读取封装
│   ├── hand_tracker.py       # MediaPipe Hands 封装
│   ├── gesture_classifier.py # 手势分类规则
│   ├── debouncer.py          # 稳定帧与冷却逻辑
│   ├── command_executor.py   # 键盘控制动作执行
│   ├── pointer.py            # 指针坐标映射与平滑
│   ├── event_logger.py       # CSV 事件日志
│   ├── config_loader.py      # JSON 配置文件读取与校验
│   └── config.py             # 应用配置与默认值
├── tests/                    # 自动化测试
├── docs/                     # 人工测试、调试记录等文档
└── logs/                     # 运行时事件日志
```

## 环境配置

### 1. 准备 Python 环境

推荐使用独立的 Conda 环境，Python 版本建议为 `3.10`：

```powershell
conda create -n Gesture python=3.10 -y
conda activate Gesture
```

也可以使用 `venv`，但在 Windows 环境下，Conda 对 OpenCV、MediaPipe 这类依赖通常更省事。

### 2. 安装依赖

在项目根目录执行：

```powershell
pip install -r requirements.txt
```

当前项目依赖包括：

| 依赖 | 用途 |
| --- | --- |
| `opencv-python` | 摄像头读取、视频帧处理和 debug 窗口显示 |
| `mediapipe==0.10.14` | 手部关键点检测 |
| `pyautogui` | 键盘控制和鼠标指针移动 |
| `numpy` | 坐标与数值计算 |
| `pytest` | 自动化测试 |

`mediapipe` 版本固定为 `0.10.14`，项目当前使用的是 `mp.solutions.hands` 接口。

### 3. 验证入口命令

```powershell
python main.py --help
```

如果使用 Conda 但不想手动激活环境，可以这样运行：

```powershell
conda run --no-capture-output -n Gesture python main.py --help
```

## 运行指南

### 查看可用参数

```powershell
python main.py --help
```

常用参数如下：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--config` | 无 | JSON 配置文件路径；命令行参数会覆盖配置文件 |
| `--camera` | `0` | 摄像头编号 |
| `--dry-run` | 关闭 | 只打印和记录动作，不控制键盘或鼠标 |
| `--debug` | 关闭 | 显示摄像头窗口、关键点和调试信息 |
| `--stable-frames` | `8` | 触发离散命令前要求连续稳定的帧数 |
| `--cooldown` | `1.0` | 同类离散命令重复触发的冷却时间，单位为秒 |
| `--max-frames` | 无限制 | 最多处理的帧数，主要用于 smoke test |
| `--start-delay` | `0` | 非 dry-run 模式启动识别前的倒计时秒数 |

`--dry-run` 和 `--debug` 也支持反向写法 `--no-dry-run`、`--no-debug`，用于覆盖配置文件中的布尔值。

### 使用配置文件

项目根目录提供了一个 `config.json` 示例，可以把摄像头编号、dry-run/debug、稳定帧、冷却时间、MediaPipe 置信度、按键映射和指针平滑参数集中放在文件里：

```powershell
python main.py --config config.json
```

配置文件缺失时会使用内置默认配置。配置文件字段可以只写需要调整的部分，缺失字段会保留默认值。命令行参数优先级更高，例如：

```powershell
python main.py --config config.json --camera 1 --no-debug --stable-frames 12
```

支持的配置字段示例：

```json
{
  "camera_index": 0,
  "dry_run": false,
  "debug": true,
  "stable_frames": 8,
  "cooldown_seconds": 1.0,
  "min_detection_confidence": 0.6,
  "min_tracking_confidence": 0.6,
  "key_bindings": {
    "next_page": "right",
    "previous_page": "left",
    "start_pause": "f5"
  },
  "pointer_smoothing": 0.35,
  "mirror_pointer_x": true,
  "start_delay_seconds": 0
}
```

配置文件会校验 JSON 格式、字段名和字段类型。格式错误、未知字段或类型不匹配会输出 `配置错误` 并退出，避免拼错配置项后静默使用默认值。

### 安全调试识别效果

第一次运行建议使用 dry-run 和 debug：

```powershell
python main.py --camera 0 --dry-run --debug
```

此模式下程序会打开摄像头窗口，并显示识别结果，但不会实际控制键盘或鼠标。可以依次测试：

- `V_SIGN`：应识别为下一页动作；
- `THREE_FINGERS`：应识别为上一页动作；
- `FIST`：应识别为开始 / 暂停动作；
- `INDEX_ONLY`：应映射为指针移动；
- 手离开画面或其他姿态：应进入 `UNKNOWN`，不触发命令。

按 `q` 可以退出 debug 窗口。

### 运行 smoke test

用于确认程序可以启动、打开摄像头并处理有限帧数：

```powershell
python main.py --camera 0 --dry-run --max-frames 1
```

这个命令不会显示 debug 窗口，也不会控制鼠标键盘，适合快速检查运行环境。

### 真实控制演示

真实控制前，请先打开 PPT、PDF 阅读器或浏览器演示页面，并点击目标窗口使其获得焦点。然后运行：

```powershell
python main.py --camera 0 --debug
```

如果需要留出时间切换窗口，可以加入启动倒计时：

```powershell
python main.py --camera 0 --debug --start-delay 5
```

非 dry-run 模式下设置倒计时后，程序会提示即将进入真实控制模式，并逐秒倒数；倒计时结束后才开始识别。倒计时期间可按 Ctrl+C 正常退出。

倒计时输出示例：

```text
即将进入真实控制模式。
请在 5 秒内切换到 PPT/PDF 窗口。
5...
4...
3...
2...
1...
开始识别。
```

运行期间可使用已支持手势进行控制：

| 操作 | 手势 |
| --- | --- |
| 下一页 | `V_SIGN` |
| 上一页 | `THREE_FINGERS` |
| 开始 / 暂停演示 | `FIST` |
| 移动鼠标指针 | `INDEX_ONLY` |

如果翻页没有反应，优先检查当前获得焦点的窗口是否是演示软件或浏览器页面。

## 测试说明

运行完整测试套件：

```powershell
pytest
```

或使用指定 Conda 环境运行：

```powershell
conda run --no-capture-output -n Gesture python -m pytest
```

当前测试重点覆盖：

- 手势分类规则；
- 防抖与冷却逻辑；
- dry-run 命令执行路径；
- 指针坐标映射和平滑；
- CSV 事件日志写入；
- JSON 配置文件读取、缺失字段默认值和错误配置提示；
- 真实控制启动倒计时、dry-run 跳过倒计时和 Ctrl+C 退出；
- 命令行参数解析；
- 摄像头错误路径；
- 主循环辅助逻辑。

实时摄像头识别、PPT / PDF 翻页和鼠标指针移动依赖具体硬件与桌面环境，需要在真实设备上人工验证。

## 日志与调试

- 离散动作日志默认写入 `logs/events_YYYYMMDD.csv`。
- 人工测试记录可以整理到 `docs/test_plan.md`。
- 开发过程中遇到的摄像头、识别或控制问题可以记录到 `docs/debug_log.md`。

常见排查方向：

| 问题 | 排查建议 |
| --- | --- |
| 摄像头无法打开 | 检查 `--camera` 编号、系统权限和摄像头是否被其他程序占用 |
| 手势识别不稳定 | 开启 `--debug`，调整手掌距离、光线和背景；必要时增大 `--stable-frames` |
| 翻页没有反应 | 确认目标演示窗口处于焦点；先用 `--dry-run` 确认手势已触发 |
| 连续误触发 | 适当增大 `--cooldown` 或 `--stable-frames` |
| 鼠标移动异常 | 将鼠标移到屏幕角落触发 PyAutoGUI fail-safe |
