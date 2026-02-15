from setuptools import setup
import datetime

setup(
    name="cygwinpack",
    version=datetime.datetime.now().strftime("%Y%m%d"),
    packages=["cygwinpack"],
    package_data={
        "package": ["cygwin/*"],  # 包含 tools 目录下的所有 .exe
    },
    install_requires=["pywin32"]
    entry_points={
        "console_scripts": [
            "cygwinpack=cygwinpack.cli:main",  # ← 安装后可用 runmyexe 命令
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
    platforms=["Windows"]

)

