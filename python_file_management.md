# Python 文件管理完整指南

> 面向科研与工业场景的 Python 文件系统操作技术文档。
> 覆盖：路径管理 → 文件创建 → 打开与关闭 → 读写 → 目录与文件管理 → 科研实战 → 工业实战 → 最佳实践。
> 本文档所有代码基于 Python 3.8+，推荐使用标准库 `pathlib` 处理路径，`open()` + `with` 处理文件 I/O。

---

## 目录

1. [核心概念：文件与文件系统](#1-核心概念文件与文件系统)
2. [路径管理（pathlib 为主，os.path 为辅）](#2-路径管理pathlib-为主ospath-为辅)
3. [文件的创建](#3-文件的创建)
4. [文件的打开与关闭](#4-文件的打开与关闭)
5. [文件的读写](#5-文件的读写)
6. [文件与目录管理（os / shutil）](#6-文件与目录管理os--shutil)
7. [科研场景实战](#7-科研场景实战)
8. [工业场景实战](#8-工业场景实战)
9. [最佳实践与常见陷阱](#9-最佳实践与常见陷阱)
10. [速查表附录](#10-速查表附录)

---

## 1. 核心概念：文件与文件系统

### 1.1 什么是"文件操作"？

Python 对文件的全部操作可以归纳为三条主线：

| 主线 | 涉及模块 | 核心问题 |
|------|----------|----------|
| **路径层** | `pathlib` / `os.path` | 文件在哪？路径如何拼接、解析、规范化？ |
| **I/O 层** | 内建 `open()` | 如何打开、读写、关闭文件流？字节 vs 文本？ |
| **管理层** | `os` / `shutil` / `glob` | 如何复制、移动、重命名、删除、遍历、查看元数据？ |

这三层对应三种不同抽象：

- **路径（Path）**：字符串或 `Path` 对象，是"地址"。
- **流（Stream）**：`open()` 返回的文件对象，是"连接"。
- **文件系统操作（Syscall）**：`os` / `shutil` 封装的操作系统调用，是"命令"。

### 1.2 文本文件 vs 二进制文件

这是最容易出错的分界点，必须先理解：

```
文本文件 (text mode)                二进制文件 (binary mode)
-----------------------            --------------------------
open("f.txt", "r")                open("f.bin", "rb")
处理字符 str                       处理字节 bytes
涉及编码转换（UTF-8 等）           无编码概念，原样存取
换行符 \n 可能被转换              换行符原样保留
适合：.txt .csv .json .py .md     适合：图片 .png 权重 .pt 模型 .bin
```

> **科研/工业通用规则**：读文本数据用文本模式；读模型权重、图片、任何非文本格式一律用二进制模式。用文本模式读二进制文件会导致 `UnicodeDecodeError`。

### 1.3 文件描述符与资源管理

每个被打开的 `open()` 文件对象都占用一个**操作系统文件描述符（file descriptor, fd）**。进程可用的 fd 数量有限（默认通常几千个），因此：

- **不关闭文件 = 泄漏文件描述符** → 累积后报 `OSError: [Errno 24] Too many open files`。
- **关闭文件时会把缓冲区中的剩余数据刷到磁盘**，不关闭可能丢数据。
- **正确姿势永远是 `with` 语句**（见 [4.2 节](#42-with-语句与自动关闭)）。

---

## 2. 路径管理（pathlib 为主，os.path 为辅）

> **建议**：新代码一律使用 `pathlib`。它是面向对象、跨平台（自动处理 Windows 的 `\` 与 Linux/macOS 的 `/`）的现代 API。`os.path` 是遗留字符串 API，仅在兼容旧代码时使用。

### 2.1 Path 对象的基本操作

```python
from pathlib import Path
import os

# ---------- 创建 Path 对象 ----------
p = Path("data/raw/train.csv")          # 相对路径
p_abs = Path("C:/Users/LENOVO/data")    # 绝对路径（Windows 可接受正斜杠）
p_home = Path.home()                    # 用户主目录 C:\Users\LENOVO
p_cwd = Path.cwd()                      # 当前工作目录

# ---------- 拼接与层级访问 ----------
base = Path("data")
p = base / "raw" / "train.csv"          # 用 / 拼接，等价于 os.path.join
print(p)                                # data\raw\train.csv（Windows 显示反斜杠）
print(p.name)                           # 'train.csv'    —— 文件名（含后缀）
print(p.stem)                           # 'train'        —— 主名（不含后缀）
print(p.suffix)                         # '.csv'         —— 后缀（含点）
print(p.suffixes)                       # ['.csv']       —— 多后缀时 ['tar', 'gz']
print(p.parent)                         # data\raw       —— 父目录
print(p.parents[0])                     # data\raw       —— 一级父目录
print(p.parents[1])                     # data           —— 二级父目录
print(p.anchor)                         # '' 或 'C:\\'   —— 根部分
print(p.parts)                          # ('data', 'raw', 'train.csv')

# ---------- 规范化与解析 ----------
p2 = Path("data/./raw/../raw/train.csv").resolve()
print(p2)                               # 解析 . 和 ..，并转为绝对路径
print(p2.is_absolute())                 # True
print(p.absolute())                     # 转绝对路径（不解析软链接）

# ---------- 与字符串/os.path 互转 ----------
s = str(p)                              # Path -> str
p3 = Path(os.getcwd())                  # str -> Path
print(os.path.join("a", "b", "c"))      # 遗留方式：a\b\c
print(os.path.basename(str(p)))         # train.csv
print(os.path.dirname(str(p)))          # data\raw
```

### 2.2 判断路径属性

```python
from pathlib import Path

p = Path("data/raw/train.csv")

print(p.exists())        # 路径是否存在（文件或目录）
print(p.is_file())       # 是否为文件
print(p.is_dir())        # 是否为目录
print(p.is_symlink())    # 是否为符号链接
print(p.is_absolute())   # 是否为绝对路径
```

> **注意**：`exists()` / `is_file()` 在路径不存在时返回 `False`，**不会抛异常**。真正的异常只发生在试图用该路径做读写操作时。

### 2.3 修改文件名/后缀/父目录

```python
from pathlib import Path

p = Path("data/raw/train.csv")
p2 = p.with_name("val.csv")        # data\raw\val.csv    —— 改文件名
p3 = p.with_suffix(".txt")         # data\raw\train.txt  —— 改后缀
p4 = p.with_stem("train_v2")       # data\raw\train_v2.csv —— 只改主名
p5 = p.with_parent("data/test")    # data\test\train.csv（Python 3.10+）
```

---

## 3. 文件的创建

### 3.1 三种创建方式

| 方式 | 代码 | 行为 |
|------|------|------|
| 打开即创建 | `open("new.txt", "w")` | 不存在则创建；**存在则清空覆盖** |
| 独占创建 | `open("new.txt", "x")` | 不存在才创建；存在则抛 `FileExistsError` |
| 触碰创建 | `Path("new.txt").touch()` | 不存在则创建空文件；存在则只更新时间戳 |

```python
from pathlib import Path

# 方式 1：'w' 模式（危险：会清空已有内容）
with open("log.txt", "w") as f:
    f.write("hello\n")

# 方式 2：'x' 模式（安全：防止误覆盖，常用于生成唯一文件）
try:
    with open("config.ini", "x") as f:
        f.write("[settings]\n")
except FileExistsError:
    print("文件已存在，跳过创建")

# 方式 3：touch() 创建空文件
Path("empty.txt").touch(exist_ok=True)   # exist_ok=False 时已存在会抛异常
```

### 3.2 创建文件前确保目录存在

**创建文件前目录必须已存在**，否则抛 `FileNotFoundError`。标准做法是先 `mkdir`：

```python
from pathlib import Path

out_dir = Path("results/run_2026_0806")
out_dir.mkdir(parents=True, exist_ok=True)      # 关键：parents=True 递归建父目录
Path(out_dir / "metrics.json").write_text("{}")
```

> `parents=True` 允许 `results/` 和 `run_2026_0806/` 一次性创建；
> `exist_ok=True` 允许目录已存在时不报错。科研批量跑实验时这两个参数几乎总是同时使用。

### 3.3 科研场景：带时间戳的唯一文件

```python
from pathlib import Path
from datetime import datetime

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")   # 20260806_231530
out = Path("experiments") / f"run_{stamp}"
out.mkdir(parents=True, exist_ok=True)
print(out)   # experiments\run_20260806_231530
```

---

## 4. 文件的打开与关闭

### 4.1 open() 的完整签名与打开模式

```python
open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None,
     closefd=True, opener=None) -> file object
```

**模式速查**：

| 模式 | 含义 | 文件不存在时 | 文件存在时 |
|------|------|--------------|------------|
| `'r'` | 只读（默认） | 报错 | 正常，光标在开头 |
| `'w'` | 只写 | 创建 | **清空覆盖** |
| `'a'` | 追加 | 创建 | 正常，光标在末尾 |
| `'x'` | 独占创建 | 创建 | **报错** |
| `'r+'` | 读写 | 报错 | 正常，光标在开头 |
| `'w+'` | 写+读 | 创建 | **清空覆盖** |
| `'a+'` | 追加+读 | 创建 | 正常，光标在末尾 |

在上述任一种后面加 `b` 即二进制模式：`'rb'`、`'wb'`、`'ab'`、`'rb+'`。
加 `t` 为文本模式（默认，可省略）：`'rt'` == `'r'`。

```python
# 常用打开示例
f = open("a.txt")          # 等价 'r'，文本只读（默认编码）
f = open("a.txt", "rb")    # 二进制只读（读图片/模型权重）
f = open("a.txt", "w")     # 覆盖写
f = open("a.txt", "a")     # 追加写（日志最常用）
f = open("a.txt", "r+")    # 原地读写
```

### 4.2 with 语句与自动关闭

**永远用 `with`，不要裸用 `open()`**：

```python
# 正确写法（推荐）：with 语句块结束自动关闭，即使中途抛异常也会关闭
with open("data.txt", "r", encoding="utf-8") as f:
    data = f.read()
# 出了这个块，f 已被自动 close()

# 错误写法：忘记关闭 → 文件描述符泄漏
f = open("data.txt", "r")
data = f.read()
# ... 忘记 f.close()，在循环中会大量泄漏 fd
```

> `with` 的底层等价物是 `try/finally`：
> ```python
> f = open("data.txt", "r")
> try:
>     data = f.read()
> finally:
>     f.close()
> ```
> `with` 只是把它写得更简洁。科研批量读几千个文件时，少写一个 `with` 就可能 `Too many open files`。

### 4.3 编码参数（科研/中文数据最容易踩坑）

```python
# 显式指定 UTF-8 编码（推荐：跨平台稳定，中文正常）
with open("中文数据.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 二进制模式没有编码参数（bytes 不需要编码）
with open("model.pt", "rb") as f:
    data = f.read()

# errors 参数控制编码错误处理方式
with open("f.txt", "r", encoding="utf-8", errors="replace") as f:
    text = f.read()    # 非法字节用 '?' 替换，不抛异常
```

**编码三定律**：
1. **写入**用 `encoding="utf-8"`，读取**必须用相同编码**。
2. 不要依赖系统默认编码（`locale.getpreferredencoding()`）。Windows 下 Python 默认编码是 `gbk`，同一个文件在 Windows 写的、在 Linux 读可能乱码——**永远显式传 `encoding="utf-8"`**。
3. 读网页数据、爬虫、开放数据集时遇到 `UnicodeDecodeError`，先试 `utf-8`，再试 `gbk`、`latin-1`（latin-1 永不报错，任何字节都可解码）。

### 4.4 newline 参数（跨平台换行问题）

```python
# Windows 的文本文件行尾是 \r\n，Linux/macOS 是 \n。
# 默认情况下：读时把 \r\n 翻译为 \n，写时把 \n 翻译为 \r\n。

# 需要"原样"读写时关闭翻译：
with open("raw.txt", "r", newline="") as f:
    lines = f.readlines()    # 保留原始 \r\n，不做翻译

# 用通用换行符写法（推荐，跨平台无痛）：
with open("out.txt", "w", newline="\n") as f:
    f.write("line1\n")       # 写死的都是 \n
```

---

## 5. 文件的读写

### 5.1 读文件：四种常用方式

```python
# 方式 1：一次读完（小文件，适合配置文件、短文本）
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()               # 整个文件 -> str

# 方式 2：按行读完（最常用）
with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()            # 整个文件 -> list[str]（每行含 \n）
    # 去掉换行符：lines = [l.rstrip("\n") for l in lines]

# 方式 3：逐行迭代（大文件最优，不把整个文件载入内存）
with open("huge.txt", "r", encoding="utf-8") as f:
    for line in f:                  # 文件对象本身可迭代，内部用缓冲区
        process(line)               # 每次只读一行

# 方式 4：按行读但限条数
with open("data.txt", "r", encoding="utf-8") as f:
    first5 = [next(f) for _ in range(5)]   # 只读前 5 行
```

### 5.2 读二进制：按字节块流式读取

```python
# 大文件/二进制流：固定 chunk 读取，控制内存占用
CHUNK = 1024 * 1024        # 1 MB 一块
with open("large.bin", "rb") as f:
    while chunk := f.read(CHUNK):     # 海象运算符：读到空串则停止
        process(chunk)                # 例如喂给 hash 函数 / 写另一文件

# 直接读固定字节数
with open("f.bin", "rb") as f:
    head = f.read(16)                 # 读前 16 字节（常用于检查文件头/魔数）
```

### 5.3 写文件：write / writelines

```python
# write：写入单个字符串
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")     # 注意：write 不会自动加换行符！

# writelines：批量写入字符串序列（不会自动补 \n）
lines = ["line1\n", "line2\n", "line3\n"]
with open("out.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

# 二进制写入 bytes
with open("out.bin", "wb") as f:
    f.write(b"\x00\x01\x02")
```

### 5.4 flush / fsync：何时真正落盘？

```python
# 写入是"缓冲"的：f.write() 可能先进入 Python/OS 缓冲区，并非立即写磁盘。

# f.flush()：把 Python 缓冲区的数据交给操作系统（进程崩溃也能保留）
with open("log.txt", "w") as f:
    f.write("important\n")
    f.flush()                     # 立刻可被其他进程看到

# os.fsync()：强制操作系统把数据刷到磁盘（机器断电也能保留，代价大）
import os
with open("critical.txt", "w") as f:
    f.write("must survive power loss\n")
    f.flush()
    os.fsync(f.fileno())          # 工业级关键数据才用，非常慢
```

> **何时需要 flush**：写日志后希望 tail 立刻看到；写进度文件后希望崩溃恢复时能读到。
> **何时需要 fsync**：金融流水、数据库预写日志等"断电也不能丢"的数据。普通科研记录完全不需要。

### 5.5 光标定位：seek / tell

```python
# tell()：当前光标位置（字节数）
# seek(offset, whence)：移动光标
#   whence=0（默认）从文件头；1 相对当前位置；2 从文件尾

with open("data.bin", "rb") as f:
    f.seek(0, 2)              # 跳到文件末尾
    size = f.tell()           # 文件总字节数
    f.seek(0)                 # 回到开头
    first_byte = f.read(1)

# 覆盖写中间部分：r+ 模式
with open("data.txt", "r+", encoding="utf-8") as f:
    f.seek(5)                 # 跳到第 6 个字符处
    f.write("XX")             # 覆盖原内容
```

---

## 6. 文件与目录管理（os / shutil）

### 6.1 复制、移动、重命名

```python
import shutil
from pathlib import Path

src = Path("data.csv")
dst = Path("backup/data.csv")

# 复制文件
shutil.copy(src, dst)                    # 复制内容+权限，不保留元数据（最常用）
shutil.copy2(src, dst)                   # 额外保留修改时间等元数据
shutil.copytree("dir", "dir_backup")     # 递归复制整个目录树

# 移动 / 重命名（同一目录内即重命名）
shutil.move(src, "archive/old.csv")      # 跨目录移动
Path("a.csv").rename("b.csv")            # 简单重命名（也可移动）
```

### 6.2 删除

```python
from pathlib import Path
import os
import shutil

Path("tmp.txt").unlink()               # 删除单个文件；不存在抛 FileNotFoundError
Path("tmp.txt").unlink(missing_ok=True)  # Python 3.8+：不存在也不报错
Path("empty_dir").rmdir()              # 删除空目录；非空报错 OSError
shutil.rmtree("data_old")              # 递归删除整个目录树（慎用，不可恢复）
os.remove("tmp.txt")                   # 等同 unlink（os 风格）
```

> **危险警告**：`shutil.rmtree` 和 `'w'` 模式是**不可逆**操作。删除前务必确认路径正确，尤其在科研脚本中批量处理时，先用 `print()` 或 dry-run 验证。

### 6.3 遍历目录

```python
from pathlib import Path

d = Path("data")

# 列出当前目录内容
for p in d.iterdir():
    print(p.name, "是目录" if p.is_dir() else "是文件")

# glob：按模式递归查找（科研最常见）
for p in d.rglob("*.csv"):        # 递归找所有 csv
    print(p)

for p in d.glob("raw/*.json"):    # 非递归，一层内找 json
    print(p)

# os.walk：传统方式（返回 (dirpath, dirnames, filenames) 三元组）
import os
for root, dirs, files in os.walk("data"):
    for name in files:
        if name.endswith(".csv"):
            print(os.path.join(root, name))
```

### 6.4 文件元数据与统计信息

```python
from pathlib import Path
import os
import time

p = Path("data.csv")
st = p.stat()                     # 返回 os.stat_result

print(st.st_size)                 # 文件字节大小
print(st.st_mtime)                # 最后修改时间（时间戳）
print(st.st_ctime)                # 创建时间（Windows）
print(time.ctime(st.st_mtime))    # 人类可读时间

# 便捷方法
print(p.stat().st_size)           # 大小
```

### 6.5 权限与只读属性

```python
from pathlib import Path
import os

p = Path("f.txt")

# 设置/检查读写权限（Linux/macOS；Windows 上只对只读属性部分有效）
os.chmod("f.txt", 0o644)          # rw-r--r--
p.chmod(0o600)                    # 仅所有者可读写

# 检查可读写性
print(os.access("f.txt", os.R_OK))   # 可读？
print(os.access("f.txt", os.W_OK))   # 可写？
```

### 6.6 临时文件与临时目录

```python
import tempfile
from pathlib import Path

# 方式 1：上下文管理器，用完自动删除（工业推荐）
with tempfile.TemporaryDirectory() as tmpdir:
    p = Path(tmpdir) / "out.txt"
    p.write_text("data")
    # 块结束自动清理整个目录

# 方式 2：临时文件，自动删除
with tempfile.NamedTemporaryFile(delete=True) as tf:
    tf.write(b"data")
    tf.flush()
    print(tf.name)                # 在磁盘上可见的唯一临时路径

# 方式 3：持久化临时文件（不自动删除，用完手动删）
import tempfile
tmp = tempfile.mkstemp(suffix=".json")[1]
print(tmp)
```

---

## 7. 科研场景实战

> 科研代码的核心诉求：**数据可复现、批量可扩展、结果易汇总**。下面给出可直接套用的模式。

### 7.1 结构化数据：CSV 读写（文本模式的典型）

```python
import csv
from pathlib import Path

# ---- 写入 CSV ----
rows = [
    {"epoch": 1, "loss": 0.512, "acc": 0.83},
    {"epoch": 2, "loss": 0.331, "acc": 0.90},
]
with open("train_log.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["epoch", "loss", "acc"])
    writer.writeheader()
    writer.writerows(rows)

# ---- 读取 CSV ----
with open("train_log.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["epoch"], row["loss"], row["acc"])
```

> **为什么 `newline=""`**：csv 模块自己管理换行，若不传 `newline=""`，Windows 下会写出多余的 `\r\r\n`。这是 CSV 写入最常见的坑。

### 7.2 结构化数据：JSON 读写（配置/结果/元数据）

```python
import json
from pathlib import Path

# ---- 写 JSON ----
config = {"lr": 1e-3, "batch_size": 64, "arch": "resnet18"}
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
    # ensure_ascii=False：中文原样保存而非 \uXXXX
    # indent=2：人类可读格式化

# ---- 读 JSON ----
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# ---- 批量追加结果到同文件（换行分隔 JSON / JSONL）----
with open("results.jsonl", "a", encoding="utf-8") as f:
    for trial in trials:
        f.write(json.dumps(trial) + "\n")   # 每行一条，可增量追加
```

### 7.3 NumPy 科学数据

```python
import numpy as np
from pathlib import Path

arr = np.random.rand(1000, 3)

# 文本格式（可读、体积大、慢）
np.savetxt("arr.txt", arr, fmt="%.6f", delimiter=",")
loaded = np.loadtxt("arr.txt", delimiter=",")

# 二进制 npy（快、紧凑、保留 dtype）
np.save("arr.npy", arr)
loaded2 = np.load("arr.npy")

# 多数组打包 npz
np.savez("bundle.npz", x=arr, y=np.arange(10))
data = np.load("bundle.npz")
data["x"], data["y"]

# 字典直接写 JSON（小结果汇总）
Path("summary.json").write_text(
    json.dumps({"mean": float(arr.mean())}, indent=2), encoding="utf-8"
)
```

### 7.4 模型权重：PyTorch

```python
import torch

# 保存
torch.save(model.state_dict(), "model.pt")
torch.save({"epoch": 10, "state_dict": model.state_dict(),
            "optim": optimizer.state_dict()}, "checkpoint.pt")

# 加载（务必指定 map_location 以兼容 CPU/GPU 环境）
ckpt = torch.load("checkpoint.pt", map_location="cpu", weights_only=True)
print(ckpt["epoch"])

# 工业经验：训练中断后从 checkpoint 恢复、只保留 best 模型
Path("checkpoints").mkdir(parents=True, exist_ok=True)
```

### 7.5 大数据集流式处理（内存友好）

```python
# 一个 5 GB 的 CSV：不能用 pandas.read_csv 直接读（内存爆炸），
# 应逐块/逐行处理：
CHUNK = 10_000
with open("huge.csv", "r", encoding="utf-8") as f:
    header = f.readline()
    batch = []
    for line in f:
        batch.append(line.strip().split(","))
        if len(batch) >= CHUNK:
            process_batch(batch)      # 比如转成 numpy 数组喂给模型
            batch = []
    if batch:                          # 处理最后的残余
        process_batch(batch)
```

### 7.6 实验目录的规范化组织（科研可复现的骨架）

```python
from pathlib import Path
from datetime import datetime

def make_run_dir(root="experiments"):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run = Path(root) / stamp
    for sub in ("checkpoints", "logs", "results"):
        (run / sub).mkdir(parents=True, exist_ok=True)
    # 记录超参数，方便事后复现
    (run / "hparams.json").write_text(
        json.dumps(hparams, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return run

run_dir = make_run_dir()
```

---

## 8. 工业场景实战

> 工业代码的核心诉求：**健壮性、可观测性、并发安全、不留垃圾**。

### 8.1 日志：logging（不要 print）

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                  # 屏幕输出
        RotatingFileHandler("app.log",            # 滚动文件日志
                            maxBytes=5 * 1024 * 1024,
                            backupCount=3,        # 保留最近 3 个滚动文件
                            encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)
logger.info("服务启动")
logger.error("处理失败: %s", err)   # 不要用 f-string，用占位符延迟求值
```

### 8.2 配置文件：读取与写入

```python
import json, configparser
from pathlib import Path

# ---- JSON 配置（推荐，天然嵌套）----
with open("app.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

# ---- INI 配置 ----
conf = configparser.ConfigParser()
conf.read("app.ini", encoding="utf-8")
host = conf.get("database", "host", fallback="localhost")

# ---- 环境变量（敏感信息不要落盘）----
import os
API_KEY = os.environ.get("API_KEY")
```

### 8.3 原子写入（防止写一半的坏文件）

写文件可能中途崩溃，留下半截文件。**原子写** = 先写临时文件 + `os.replace`（同文件系统下原子）。

```python
import os, tempfile
from pathlib import Path

def atomic_write(path, text, encoding="utf-8"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # 在目标目录创建临时文件（保证同分区，replace 才原子）
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())          # 先保证数据落盘
        os.replace(tmp, path)             # 原子替换：要么旧文件，要么新文件
    except BaseException:
        os.unlink(tmp)                    # 出错清理临时文件
        raise

atomic_write("state.json", '{"done": true}')
```

### 8.4 并发安全：多进程写入与文件锁

多个进程同时写同一文件会互相覆盖。标准解法：**文件锁（fcntl，仅 Unix）**或**每进程写独立文件再合并**。

```python
# Unix/Linux 下用 fcntl 加锁（Windows 可用 msvcrt 或第三方 portalocker）
import fcntl

with open("shared.log", "a") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)   # 排他锁，阻塞等待
    f.write(line)
    f.flush()
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)   # 解锁
```

**工业更常用的替代方案**：
- 每进程写独立文件（`worker_1.jsonl`、`worker_2.jsonl`...），最后合并——无锁、天然并发。
- 用专门的队列/数据库（SQLite 自带上锁、Redis、Kafka）做并发写入。

### 8.5 大文件：内存映射（mmap）

只读访问几十 GB 文件而几乎不占内存：

```python
import mmap

with open("huge_index.bin", "rb") as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        # m 表现得像字节串，可切片、可 search，但按需从磁盘分页加载
        pos = m.find(b"needle")
        print(m[pos:pos + 20])
```

### 8.6 目录监控与批处理（Watcher 模式）

```python
import time, os
from pathlib import Path

inbox = Path("inbox")
inbox.mkdir(exist_ok=True)

seen = set()
while True:
    for p in inbox.glob("*.csv"):
        if p.name in seen:
            continue
        seen.add(p.name)
        process_csv(p)               # 处理新到文件
        p.unlink(missing_ok=True)    # 处理完即移走，避免重复处理
    time.sleep(1)
```

### 8.7 从文件读取结构化行数据（错误容忍）

```python
def load_lines_safe(path, encoding="utf-8"):
    """逐行读取，跳过坏行，返回 (好行列表, 坏行数)。"""
    good, bad = [], 0
    with open(path, "r", encoding=encoding, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                good.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    return good, bad
```

---

## 9. 最佳实践与常见陷阱

### 9.1 十大最佳实践

| # | 实践 | 理由 |
|---|------|------|
| 1 | 永远用 `with open(...)` | 自动关闭，防 fd 泄漏 |
| 2 | 永远显式 `encoding="utf-8"` | 跨平台无乱码，摆脱 gbk/locale 差异 |
| 3 | 用 `pathlib.Path` 而非字符串拼接路径 | 跨平台分隔符自动处理 |
| 4 | 写 CSV 时 `newline=""` | 避免 Windows `\r\r\n` 双换行 |
| 5 | 创建文件前 `mkdir(parents=True, exist_ok=True)` | 避免 FileNotFoundError |
| 6 | 大文件用迭代/分块读取，不 `read()` 全量 | 控内存 |
| 7 | 二进制文件（权重/图片）用 `rb/wb` | 防 UnicodeDecodeError |
| 8 | 覆盖写/删除前先 dry-run 打印 | 防不可逆误操作 |
| 9 | 写重要数据用临时文件 + `os.replace` | 防写一半的坏文件 |
| 10 | 日志用 `logging`，不 `print` | 分级、滚动、可观测 |

### 9.2 常见陷阱对照表

| 症状 | 根因 | 修复 |
|------|------|------|
| `UnicodeDecodeError` | 编码不一致（最常见：utf-8 写的用 gbk 读） | 统一显式 `encoding="utf-8"` |
| 中文乱码 | 读/写编码不一致 | 同上；JSON 加 `ensure_ascii=False` |
| `FileNotFoundError: No such file` | 目标目录不存在 | `mkdir(parents=True, exist_ok=True)` |
| `FileExistsError` | `'x'` 模式文件已存在 | `try/except` 或 `exist_ok=True` |
| `PermissionError` | 文件被占用/无权限 | 检查是否有进程占用；Windows 上被打开的 Excel 会锁文件 |
| `Too many open files` | 忘了 close / with | 检查循环内是否裸 open |
| CSV 出现空行 `\r\r\n` | 写 CSV 未传 `newline=""` | `open(..., newline="")` |
| 读到空文件/丢数据 | write 后立即读未 flush | 先 `f.flush()` 再读，或用 `with`（关闭时自动 flush） |
| Windows 路径分隔符问题 | 手写 `\` 转义错 | 用 `pathlib` 或原始字符串 `r"..."` |
| `IsADirectoryError` / `NotADirectoryError` | 把目录当文件打开 | 先 `is_dir()` / `is_file()` 判断 |
| `OSError: [Errno 28] No space left` | 磁盘满 | 捕获并清理/告警，别让进程崩溃 |

### 9.3 统一"读/写小文本文件"的工具函数

```python
from pathlib import Path
import json

def read_text(path, encoding="utf-8"):
    return Path(path).read_text(encoding=encoding)

def write_text(path, text, encoding="utf-8"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding=encoding)

def read_json(path, encoding="utf-8"):
    return json.loads(Path(path).read_text(encoding=encoding))

def write_json(path, obj, indent=2, encoding="utf-8"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(obj, ensure_ascii=False, indent=indent), encoding=encoding)
```

> `Path.read_text()` / `Path.write_text()` / `Path.read_bytes()` / `Path.write_bytes()`
> 是 Python 3.5+ 的内置便捷方法，一条语句完成打开→读写→关闭。**小文件日常首选**。

---

## 10. 速查表附录

### 10.1 打开模式速查

```
r  只读      w  覆盖写     a  追加写     x  独占创建
r+ 读写      w+ 覆盖读写   a+ 追加读写
+b 二进制    +t 文本（默认）
```

### 10.2 pathlib 常用方法速查

| 方法 | 作用 |
|------|------|
| `Path("a") / "b"` | 拼接路径 |
| `.name / .stem / .suffix / .parent` | 取文件名/主名/后缀/父目录 |
| `.exists() / .is_file() / .is_dir()` | 判断 |
| `.mkdir(parents=True, exist_ok=True)` | 建目录 |
| `.touch()` | 创建空文件/更新时间戳 |
| `.unlink(missing_ok=True)` | 删文件 |
| `.rename()` / `.replace()` | 改名/移动 |
| `.glob()` / `.rglob()` | 查找文件 |
| `.read_text() / .write_text()` | 便捷读写文本 |
| `.read_bytes() / .write_bytes()` | 便捷读写二进制 |
| `.stat().st_size` | 文件大小 |
| `.resolve()` / `.absolute()` | 规范化/绝对化 |

### 10.3 模块分工速查

| 模块 | 职责 | 何时用 |
|------|------|--------|
| `pathlib` | 路径对象 | **默认首选** |
| 内建 `open()` | 打开/读写文件 | 所有 I/O |
| `os` | 底层：chmod、walk、remove、rename | 系统级操作 |
| `shutil` | 复制/移动/删除目录树 | 文件批量管理 |
| `glob` | 文件名模式匹配 | 快速找文件 |
| `tempfile` | 临时文件/目录 | 原子写、暂存 |
| `json` / `csv` / `configparser` | 结构化格式 | 数据/配置 |
| `logging` | 日志 | 工业可观测性 |
| `mmap` | 内存映射 | 超大只读文件 |
| `fcntl`（Unix）/ `portalocker` | 文件锁 | 多进程互斥 |

### 10.4 编码速查

```
UTF-8（无 BOM）—— 现代通用标准，推荐
UTF-8 with BOM  —— Windows 记事本默认，pandas 读 CSV 常见 \ufeff 坑
GBK / GB2312    —— 中文 Windows 旧系统、某些中文数据集
latin-1         —— 万能兜底解码（永不报错），用于探测
```

---

## 练习建议（检验掌握程度）

1. 写一个函数 `save_experiment(metrics: dict, run_dir)`：创建带时间戳的目录、写 `metrics.json` 和 `log.csv`。
2. 写一个脚本：用 `rglob("*.pt")` 找到某目录下所有 checkpoint，输出文件名与大小（MB），按大小排序。
3. 写一个 `atomic_append(path, line)`：并发环境下安全地给共享日志追加一行。
4. 写一个流式处理器：不把整个文件载入内存，统计一个 10 GB 文本文件的行数和总字数。
5. 排查：为什么一个 utf-8 写的中文 CSV 在 Windows Excel 打开是乱码？（提示：加 BOM，`open(..., encoding="utf-8-sig")`）
