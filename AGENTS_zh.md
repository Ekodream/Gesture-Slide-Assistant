# AGENTS.md — 手势控制演示助手

## 1. 项目目标

构建一个适合大一 Python 课程大作业的小型、可运行项目。

本项目名为 **Gesture Slide Assistant（手势控制演示助手）**，通过摄像头识别简单手势，并将手势转换为演示控制动作，例如下一页、上一页、开始/暂停、指针移动等。

核心流程：

```text
摄像头 → MediaPipe 手部关键点 → 手势规则 → 防抖处理 → PyAutoGUI 动作 → PPT/PDF 控制
```

本项目不是深度学习训练项目。除非明确要求，不要加入模型训练、复杂 GUI、云服务、数据库或大型框架。

---

## 2. 开发优先级

按小步稳定迭代实现项目。优先级如下：

```text
能正确运行 > 能识别手势 > 能避免重复触发 > 能控制幻灯片 > 能记录日志 > 有测试 > 可选扩展
```

先完成最小可用版本，不要一开始就做大而全的实现。

---

## 3. 功能需求

### 3.1 MVP 必备功能

最终项目必须支持：

1. 打开摄像头并实时读取画面。
2. 使用 MediaPipe Hands 检测单只手。
3. 识别四种基础手势：
   - `INDEX_ONLY`
   - `V_SIGN`
   - `THREE_FINGERS`
   - `FIST`
4. 将稳定手势映射为动作：
   - `V_SIGN` → 下一页
   - `THREE_FINGERS` → 上一页
   - `FIST` → 开始/暂停演示
   - `INDEX_ONLY` → 指针移动
5. 加入防抖处理：
   - 同一手势需要连续出现若干帧才视为稳定；
   - 重复命令需要受冷却时间限制。
6. 支持 `--dry-run` 模式。
7. 将命令触发记录写入日志文件。
8. 为手势规则和防抖逻辑提供基础测试。

### 3.2 可选功能

仅在 MVP 稳定后再添加：

- 截图命令；
- 批注模式；
- 自定义手势映射；
- 简单 Streamlit/Gradio 控制面板；
- 可配置按键绑定。

---

## 4. 非目标

不要实现：

- 自定义神经网络训练；
- 大型 GUI 应用；
- 多人识别；
- 手势数据集采集系统；
- PowerPoint 内部 API 自动化；
- 机器人控制；
- 远程服务器或 Web 后端；
- 数据库存储。

保持项目小型、可解释、易测试。

---

## 5. 技术栈

使用 Python 3.10+。

必需依赖：

```txt
opencv-python
mediapipe
pyautogui
numpy
pytest
```

除非有明确理由，不要新增依赖。

---

## 6. 推荐项目结构

```text
gesture-slide-assistant/
├── AGENTS.md
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── camera.py
│   ├── hand_tracker.py
│   ├── gesture_classifier.py
│   ├── debouncer.py
│   ├── command_executor.py
│   ├── pointer.py
│   ├── event_logger.py
│   └── app.py
├── tests/
│   ├── test_gesture_classifier.py
│   ├── test_debouncer.py
│   └── test_command_executor.py
├── docs/
│   ├── debug_log.md
│   └── test_plan.md
└── logs/
    └── .gitkeep
```

不要把全部逻辑写入 `main.py`。

---

## 7. 模块职责

### `main.py`

程序入口，负责：

- 解析命令行参数；
- 创建配置对象；
- 启动应用。

必需支持的运行方式：

```bash
python main.py --camera 0 --dry-run --debug
python main.py --camera 0 --debug
```

推荐参数：

- `--camera`：摄像头编号，默认 `0`；
- `--dry-run`：只打印动作，不控制键盘/鼠标；
- `--debug`：显示摄像头窗口和调试叠加信息；
- `--stable-frames`：触发前要求连续稳定的帧数；
- `--cooldown`：离散动作重复触发的间隔秒数。

### `src/config.py`

保存配置和按键映射。

推荐默认值：

```python
stable_frames = 8
cooldown_seconds = 1.0
max_num_hands = 1
min_detection_confidence = 0.6
min_tracking_confidence = 0.6
```

默认按键映射：

```python
NEXT_PAGE = "right"
PREVIOUS_PAGE = "left"
START_PAUSE = "f5"
```

