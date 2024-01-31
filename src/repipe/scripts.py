import argparse
import os
import json
import subprocess
import sys
import tempfile
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

        _install_requirements(lock_file_path)
    else:
        print("Installing from requirements file")

        packages_in_requirements = _resolve_requirements_file(requirements_path)
        _install_requirements(requirements_path)
        freeze_output = _freeze()
        filtered_freeze_lines = []

        # filter out packages that might have been installed by the user but
        # are not in the requirements file
        for line in freeze_output.splitlines():
            cleaned_line = line.strip()
            if cleaned_line.startswith("#") or not cleaned_line:
                continue

            if cleaned_line.split("==")[0] not in packages_in_requirements:
                continue

            filtered_freeze_lines.append(cleaned_line)

        with open(lock_file_path, "w") as lock_file:
            lock_file.write("\n".join(filtered_freeze_lines))


def _install_requirements(requirements_file_path: str):
    subprocess.call(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file_path]
    )


def _resolve_requirements_file(requirements_path: str) -> List[str]:
    with tempfile.NamedTemporaryFile("w+") as install_report:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                requirements_path,
                "--dry-run",
                "--ignore-installed",
                "--report",
                install_report.name,
            ],
            stderr=subprocess.STDOUT,
        )
        install_report.seek(0)
        report = json.load(install_report)
        return [p["metadata"]["name"] for p in report["install"]]


def _freeze() -> str:
    with tempfile.NamedTemporaryFile("w+") as freeze_output:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "freeze"], stdout=freeze_output
        )
        freeze_output.seek(0)
        return freeze_output.read()
