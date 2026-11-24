@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
set "ROOT=%~dp0.."
if not exist "%ROOT%\安装包\win" mkdir "%ROOT%\安装包\win"
explorer "%ROOT%\安装包\win"

echo 将依次打开 17 个官方下载页，每个页面选 Windows 版本。
echo 安装包会存进「下载」文件夹，请移动到 安装包\win\
echo.

for %%U in (
  "https://www.gimp.org/downloads/"
  "https://krita.org/en/download/"
  "https://www.darktable.org/install/"
  "https://upscayl.org/download"
  "https://inkscape.org/release/"
  "https://www.scribus.net/downloads/"
  "https://www.blender.org/download/"
  "https://www.freecad.org/downloads.php"
  "https://openscad.org/downloads.html"
  "https://godotengine.org/download"
  "https://kdenlive.org/en/download/"
  "https://shotcut.org/download/"
  "https://handbrake.fr/downloads.php"
  "https://natrongithub.github.io/"
  "https://www.audacityteam.org/download/"
  "https://obsproject.com/download"
  "https://www.blackmagicdesign.com/products/davinciresolve"
) do (
  start "" %%U
  timeout /t 2 >nul
)

echo.
echo 全部页面已打开。装完后双击「启动创意桥.bat」。
pause