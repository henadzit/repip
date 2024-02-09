import argparse
import os
import json
import subprocess
import sys
import tempfile
from typing import List, Tuple

from .utils import repipe_print


parser = argparse.ArgumentParser()

commands_parser = parser.add_subparsers(dest="cmd")
install_parser = commands_parser.add_parser("install")
install_parser.add_argument("-r", help="Path to requirements.txt file", required=True)
install_parser.add_argument("package", nargs="*", help="Package to install")


def main():
    args = parser.parse_args()
    if args.command == "install":
        # pip installs packages before installing requirements
        if args.package:
            update_requirements(args.r, args.package)
            install_requirements_and_update_lock(args.r, rewrite_lock=True)
        else:
            install_requirements_and_update_lock(args.r)


def install_requirements_and_update_lock(
    requirements_path: str, rewrite_lock: bool = False
):
    # TODO: check for .lock in the file name

    if not os.path.exists(requirements_path):
        raise ValueError(f"Path {requirements_path} does not exist")

    lock_file_path = f"{requirements_path}.lock"
    if not rewrite_lock and os.path.exists(lock_file_path):
        repipe_print("Installing from lock file")

        _install_requirements_file(lock_file_path)
    else:
        repipe_print("Installing from requirements file")

        packages_in_requirements = set(
            [p for p, _ in _resolve_requirements_file(requirements_path)]
        )
        _install_requirements_file(requirements_path)

        # filter out packages that might have been installed by the user but
        # are not in the requirements file
        repipe_print("Updating lock file")
        with open(lock_file_path, "w") as lock_file:
            for pkg, version in _installed_pkgs_with_versions():
                if pkg in packages_in_requirements:
                    lock_file.write("==".join((pkg, version)) + "\n")


def update_requirements(requirements_path: str, package_args: List[str]):
    with tempfile.NamedTemporaryFile("w+") as install_report:
        # use pip to resolve the package versions
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--no-deps",
                "--dry-run",
                "--ignore-installed",
                "--report",
                install_report.name,
                *package_args,
            ],
            stderr=subprocess.STDOUT,
        )
        requested_pkgs_with_versions = [
            (p["metadata"]["name"], p["metadata"]["version"])
            for p in json.load(install_report)["install"]
        ]
        requested_pkgs = set(p[0] for p in requested_pkgs_with_versions)

    pkgs_in_requirements = _resolve_requirements_file(
        requirements_path, include_dependencies=False
    )

    with open(requirements_path, "w") as requirements_file:
        for requirements_pkg, requirements_pkg_version in pkgs_in_requirements:
            if requirements_pkg in requested_pkgs:
                # update the version of the package to the one requested
                pkg_to_write, ver_to_write = next(
                    (p, v)
                    for p, v in requested_pkgs_with_versions
                    if p == requirements_pkg
                )
                requested_pkgs.remove(requirements_pkg)
                repipe_print(
                    f"Changing {requirements_pkg} from {requirements_pkg_version} to {ver_to_write}"
                )
            else:
                pkg_to_write, ver_to_write = requirements_pkg, requirements_pkg_version

            requirements_file.write(f"{pkg_to_write}=={ver_to_write}\n")

        # write the new packages at the end of the requirements file
        for pkg, ver in requested_pkgs_with_versions:
            if pkg in requested_pkgs:
                requirements_file.write(f"{pkg}=={ver}\n")
                repipe_print(f"Adding {pkg}=={ver}")


def _install_requirements_file(requirements_file_path: str):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file_path]
    )


def _resolve_requirements_file(
    requirements_path: str, include_dependencies: bool = True
) -> List[Tuple[str, str]]:
    with tempfile.NamedTemporaryFile("w+") as install_report:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                requirements_path,
                "--quiet",
                "--dry-run",
                "--ignore-installed",
                "--report",
                install_report.name,
            ]
            + (["--no-deps"] if not include_dependencies else []),
            stderr=subprocess.STDOUT,
        )
        install_report.seek(0)
        report = json.load(install_report)
        return [
            (p["metadata"]["name"], p["metadata"]["version"]) for p in report["install"]
        ]


def _installed_pkgs_with_versions() -> List[Tuple[str, str]]:
    with tempfile.NamedTemporaryFile("w+") as freeze_output:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "freeze"], stdout=freeze_output
        )
        freeze_output.seek(0)
        # TODO: handle:
        # pystache @ git+https://github.com/PennyDreadfulMTG/pystache.git@256bc103fe99b4d387f4c4b049581d9474a871c4
        return [
            pv
            for pv in (p.split("==") for p in freeze_output.read().splitlines())
            if len(pv) == 2
        ]
