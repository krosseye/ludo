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

import csv
import json
import socket
import urllib.request
from datetime import datetime

import cpuinfo
import psutil
from PySide6.QtCore import QCoreApplication, QObject, QSysInfo, QThread, Signal
from PySide6.QtGui import QOffscreenSurface, QOpenGLContext
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

GL_VENDOR = 0x1F00
GL_RENDERER = 0x1F01


class InfoWorker(QObject):
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.system_info = SystemInfo()

    def run(self):
        info = self.system_info.get_system_info(include_gpu=False)
        self.finished.emit(info)


class SystemInfo:
    def get_system_info(self, include_gpu=True):
        info = {
            "Operating System": self.get_os_info(),
            "Processor": self.get_cpu_info(),
            "Memory": self.get_memory_info(),
            "Storage": self.get_storage_info(),
            "Network": self.get_network_info(),
        }

        if include_gpu:
            info["GPU"] = self.get_gpu_info()

        return info

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
                "Vendor": vendor if vendor else "Unknown",
                "Brand": renderer if renderer else "Unknown",
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
        try:
            with urllib.request.urlopen(urls[0]) as response:
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
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.is_info_loading = False
        self.system_info = None

        self.layout.addWidget(QLabel("<h1>System Information</h1>", self))
        self.label = QLabel(
            f"{QCoreApplication.applicationName()} is gathering system info..."
        )
        self.layout.addWidget(self.label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.export_button = QPushButton("Export...", self)
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.show_export_options)

        self.close_button = QPushButton("OK", self)
        self.close_button.setEnabled(False)
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

        self.load_system_info_async()

    def show_export_options(self):
        if not self.system_info:
            return

        menu = QMenu(self)

        json_action = menu.addAction("Export as JSON")
        json_action.triggered.connect(lambda: self.export_data("json"))

        csv_action = menu.addAction("Export as CSV")
        csv_action.triggered.connect(lambda: self.export_data("csv"))

        txt_action = menu.addAction("Export as Text")
        txt_action.triggered.connect(lambda: self.export_data("txt"))

        menu.exec_(
            self.export_button.mapToGlobal(self.export_button.rect().bottomLeft())
        )

    def export_data(self, format_type):
        if not self.system_info:
            return

        default_name = f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        file_filter = ""
        if format_type == "json":
            file_filter = "JSON Files (*.json)"
        elif format_type == "csv":
            file_filter = "CSV Files (*.csv)"
        else:  # txt
            file_filter = "Text Files (*.txt)"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export System Information",
            f"{default_name}.{format_type}",
            file_filter,
        )

        if not file_path:
            return  # User cancelled

        try:
            if format_type == "json":
                self.export_to_json(file_path)
            elif format_type == "csv":
                self.export_to_csv(file_path)
            else:  # txt
                self.export_to_text(file_path)

            QMessageBox.information(
                self,
                "Export Successful",
                f"System information exported successfully to:\n{file_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export system information:\n{str(e)}"
            )

    def export_to_json(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.system_info, f, indent=4)

    def export_to_csv(self, file_path):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(["Category", "Property", "Value"])

            for category, properties in self.system_info.items():
                for prop, value in properties.items():
                    if isinstance(value, dict):
                        for sub_prop, sub_value in value.items():
                            writer.writerow([category, f"{prop}.{sub_prop}", sub_value])
                    else:
                        writer.writerow([category, prop, value])

    def export_to_text(self, file_path):
        with open(file_path, "w") as f:
            for category, properties in self.system_info.items():
                f.write(f"=== {category} ===\n")
                for prop, value in properties.items():
                    if isinstance(value, dict):
                        for sub_prop, sub_value in value.items():
                            f.write(f"{prop}.{sub_prop}: {sub_value}\n")
                    else:
                        f.write(f"{prop}: {value}\n")
                f.write("\n")

    def load_system_info_async(self):
        self.is_info_loading = True
        self.thread = QThread()
        self.worker = InfoWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_info_loaded)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_info_loaded(self, system_info):
        gpu_info = SystemInfo.get_gpu_info()  # Fetch GPU info safely in main thread
        system_info["GPU"] = gpu_info
        self.system_info = dict(sorted(system_info.items(), key=lambda x: x[0].lower()))

        info_widget = self.create_info_widget(self.system_info)
        self.scroll_area.setWidget(info_widget)

        self.label.setText(
            f"{QCoreApplication.applicationName()} has detected the following hardware and software in your system:"
        )
        self.close_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.is_info_loading = False

    def create_info_widget(self, system_info):
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        categories = system_info.items()

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