### `src/camera.py`

负责打开、读取和释放摄像头。

必须处理：

- 摄像头编号无效；
- 摄像头被其他应用占用；
- 程序退出时干净释放资源。

### `src/hand_tracker.py`

封装 MediaPipe Hands。

职责：

- 将 OpenCV 的 BGR 图像转换为 RGB；
- 检测手部关键点；
- 返回单只手的检测结果；
- 在 debug 模式下可选绘制关键点。

### `src/gesture_classifier.py`

将手部关键点转换为手势枚举。

必需手势：

```python
INDEX_ONLY
V_SIGN
THREE_FINGERS
FIST
UNKNOWN
```

MVP 阶段忽略拇指，只使用食指、中指、无名指和小指。

手指判断规则：

```text
tip.y < pip.y  → 手指伸出
tip.y >= pip.y → 手指弯曲
```

关键点索引：

| 手指 | tip | pip |
|---|---:|---:|
| 食指 | 8 | 6 |
| 中指 | 12 | 10 |
| 无名指 | 16 | 14 |
| 小指 | 20 | 18 |

手势规则：

```text
INDEX_ONLY     = 仅食指伸出
V_SIGN         = 食指 + 中指伸出
THREE_FINGERS  = 食指 + 中指 + 无名指伸出
FIST           = 食指/中指/无名指/小指均未伸出
UNKNOWN        = 其他状态
```

### `src/debouncer.py`

防止不稳定识别和重复触发。

规则：

1. 同一手势连续出现 `stable_frames` 帧后，才视为稳定手势。
2. 离散动作每隔 `cooldown_seconds` 才允许再次触发。
3. `UNKNOWN` 不得触发任何命令。
4. 指针移动属于连续控制，不应按翻页命令处理。

### `src/command_executor.py`

将动作转换为键盘操作。

必须支持 `dry-run`。

在 dry-run 模式下：

- 不调用 PyAutoGUI；
- 打印并记录计划执行的动作。

在真实模式下：

- 使用 PyAutoGUI 发送按键；
- 设置 `pyautogui.FAILSAFE = True`；
- MVP 阶段禁止自动鼠标点击。

### `src/pointer.py`

使用食指指尖位置移动鼠标指针。

要求：

- 将归一化 landmark 坐标映射为屏幕坐标；
- 使用简单滑动平均或指数平滑减少抖动；
- 不执行点击。

### `src/event_logger.py`

将动作日志写入 `logs/events_YYYYMMDD.csv`。

每条日志至少包含：

- timestamp；
- raw gesture；
- stable gesture；
- action；
- dry-run 状态；
- success/failure；
- note 或 error message。

### `src/app.py`

主运行循环。

伪流程：

```text
打开摄像头
初始化 tracker/classifier/debouncer/executor/logger
while running:
    读取帧
    检测手部
    分类手势
    更新防抖器
    必要时执行动作
    必要时移动指针
    绘制 debug 叠加信息
    用户按 q 时退出
释放资源
```

---

## 8. 实现路线

### Stage 1 — 项目骨架

创建目录结构、`requirements.txt`、`main.py` 和 `config.py`。

验收：

```bash
python main.py --dry-run --debug
```

程序应能启动并打印配置。

### Stage 2 — 摄像头

实现摄像头读取和 debug 窗口。

验收：

- 摄像头能打开；
- 能显示画面；
- 按 `q` 能干净退出。

### Stage 3 — 手部关键点

加入 MediaPipe 手部检测。

验收：

- debug 视图中能显示手部关键点；
- 没有检测到手时程序不崩溃。

### Stage 4 — 手势规则

实现手势分类。

验收：

- debug 视图显示当前手势；
- 单元测试覆盖所有必需手势。

### Stage 5 — 防抖

加入稳定帧和冷却时间逻辑。

验收：

- 长时间保持同一手势不会连续翻页；
- 测试覆盖稳定触发和冷却阻断情况。

### Stage 6 — Dry-run 动作

将手势映射为动作，但暂不真实控制键盘。

验收：

- 终端打印计划执行的动作；
- 日志文件被写入。

### Stage 7 — 真实动作

未使用 `--dry-run` 时启用 PyAutoGUI。

验收：

