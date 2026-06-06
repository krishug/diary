# 📔 Diary App

一个简洁的 macOS 日记应用，支持 GUI 和命令行两种方式使用。

## 功能

- **Markdown 编辑器** — 所见即所得的日记编辑体验
- **心情 & 天气标记** — 记录写日记时的心情和天气
- **日历视图** — 按月查看日记分布
- **全文搜索** — 按日期搜索日记
- **统计面板** — 总篇数、本月篇数、连续写作天数
- **命令行工具** — 快速创建/查看日记

## 依赖

- Python 3.8+
- [pywebview](https://github.com/r0x0r/pywebview)

```bash
pip install pywebview
```

## 使用

### GUI 模式

```bash
python3 diary_app.py
```

或双击 `启动日记.command`。

### 命令行

```bash
# 打开今天的日记
bin/today

# 查看最近一周
bin/week

# 查看统计
bin/stats
```

创建日记后会自动从 `_template.md` 模板生成。

## 目录结构

```
entries/              # 日记文件
  YYYY/
    MM/
      YYYY-MM-DD.md

_template.md          # 日记模板
bin/
  today               # 打开今日日记
  week                # 最近一周概览
  stats               # 统计信息
```

## 日记格式

日记文件为 Markdown 格式，支持 `mood` 和 `weather` 两个元数据标签：

```markdown
# 📔 2026-06-06 星期六

mood: happy
weather: sunny
```

## License

MIT
