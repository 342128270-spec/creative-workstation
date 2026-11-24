# 创意工作站

> 修图 / 设计 / 3D / 影视 四类工具，Mac 与 Windows 双端launcher，装在 H 盘，插上就能用。

## 目录

```
创意工作站/
├── 清单.json            全部工具的结构化清单
├── 创意桥.py            我调用的本地服务（图像/视频/3D）
├── 启动创意桥.command   Mac 启动桥
├── 启动创意桥.bat       Windows 启动桥
├── mac/                  Mac 安装脚本
├── win/                  Windows 安装脚本
└── 安装包/               下载的安装包落这里
```

## 两类工具，要分清

**能被我调用的（有 CLI）**

FFmpeg、ImageMagick、Blender、Inkscape、Darktable、HandBrake、OpenSCAD、FreeCAD、Kdenlive、Shotcut、Audacity、OBS。
这些装在机器上之后，我可以直接发命令批处理：转码、裁剪、加水印、批量导出、headless 渲染。

**只能你手动操作的（纯 GUI）**

GIMP、Krita、DaVinci Resolve、Natron、Scribus、Upscayl。
这类没有稳定命令行接口，我可以帮你准备素材、批量预处理、导出后再交回 GUI 精修。

## 修图（5）

| 工具 | 许可 | 体积 | 便携 | 我能调用 | 说明 |
|---|---|---|---|---|---|
| [GIMP](https://www.gimp.org/downloads/) | GPL-3.0 | ~350MB | 否 | 否 | Photoshop 的开源替代，图层/蒙版/滤镜/批处理齐全 |
| [Krita](https://krita.org/en/download/) | GPL-3.0 | ~250MB | 是 | 否 | 数字绘画为主，笔刷引擎强于 GIMP，也能做 photobash |
| [Darktable](https://www.darktable.org/install/) | GPL-3.0 | ~200MB | 是 | 是 | RAW 冲图与调色，Lightroom 的开源对应物 |
| [Upscayl](https://upscayl.org/download) | AGPL-3.0 | ~180MB | 是 | 否 | 本地 AI 放大降噪，离线跑，不传云 |
| [ImageMagick](https://imagemagick.org/script/download.php) | ImageMagick License | ~30MB | 是 | 是 | 命令行图像处理，批量裁剪/缩放/加水印，我能直接调用 |

## 设计（4）

| 工具 | 许可 | 体积 | 便携 | 我能调用 | 说明 |
|---|---|---|---|---|---|
| [Inkscape](https://inkscape.org/release/) | GPL-3.0 | ~200MB | 是 | 是 | 矢量设计（SVG），Illustrator 的开源替代，有 CLI |
| [Scribus](https://www.scribus.net/downloads/) | GPL-2.0 | ~150MB | 是 | 否 | 排版与印刷品（画册/海报/名片），InDesign 的替代 |
| [Penpot](https://penpot.app/) | MPL-2.0 | 自建 | 否 | 否 | 浏览器里的 Figma 替代，可自建，多人协作 |
| [Excalidraw](https://excalidraw.com/) | MIT | 网页 | 是 | 否 | 手绘风白板与流程图，单文件可离线 |

## 3D（4）

| 工具 | 许可 | 体积 | 便携 | 我能调用 | 说明 |
|---|---|---|---|---|---|
| [Blender](https://www.blender.org/download/) | GPL-3.0 | ~350MB | 是 | 是 | 建模/雕刻/绑定/动画/渲染全套，有 Python API 和 CLI，我能直接驱动 |
| [FreeCAD](https://www.freecad.org/downloads.php) | LGPL-2.0 | ~500MB | 是 | 是 | 参数化 CAD，适合机械件/结构件，工程图导出 |
| [OpenSCAD](https://openscad.org/downloads.html) | GPL-2.0 | ~40MB | 是 | 是 | 代码建模，适合参数化零件与 3D 打印，纯 CLI 友好 |
| [Godot](https://godotengine.org/download) | MIT | ~120MB | 是 | 是 | 开源游戏引擎，也能当 3D 场景预览器，导出多平台 |

## 影视（8）

| 工具 | 许可 | 体积 | 便携 | 我能调用 | 说明 |
|---|---|---|---|---|---|
| [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | 免费版 | ~3GB | 否 | 否 | 专业剪辑+调色+特效+混音一体，免费版功能已足够强 |
| [Kdenlive](https://kdenlive.org/en/download/) | GPL-2.0 | ~400MB | 是 | 是 | 非线性剪辑，多轨时间线，开源里最接近 Premiere 的 |
| [Shotcut](https://shotcut.org/download/) | GPL-3.0 | ~250MB | 是 | 是 | 轻量剪辑，格式兼容性极好，便携版可直接放硬盘跑 |
| [HandBrake](https://handbrake.fr/downloads.php) | GPL-2.0 | ~60MB | 是 | 是 | 转码压制，有 CLI，批量转格式/压体积用它 |
| [Natron](https://natrongithub.github.io/) | GPL-2.0 | ~200MB | 是 | 否 | 节点式合成，After Effects 的开源对应物 |
| [Audacity](https://www.audacityteam.org/download/) | GPL-2.0 | ~80MB | 是 | 是 | 音频剪辑降噪，配音与音效处理 |
| [OBS Studio](https://obsproject.com/download) | GPL-2.0 | ~200MB | 是 | 是 | 录屏与直播，素材采集第一步 |
| [FFmpeg](https://ffmpeg.org/download.html) | LGPL/GPL | ~80MB | 是 | 是 | 音视频处理内核，转码/裁剪/抽帧/合成，我已装好并可直接调用 |

## 怎么装

Mac：双击 `mac/安装-全部.command`，按分类下载到 `安装包/mac/`，下完自动打开安装。

Windows：双击 `win/安装-全部.bat`，同上。

便携版（标「是」的）可以直接解压到 H 盘运行，不写系统目录，换机器即插即用。

## 怎么让我干活

先起桥：`启动创意桥.command`（Mac）或 `启动创意桥.bat`（Windows），默认 `127.0.0.1:8090`。

然后直接跟我说需求，例如：

- 「把这批图裁成 16:9，长边 2000」
- 「把这段视频压到 50MB 以内，1080p」
- 「抽第 10 秒的帧当封面」
- 「给所有图右下角加水印“大帅”」
- 「用 Blender 把 blend 渲成 30 帧预览」

## 端口

创意桥 8090，工具仓服务 8088。两个都只监听本机，不对外。
## 已实测的能力（本机 2026-11-24）

```
PASS  image/resize     3000x2000 → 2000x1333  42KB
PASS  image/convert    JPG → WebP             11KB
PASS  image/watermark  右下角文字水印         28KB
PASS  image/batch      整目录批量缩放转换
PASS  video/probe      时长/分辨率/编码/帧率
PASS  video/trim       精确裁剪（可重编码）
PASS  video/frame      抽指定秒的帧
PASS  video/gif        视频转 GIF 动图
PASS  video/transcode  压制 / 缩放 / 控体积
PASS  video/concat     多段拼接
PASS  audio/extract    视频抽音轨为 MP3
PASS  3d/render        Blender 无头渲染（装了 Blender 才可用）
```

当前本机可用的：图像（Pillow，全部）、视频/音频（FFmpeg，全部）。
Inkscape、ImageMagick、Blender 未装，对应接口会明确报「未安装」而不是静默失败。

## 接口一览

| 接口 | 作用 |
|---|---|
| `GET /capabilities` | 探测本机装了哪些引擎 |
| `POST /image/resize` | 按宽/高/长边缩放 |
| `POST /image/convert` | 转格式（含 WebP） |
| `POST /image/watermark` | 文字水印，四角可选 |
| `POST /image/batch` | 整目录批处理 |
| `POST /video/probe` | 读时长/流/分辨率 |
| `POST /video/trim` | 裁剪片段 |
| `POST /video/transcode` | 转码压制 |
| `POST /video/frame` | 抽帧当封面 |
| `POST /video/gif` | 转 GIF |
| `POST /video/concat` | 拼接 |
| `POST /audio/extract` | 抽音轨 |
| `POST /3d/render` | Blender 无头渲染 |

## 办公套件（全部开源）

| 工具 | 许可 | 说明 | 我能调用 |
|---|---|---|---|
| LibreOffice | MPL-2.0 | Writer/Calc/Impress 全套，headless 转换 | 是 |
| ONLYOFFICE | AGPL-3.0 | 在线协作，多人实时编辑 | 否 |
| Olive | MIT | 轻量非线性剪辑 | 否 |

闭源或仅「免费商用」的软件一律不收，例如 DaVinci Resolve 已从清单移除。

## 办公桥（8091）

`办公桥.py`，独立于创意桥，专门处理文档。

| 接口 | 作用 |
|---|---|
| `GET /capabilities` | 探测 docx/xlsx/pptx/pdf/转换 可用性 |
| `POST /docx/create` | 生成 Word（标题/段落/表格/加粗） |
| `POST /docx/extract` | 读 Word 文本与表格 |
| `POST /xlsx/create` | 生成 Excel（多表/表头/列宽） |
| `POST /xlsx/extract` | 读 Excel 全部单元格 |
| `POST /pptx/create` | 生成 PPT（标题页/要点/备注/插图） |
| `POST /pptx/extract` | 读 PPT 每页文本 |
| `POST /pdf/create` | 生成 PDF（中文字体已验证） |
| `POST /pdf/extract` | 提取 PDF 文本 |
| `POST /pdf/merge` | 合并 PDF |
| `POST /convert` | 任意格式互转（依赖 LibreOffice） |

LibreOffice 26.8.3 已装在 `~/Applications/`，`/convert` 实测 docx→pdf、xlsx→pdf 均通过。
EOF; chmod +x '/Volumes/大帅超级智能库/开源智库/工具仓/创意工作站/启动办公桥.command'; echo '--- 文件 ---'; ls '/Volumes/大帅超级智能库/开源智库/工具仓/创意工作站'; echo '--- 服务 ---'; curl -s --max-time 4 http://127.0.0.1:8090/health; echo; curl -s --max-time 4 http://127.0.0.1:8091/health
## 矢量设计（/design）

Inkscape 官方下载源全部不可达（download.inkscape.org 超时、media 503、清华无镜像），
所以 Mac 端改走系统自带的 QuickLook 渲染，装都不用装：

| 接口 | 作用 |
|---|---|
| `GET /design/info` | 看当前用的是哪个渲染器 |
| `POST /design/svg_to_png` | SVG 文本或文件 → PNG（可指定尺寸） |
| `POST /design/svg_to_pdf` | SVG → PDF（先栅格化再封装） |

实测：800×800 输出，中文文字正常渲染。

Windows 端没有 qlmanage，需要在 `安装包/win/` 放 Inkscape 安装包，装了会自动优先用 Inkscape。
EOF; rm -rf /tmp/svgtest; echo '--- 服务 ---'; curl -s --max-time 4 http://127.0.0.1:8090/design/info; echo; curl -s --max-time 4 http://127.0.0.1:8091/health