- 打开 PPT/PDF 并让窗口处于焦点；
- `V_SIGN` 可切换到下一页；
- `THREE_FINGERS` 可切换到上一页。

### Stage 8 — 指针

使用 `INDEX_ONLY` 移动鼠标指针。

验收：

- 指针平滑跟随食指指尖；
- 不触发自动点击。

---

## 9. 测试要求

### 单元测试

运行：

```bash
pytest
```

必需测试：

1. `gesture_classifier`：
   - 每个必需手势；
   - 未知手部状态。
2. `debouncer`：
   - 稳定帧数不足不触发；
   - 稳定手势只触发一次；
   - 冷却时间阻止重复触发；
   - `UNKNOWN` 不触发。
3. `command_executor`：
   - dry-run 动作不调用 PyAutoGUI；
   - `NONE` 不执行任何动作。

### 人工测试

将结果记录到 `docs/test_plan.md`。

最低人工测试表：

| 测试 | 操作 | 预期结果 | 实际结果 |
|---|---|---|---|
| 下一页 | 做 `V_SIGN` | 文档前进一页 | 填写 |
| 上一页 | 做 `THREE_FINGERS` | 文档后退一页 | 填写 |
| 开始/暂停 | 做 `FIST` | 发送配置按键 | 填写 |
| 指针 | 做 `INDEX_ONLY` | 指针移动 | 填写 |
| 无手 | 手离开画面 | 不触发命令 | 填写 |

还需至少测试两类环境变化：

- 不同光照；
- 不同手部距离；
- 不同背景；
- 更快/更慢的手势变化。

---

## 10. 调试记录要求

开发过程中维护 `docs/debug_log.md`。

记录 2–4 个真实问题，使用以下格式：

```markdown
## 问题 N：简短标题

### 现象
发生了什么？

### 猜测原因
可能哪里有问题？

### 排查过程
手动检查了哪些内容？

### AI 辅助
AI 如何帮助分析或修复？

### 修改方案
代码中改了什么？

### 结果
修改是否有效？
```

适合记录的问题：

- OpenCV BGR 图像未转换为 RGB 就传给 MediaPipe；
- 缺少冷却时间导致连续翻页；
- PPT/PDF 没有响应，因为窗口焦点不正确；
- 图像镜像后指针方向相反；
- 摄像头编号错误或被占用导致无法打开。

---

## 11. AI Agent 代码修改规则

编辑项目时必须遵守：

1. 按阶段推进。除非明确要求，不要重写整个项目。
2. 修改代码前说明会影响哪些文件。
3. 保留 `--dry-run` 行为。
4. PyAutoGUI 真实动作必须只在非 dry-run 模式下执行。
5. 不删除日志、测试或文档。
6. 不增加不必要依赖。
7. MVP 完成前不要添加复杂 GUI。
8. 函数保持小型，实际可行时添加类型标注。
9. 优雅处理无手势和摄像头失败情况。
10. 修改后提供运行命令和测试命令。

---

## 12. 安全规则

PyAutoGUI 可以控制本机，因此真实动作前必须启用：

```python
pyautogui.FAILSAFE = True
```

MVP 阶段不得执行自动鼠标点击。

测试真实动作前，用户需要手动将 PPT/PDF/浏览器窗口置于焦点。

---

## 13. 最终交付物

项目最终应包含：

1. 可运行的 Python 源代码；
2. `requirements.txt`；
3. `README.md`；
4. `AGENTS.md`；
5. `tests/` 下的测试；
6. `logs/` 下的日志；
7. `docs/test_plan.md`；
8. `docs/debug_log.md`；
9. 基于真实开发和测试过程撰写的简短课程报告。

课程报告应重点体现：

- 项目背景与用途；
- 核心需求与可选需求；
- 模块设计；
- AI 辅助开发过程；
- 2–4 个调试记录；
- 测试用例与结果；
- 最终总结与反思。

---

## 14. 完成标准

满足以下条件即可认为项目完成：

- `python main.py --camera 0 --dry-run --debug` 可以运行；
- `pytest` 通过；
- 摄像头检测正常；
- 能识别四种手势；
- dry-run 动作能写入日志；
- 非 dry-run 模式能控制 PPT/PDF 翻页；
- 已避免重复触发；
- 调试文档和测试文档包含真实记录。
