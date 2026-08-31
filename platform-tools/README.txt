# ADB App Uninstaller Pro

A lightweight, multi-threaded desktop GUI tool built in Python and Tkinter to manage, filter, and uninstall Android applications (both 3rd-party user apps and system bloatware) via ADB (Android Debug Bridge).

---

## Features

* **Multi-Threaded Performance**: Executes ADB tasks in background threads to prevent UI freeze and handles package cache delays for instant list synchronization.
* **Filter Modes**: Toggle between **All Apps**, **System Apps**, and **User Apps** instantly.
* **Real-time Search**: Search packages dynamically as you type.
* **Bulk Actions**: Includes **Select All** and **Unselect All** buttons to easily manage multiple packages.
* **Right-Click Context Menu**:
  * **Uninstall App**: Directly remove targeted packages.
  * **Copy Package Name**: Copy package identifier to system clipboard.
  * **Open App Settings on Phone**: Automatically launches the selected app's settings page on the connected Android device.

---

## Prerequisites

1. **Python 3.10+** (Fully compatible with Python 3.14+ and Tcl 9).
2. **ADB (Android Debug Bridge)**:
   * Download [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools).
   * Ensure `adb` is added to your Windows System `PATH` or place the script directly inside the `platform-tools` folder.
3. **Android Device Settings**:
   * Enable **USB Debugging** under `Settings > Developer Options`.
   * Enable **Install via USB / USB Debugging (Security Settings)** if using Xiaomi (MIUI/HyperOS), Realme, or Oppo devices.

---

## How to Run

1. Clone or download this repository.
2. Connect your Android device to your PC via USB.
3. Open terminal/command prompt and run:

```bash
python app_uninstaller.py