#!/bin/bash
# 按分类逐个打开下载页，把对应安装包存进 安装包/mac/
cd "$(dirname "$0")" || exit 1
ROOT="$(cd .. && pwd)"
mkdir -p "$ROOT/安装包/mac"
open "$ROOT/安装包/mac"

urls=(
  "https://www.gimp.org/downloads/|GIMP 修图"
  "https://krita.org/en/download/|Krita 绘画"
  "https://www.darktable.org/install/|Darktable 冲图"
  "https://upscayl.org/download|Upscayl AI放大"
  "https://inkscape.org/release/|Inkscape 矢量"
  "https://www.scribus.net/downloads/|Scribus 排版"
  "https://www.blender.org/download/|Blender 3D"
  "https://www.freecad.org/downloads.php|FreeCAD"
  "https://openscad.org/downloads.html|OpenSCAD"
  "https://godotengine.org/download|Godot"
  "https://kdenlive.org/en/download/|Kdenlive 剪辑"
  "https://shotcut.org/download/|Shotcut 剪辑"
  "https://handbrake.fr/downloads.php|HandBrake 转码"
  "https://natrongithub.github.io/|Natron 合成"
  "https://www.audacityteam.org/download/|Audacity 音频"
  "https://obsproject.com/download|OBS 录屏"
  "https://www.blackmagicdesign.com/products/davinciresolve|DaVinci Resolve"
)

echo "将依次打开 ${#urls[@]} 个官方下载页。"
echo "每个页面选 macOS 版本，安装包会存进「下载」文件夹，请移动到 安装包/mac/。"
echo
for item in "${urls[@]}"; do
  url="${item%%|*}"; name="${item##*|}"
  echo "→ $name"
  open "$url"
  sleep 2
done
echo
echo "全部页面已打开。装完后回来双击「启动创意桥.command」。"
read -n 1 -s -r -p "按任意键退出"