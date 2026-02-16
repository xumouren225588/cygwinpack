import os
import hashlib
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import requests
from pathlib import Path
import subprocess
import zipfile


# 配置
GITHUB_API_LATEST = "https://api.github.com/repos/xumouren225588/cygwinpack/releases/latest"
LOCAL_APPDATA = Path(os.getenv("LOCALAPPDATA"))
INSTALL_DIR = LOCAL_APPDATA / "cygwin-updater"
CURRENT_VERSION_FILE = INSTALL_DIR / "current_version.txt"

def ensure_dirs():
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

def get_local_version():
    return CURRENT_VERSION_FILE.read_text().strip() if CURRENT_VERSION_FILE.exists() else None

def sha256sum(filepath):
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# 全局变量用于传递进度（线程安全可通过 queue，但简单场景用 callback）
def update_progress(progress_var, value):
    progress_var.set(value)
    # 强制刷新 GUI（在主线程中调用）
    try:
        progress_var._root.update_idletasks()
    except:
        pass

def download_file_with_progress(url, save_path, progress_var, root):
    headers = {"Accept": "application/octet-stream"}
    resp = requests.get(url, headers=headers, stream=True)
    resp.raise_for_status()

    total_size = int(resp.headers.get('content-length', 0))
    downloaded = 0
    chunk_size = 8192

    with open(save_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    update_progress(progress_var, percent)
                    # 可选：更新状态文本
                    # root.after(0, lambda: status_label.config(text=f"已下载 {downloaded//1024//1024} MB"))

def extract_7z_with_progress(archive_path, target_dir, progress_var, root):
    # 第一步：读取 ZIP metadata（文件列表和大小）
    with zipfile.ZipFile(archive_path, mode='r') as z:
        file_infos = [info for info in z.infolist() if not info.is_dir()]
        total_unpacked = sum(info.file_size for info in file_infos)

    if total_unpacked == 0:
        total_unpacked = 1  # 避免除零

    unpacked_bytes = 0

    # 逐个解压文件并更新进度
    with zipfile.ZipFile(archive_path, mode='r') as z:
        for info in file_infos:
            # 提取单个文件
            z.extract(info, path=target_dir)
            unpacked_bytes += info.file_size
            percent = (unpacked_bytes / total_unpacked) * 100
            update_progress(progress_var, percent)

def update_app(root, progress_var, status_label):

    status_label.config(text="正在获取最新 Release...")
    root.update_idletasks()

    resp = requests.get(GITHUB_API_LATEST)
    resp.raise_for_status()
    release = resp.json()

    tag_name = release["tag_name"]
    assets = release["assets"]

    sevenz_asset = None
    for asset in assets:
        if asset["name"].endswith(".zip"):
            sevenz_asset = asset
            break

    if not sevenz_asset:
        raise ValueError("未找到 .7z 发布文件")

    remote_version = tag_name
    local_version = get_local_version()
    if local_version == remote_version:
        status_label.config(text=f"已是最新版本：{remote_version}")
        messagebox.showinfo("提示", "当前已是最新版本！")
        progress_var.set(0)
        return

    digest = sevenz_asset["digest"]
    if not digest.startswith("sha256:"):
        raise ValueError("仅支持 sha256 校验")
    expected_sha256 = digest.split(":", 1)[1].lower()

    download_url = "https://gh.927223.xyz/"+sevenz_asset["browser_download_url"]
    filename = sevenz_asset["name"]
    archive_path = INSTALL_DIR / filename

    # === 下载阶段 ===
    status_label.config(text="正在下载更新包...")
    download_file_with_progress(download_url, archive_path, progress_var, root)

    # === 校验阶段 ===
    status_label.config(text="正在校验...")
    actual_sha256 = sha256sum(archive_path)
    if actual_sha256 != expected_sha256:
        archive_path.unlink(missing_ok=True)
        raise ValueError("校验失败！")

    # === 解压阶段 ===
    status_label.config(text="正在解压文件...")
    progress_var.set(0)  # 重置进度条用于解压
    extract_7z_with_progress(archive_path, INSTALL_DIR, progress_var, root)
    status_label.config(text="正在安装...")
    subprocess.run([os.path.join(INSTALL_DIR,"install.exe")],check=True,cwd=INSTALL_DIR)
    
    # === 完成 ===
    CURRENT_VERSION_FILE.write_text(remote_version, encoding='utf-8')
    archive_path.unlink(missing_ok=True)

    status_label.config(text=f"更新成功！版本：{remote_version}")
    messagebox.showinfo("成功", f"Cygwin 已更新至 {remote_version}！")
    progress_var.set(100)

    

def start_update(root, progress_var, status_label):
    thread = threading.Thread(
        target=update_app,
        args=(root, progress_var, status_label),
        daemon=True
    )
    thread.start()

def create_gui():
    root = tk.Tk()
    root.title("Cygwin Updater")
    root.geometry("480x220")

    status_label = tk.Label(root, text="正在检查更新...", fg="blue", font=("Consolas", 9))
    status_label.pack(pady=10)

    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=30, pady=5)

    # 创建后立即自动开始更新
    root.after(100, lambda: start_update(root, progress_var, status_label))

    root.mainloop()

if __name__ == "__main__":
    ensure_dirs()

    create_gui()



