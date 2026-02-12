import subprocess
from importlib import resources
from pathlib import Path
import os
import win32com.client

def run_scripts_in_order(script_dir):
    # 将路径转换为 Path 对象（更现代、易读）
    script_path = Path(script_dir)

    # 确保目录存在
    if not script_path.is_dir():
        return

    # 获取所有 .bat 和 .cmd 文件，并按名称排序
    script_files = sorted(script_path.glob("*.bat")) + sorted(script_path.glob("*.cmd"))
    script_files.sort(key=lambda p: p.name)  # 再次整体按名称排序（合并后）

    # 依次执行脚本
    for script in script_files:
        print(f"正在执行: {script}")
        try:
            # 使用 subprocess.run 执行脚本，等待其完成
            subprocess.run(
                ["cmd", "/c", str(script)],  # Windows 下用 cmd /c 执行
                cwd=script.parent,           # 设置工作目录为脚本所在目录
                check=True,                  # 如果脚本返回非零退出码则抛出异常
                capture_output=True,         # 可选：捕获输出（stdout/stderr）
                text=True                    # 以文本形式返回输出
            )
            print(f"成功执行: {script.name}")
            # 如果需要打印脚本输出，可以取消下面注释：
            # print("输出:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"执行失败: {script.name}")
            print("错误输出:\n", e.stderr)
            # 可选择是否继续执行后续脚本，或直接中断
            # raise  # 如果希望一出错就停止，取消此行注释


def main():
    appdata=os.getenv("LOCALAPPDATA")
    # 获取 .exe 的完整路径（Python 3.10+）
    exe_path = resources.files("cygwinpack.cygwin").joinpath("cygwin.exe")
    postinst = resources.files("cygwinpack.postinstall")
    # 转为普通 Path 对象（resources.files 返回的是 Traversable）
    exe_path = Path(exe_path)
    postinst = Path(postinst)
    
    if not exe_path.is_file():
        raise FileNotFoundError(f"Executable not found: {exe_path}")

    work_dir = exe_path.parent

    print(f"Running {exe_path} in directory: {work_dir}")

    # 执行 .exe（阻塞，继承 stdout/stderr）
    subprocess.run([
                    "cmd", "/c", "start", "/wait",
                    str(exe_path),
                    "--quiet-mode",
                    "--local-install",
                    "--local-package-dir",
                    str(work_dir),
                    "--root",
                    os.path.join(appdata, "cygwin"),
                    "--packages",
                    "git,make"
                    ], cwd=work_dir, check=True)
      
    run_scripts_in_order(postinst)
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

