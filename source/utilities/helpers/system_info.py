#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################

import random
import socket
import sys
import urllib.request

import core.constants as constants  # type: ignore
import cpuinfo
import psutil
from PySide6.QtCore import QCoreApplication, QSysInfo
from PySide6.QtGui import QOffscreenSurface, QOpenGLContext

GL_VENDOR = 0x1F00
GL_RENDERER = 0x1F01


class SystemInfo:
    def get_system_info(self, include_gpu=True):
        info = {
            "Operating System": self.get_os_info(),
            "Processor": self.get_cpu_info(),
            "Memory": self.get_memory_info(),
            "Storage": self.get_storage_info(),
            "Network": self.get_network_info(),
            QCoreApplication.applicationName(): self.get_ludo_info(),
        }

        if include_gpu:
            info["GPU"] = self.get_gpu_info()

        return info

    @staticmethod
    def get_ludo_info():
        return {
            "Version": QCoreApplication.applicationVersion(),
            "Maintainer": constants.MAINTAINER,
            "Source": constants.GITHUB_URL,
            "Official Ludo Build": (
                QCoreApplication.applicationName() == "Ludo"
                and constants.DEVELOPER == constants.MAINTAINER
            ),
            "Bundled": hasattr(sys, "_MEIPASS"),
            "Python Version": sys.version.split()[0],
        }

    @staticmethod
    def get_cpu_info():
        cpu = cpuinfo.get_cpu_info()
        return {
            "Vendor": cpu.get("vendor_id_raw", "Unknown"),
            "Brand": cpu.get("brand_raw", "Unknown"),
            "Speed": f"{psutil.cpu_freq().max:.2f} MHz",
            "Cores": psutil.cpu_count(logical=False),
            "Threads": psutil.cpu_count(logical=True),
        }

    @staticmethod
    def get_gpu_info():
        try:
            surface = QOffscreenSurface()
            surface.create()

            context = QOpenGLContext()
            context.create()
            context.makeCurrent(surface)

            functions = context.functions()
            vendor = functions.glGetString(GL_VENDOR)
            renderer = functions.glGetString(GL_RENDERER)

            context.doneCurrent()
            surface.destroy()

            return {
                "Brand": renderer if renderer else "Unknown",
                "Vendor": vendor if vendor else "Unknown",
            }
        except Exception as e:
            return {"Status": f"Failed to retrieve GPU info: {e}"}

    def get_memory_info(self):
        svmem = psutil.virtual_memory()
        return {
            "Total": self.get_size(svmem.total),
            "In Use": self.get_size(svmem.used),
            "Available": self.get_size(svmem.available),
        }

    def get_storage_info(self):
        partitions = psutil.disk_partitions()
        fixed_drives, removable_drives = 0, 0
        fixed_drive_sizes, removable_drive_sizes = [], []

        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                if "removable" in partition.opts.lower():
                    removable_drives += 1
                    removable_drive_sizes.append(partition_usage.total)
                else:
                    fixed_drives += 1
                    fixed_drive_sizes.append(partition_usage.total)
            except PermissionError:
                continue

        return {
            "Number of Fixed Drives": fixed_drives,
            "Fixed Drive Sizes": ", ".join(
                [self.get_size(size) for size in fixed_drive_sizes]
            ),
            "Number of Removable Drives": removable_drives,
            "Removable Drive Sizes": ", ".join(
                [self.get_size(size) for size in removable_drive_sizes]
            ),
        }

    @staticmethod
    def get_os_info():
        return {
            "Platform": QSysInfo.prettyProductName(),
            "Kernel": f"{QSysInfo.kernelType()} ({QSysInfo.kernelVersion()})",
            "Architecture": QSysInfo.currentCpuArchitecture(),
            "User": psutil.users()[0].name if psutil.users() else "Unknown",
        }

    def get_network_info(self):
        try:
            return {
                "Host Name": QSysInfo.machineHostName(),
                "Local IP Address": self.get_ip_address(),
                "Public IP Address": self.get_public_ip(),
            }
        except Exception:
            return {"Status": "Unable to retrieve network information"}

    @staticmethod
    def get_size(bytes, suffix="B"):
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
        return f"{bytes:.2f}Y{suffix}"

    @staticmethod
    def get_ip_address():
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "Unable to retrieve IP"

    @staticmethod
    def get_public_ip():
        urls = [
            "https://api64.ipify.org?format=text",
            "https://checkip.amazonaws.com",
            "https://ifconfig.me/ip",
        ]
        url = random.choice(urls)
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    response_data = response.read().decode("utf-8")
                    return response_data
                else:
                    return "Unable to retrieve public IP"
        except Exception as e:
            return f"Unable to retrieve public IP: {e}"
