from setuptools import setup
import datetime

setup(
    name="cygwin_pack",
    version=datetime.datetime.now().strftime("%Y%m%d"),
    packages=["cygwin_pack"],
    package_data={
        "package": ["cygwin/*"],  # 包含 tools 目录下的所有 .exe
    },
    entry_points={
        "console_scripts": [
            "cygwin_pack=cygwin_pack.cli:main",  # ← 安装后可用 runmyexe 命令
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
    platforms=["Windows"]
)