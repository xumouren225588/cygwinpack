import subprocess
from importlib import resources
from pathlib import Path
import os
import win32com.client

def main():
    appdata=os.getenv("LOCALAPPDATA")
    # 获取 .exe 的完整路径（Python 3.10+）
    exe_path = resources.files("cygwinpack.cygwin").joinpath("cygwin.exe")

    # 转为普通 Path 对象（resources.files 返回的是 Traversable）
    exe_path = Path(exe_path)

    if not exe_path.is_file():
        raise FileNotFoundError(f"Executable not found: {exe_path}")

    work_dir = exe_path.parent

    print(f"Running {exe_path} in directory: {work_dir}")

    # 执行 .exe（阻塞，继承 stdout/stderr）
    subprocess.run([str(exe_path),
                    "--quiet-mode",
                    "--local-install",
                    "--local-package-dir",
                    work_dir,
                    "--root",
                    os.path.join(appdata,"cygwin"),
                    "--packages",
                    "git,make"], cwd=work_dir,check=True)
    # 获取当前用户的桌面路径
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

    # 快捷方式目标（例如一个 Python 脚本）
    target = os.path.join(appdata,"cygwin","Cygwin.bat")
    # 快捷方式保存路径
    shortcut_path = os.path.join(desktop, "Cygwin.lnk")

    # 创建快捷方式
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = target  # 可选：设置图标
    shortcut.save()

    print(f"快捷方式已创建：{shortcut_path}")

