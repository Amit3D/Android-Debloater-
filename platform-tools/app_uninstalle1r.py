import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk


class ADBAppUninstaller:

    def __init__(self, root):
        self.root = root
        self.root.title("ADB App Uninstaller Pro")
        self.root.geometry("700x600")

        # Top Control Frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter Dropdown
        tk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 2))
        self.filter_type = ttk.Combobox(
            control_frame,
            values=["All Apps", "System Apps", "User Apps"],
            state="readonly",
            width=12,
        )
        self.filter_type.current(0)
        self.filter_type.pack(side=tk.LEFT, padx=5)
        self.filter_type.bind("<<ComboboxSelected>>", lambda e: self.fetch_apps())

        self.btn_refresh = tk.Button(
            control_frame, text="🔄 Refresh", command=self.fetch_apps
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_uninstall = tk.Button(
            control_frame,
            text="🗑 Uninstall Selected",
            bg="#d9534f",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.uninstall_selected,
        )
        self.btn_uninstall.pack(side=tk.RIGHT, padx=5)

        # Selection Control Frame (Select All / Clear Selection)
        select_frame = tk.Frame(self.root)
        select_frame.pack(fill=tk.X, padx=10, pady=2)

        tk.Button(
            select_frame, text="Select All", command=self.select_all, width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(
            select_frame, text="Unselect All", command=self.unselect_all, width=12
        ).pack(side=tk.LEFT)

        self.lbl_status = tk.Label(
            select_frame, text="", fg="gray", font=("Arial", 9)
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=5)

        # Search Bar Frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_list)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, expand=True, padx=5)

        # App Listbox + Scrollbar
        self.listbox_frame = tk.Frame(self.root)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = tk.Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            self.listbox_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=self.scrollbar.set,
            font=("Consolas", 10),
            activestyle="none",
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        # Right-click Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Uninstall This App", command=self.uninstall_single_right_click
        )
        self.context_menu.add_command(
            label="Copy Package Name", command=self.copy_package_name
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Open App Settings on Phone", command=self.open_app_info
        )

        # Bind Right Click
        self.listbox.bind("<Button-3>", self.show_context_menu)

        self.all_packages = []
        self.fetch_apps()

    def run_adb_command(self, cmd):
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

    def fetch_apps(self):
        self.listbox.delete(0, tk.END)
        self.lbl_status.config(text="Fetching package list...")

        def task():
            devices = self.run_adb_command(["adb", "devices"])
            if "device" not in devices.replace("List of devices attached", ""):
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", "No ADB device detected. Ensure USB Debugging is ON."
                    ),
                )
                self.root.after(
                    0, lambda: self.lbl_status.config(text="No device connected")
                )
                return

            selected_filter = self.filter_type.get()
            if selected_filter == "User Apps":
                cmd = ["adb", "shell", "pm", "list", "packages", "-3"]
            elif selected_filter == "System Apps":
                cmd = ["adb", "shell", "pm", "list", "packages", "-s"]
            else:
                cmd = ["adb", "shell", "pm", "list", "packages"]

            output = self.run_adb_command(cmd)
            self.all_packages = sorted(
                [
                    line.replace("package:", "").strip()
                    for line in output.splitlines()
                    if line.startswith("package:")
                ]
            )

            # Update GUI safely on main thread
            self.root.after(0, lambda: self.populate_list(self.all_packages))

        threading.Thread(target=task, daemon=True).start()

    def populate_list(self, packages):
        self.listbox.delete(0, tk.END)
        for pkg in packages:
            self.listbox.insert(tk.END, pkg)
        self.lbl_status.config(text=f"Total: {len(packages)} packages")

    def filter_list(self, *args):
        query = self.search_var.get().lower()
        filtered = [pkg for pkg in self.all_packages if query in pkg.lower()]
        self.populate_list(filtered)

    def select_all(self):
        self.listbox.select_set(0, tk.END)

    def unselect_all(self):
        self.listbox.selection_clear(0, tk.END)

    def show_context_menu(self, event):
        try:
            # Select the item under the mouse pointer
            index = self.listbox.nearest(event.y)
            if index >= 0:
                # If target isn't already selected, select only it
                if index not in self.listbox.curselection():
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.select_set(index)
                self.context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass

    def copy_package_name(self):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            pkg = self.listbox.get(selected_indices[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(pkg)
            self.lbl_status.config(text=f"Copied: {pkg}")

    def open_app_info(self):
        selected_indices = self.listbox.curselection()
        if selected_indices:
            pkg = self.listbox.get(selected_indices[0])
            cmd = [
                "adb",
                "shell",
                "am",
                "start",
                "-a",
                "android.settings.APPLICATION_DETAILS_SETTINGS",
                "-d",
                f"package:{pkg}",
            ]
            self.run_adb_command(cmd)

    def uninstall_single_right_click(self):
        self.uninstall_selected()

    def uninstall_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one app.")
            return

        selected_pkgs = [self.listbox.get(i) for i in selected_indices]

        confirm = messagebox.askyesno(
            "Confirm Uninstall",
            f"Are you sure you want to uninstall {len(selected_pkgs)} app(s)?",
        )
        if not confirm:
            return

        # Lock UI during deletion process
        self.btn_uninstall.config(state=tk.DISABLED)
        self.lbl_status.config(text="Uninstalling, please wait...")

        def worker():
            for pkg in selected_pkgs:
                self.run_adb_command(
                    ["adb", "shell", "pm", "uninstall", "--user", "0", pkg]
                )

            # Essential delay so Android OS cleans package cache before we query again
            self.root.after(800, self.finish_uninstall)

        threading.Thread(target=worker, daemon=True).start()

    def finish_uninstall(self):
        self.btn_uninstall.config(state=tk.NORMAL)
        messagebox.showinfo("Success", "Selected apps uninstalled!")
        self.fetch_apps()


if __name__ == "__main__":
    root = tk.Tk()
    app = ADBAppUninstaller(root)
    root.mainloop()
