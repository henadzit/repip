import argparse
import os
import subprocess
import sys
from typing import List


parser = argparse.ArgumentParser()
parser.add_argument("command", choices=["install"])
parser.add_argument("-r", help="Path to requirements.txt file")


def main():
    args = parser.parse_args()
    if args.command == "install":
        _install(args.r)


def _install(requirements_path: str):
    if not os.path.exists(requirements_path):
        raise ValueError(f"Path {requirements_path} does not exist")

    lock_file_path = f"{requirements_path}.lock"
    if os.path.exists(lock_file_path):
        print("Installing from lock file")
        subprocess.call([sys.executable, "-m", "pip", "install", "-r", lock_file_path])
    else:
        print("Installing from requirements file")
        subprocess.call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path]
        )
        with open(lock_file_path, "w") as lock_file:
            subprocess.call([sys.executable, "-m", "pip", "freeze"], stdout=lock_file)


# def _get_packages(requirements_path: str) -> List[str]:
#     packages = []
#     with open(requirements_path) as f:
#         for line in f.read().splitlines():
#             cleaned_line = line.strip()
#             if cleaned_line.startswith("#") or not cleaned_line:
#                 continue

#             packages.append(cleaned_line)

#     return packages
