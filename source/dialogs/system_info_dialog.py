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

import platform
import socket
import urllib.request

import cpuinfo
import psutil
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class SystemInfo:
    def get_system_info(self):
        return {
            "Operating System": self.get_os_info(),
            "Processor": self.get_cpu_info(),
            "Memory": self.get_memory_info(),
            "Storage": self.get_storage_info(),
            "Network": self.get_network_info(),
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
            "Platform": platform.platform(),
            "Architecture": platform.architecture()[0],
            "User": psutil.users()[0].name if psutil.users() else "Unknown",
        }

    def get_network_info(self):
        try:
            return {
                "Hostname": socket.gethostname(),
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
        try:
            with urllib.request.urlopen(
                "https://api64.ipify.org?format=text"
            ) as response:
                if response.status == 200:
                    response_data = response.read().decode("utf-8")
                    return response_data
                else:
                    return "Unable to retrieve public IP"
        except Exception as e:
            return f"Unable to retrieve public IP: {e}"


class SystemInfoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Information")
        self.setFixedSize(450, 400)
        self.system_info_manager = SystemInfo()
        self.layout = self.create_layout()
        self.setLayout(self.layout)

    def create_layout(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("<h1>System Information</h1>", self))
        layout.addWidget(
            QLabel(
                f"{QCoreApplication.applicationName()} has detected the following hardware and software in your system:",
                self,
            )
        )

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.create_info_widget())
        layout.addWidget(scroll_area)

        close_button = QPushButton("OK", self)
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        return layout

    def create_info_widget(self):
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        system_info = self.system_info_manager.get_system_info()

        categories = list(system_info.items())
        total_categories = len(categories)

        for index, (category, details) in enumerate(categories):
            self.add_category_info(
                scroll_layout, category, details, index < total_categories - 1
            )

        scroll_content.setLayout(scroll_layout)
        return scroll_content

    def add_category_info(self, layout, category, details, add_spacer):
        layout.addWidget(QLabel(f"<h2>{category}:</h2>", self))
        for key, value in details.items():
            layout.addWidget(QLabel(f"<b>{key}:</b> {value}", self))
        if add_spacer:
            layout.addWidget(QLabel("<hr>", self))
