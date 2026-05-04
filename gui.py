"""
gui.py - Tkinter GUI for the honeypot project.
Features:
- Start / Stop the backend honeypot
- Show live logs from logs/connections.csv
- Fake login trap (captures credentials to logs/credentials.csv)
- Export logs button
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading, os, time, csv, subprocess, sys, webbrowser
import backend_app

BASE_DIR = os.path.dirname(__file__)
LOG_CSV = os.path.join(BASE_DIR, "logs", "connections.csv")
CRED_CSV = os.path.join(BASE_DIR, "logs", "credentials.csv")

class HoneypotGUI:
    def __init__(self, root):
        self.root = root
        root.title("Honeypot - GUI Control Panel")
        root.geometry("900x600")
        self.create_widgets()
        self.log_updater_running = False

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Controls frame
        ctrl = ttk.LabelFrame(frm, text="Control", padding=8)
        ctrl.pack(fill=tk.X)
        self.start_btn = ttk.Button(ctrl, text="Start Honeypot", command=self.start_honeypot)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(ctrl, text="Stop Honeypot", command=self.stop_honeypot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.export_btn = ttk.Button(ctrl, text="Export Logs", command=self.export_logs)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Tabs for Views
        tabs = ttk.Notebook(frm)
        tabs.pack(fill=tk.BOTH, expand=True, pady=8)

        # Logs tab
        self.log_tab = ttk.Frame(tabs)
        tabs.add(self.log_tab, text="Logs")
        self.log_text = tk.Text(self.log_tab, wrap=tk.NONE)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # Small toolbar for clearing/viewing
        ltbar = ttk.Frame(self.log_tab)
        ltbar.pack(fill=tk.X)
        ttk.Button(ltbar, text="Refresh", command=self.load_logs).pack(side=tk.LEFT)
        ttk.Button(ltbar, text="Clear Display", command=lambda: self.log_text.delete("1.0", tk.END)).pack(side=tk.LEFT)

        # Fake Login tab
        self.login_tab = ttk.Frame(tabs)
        tabs.add(self.login_tab, text="Fake Login Page")
        lfm = ttk.Frame(self.login_tab, padding=20)
        lfm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(lfm, text="This is a fake login page to attract attackers.").pack(pady=5)
        ttk.Label(lfm, text="Username").pack()
        self.username_entry = ttk.Entry(lfm, width=30)
        self.username_entry.pack(pady=2)
        ttk.Label(lfm, text="Password").pack()
        self.password_entry = ttk.Entry(lfm, width=30, show="*")
        self.password_entry.pack(pady=2)
        ttk.Button(lfm, text="Submit (simulate attacker)", command=self.fake_submit).pack(pady=8)
        ttk.Label(lfm, text="Captured credentials:").pack(pady=4)
        self.creds_text = tk.Text(lfm, height=6)
        self.creds_text.pack(fill=tk.X, pady=4)

        # Help / About
        about = ttk.LabelFrame(frm, text="About", padding=8)
        about.pack(fill=tk.X)
        ttk.Label(about, text="Honeypot GUI — Start/Stop backend, view logs, fake login trap.").pack(side=tk.LEFT)
        ttk.Button(about, text="Open logs folder", command=self.open_logs_folder).pack(side=tk.RIGHT)

    def start_honeypot(self):
        try:
            backend_app.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start honeypot: {e}")
            return
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.start_log_updater()
        messagebox.showinfo("Started", "Honeypot started on ports 2222,8080,2121")

    def stop_honeypot(self):
        backend_app.stop()
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_log_updater()
        messagebox.showinfo("Stopped", "Honeypot stopped")

    def export_logs(self):
        if not os.path.exists(LOG_CSV):
            messagebox.showwarning("No logs", "No logs found yet.")
            return
        dest = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if dest:
            import shutil
            shutil.copy(LOG_CSV, dest)
            messagebox.showinfo("Exported", f"Logs exported to {dest}")

    def open_logs_folder(self):
        folder = os.path.join(BASE_DIR, "logs")
        if sys.platform.startswith("win"):
            os.startfile(folder)
        else:
            try:
                subprocess.Popen(["xdg-open", folder])
            except Exception:
                webbrowser.open(folder)

    def load_logs(self):
        self.log_text.delete("1.0", tk.END)
        if not os.path.exists(LOG_CSV):
            return
        with open(LOG_CSV, "r", encoding="utf-8") as f:
            data = f.read()
        self.log_text.insert(tk.END, data)

    def start_log_updater(self):
        self.log_updater_running = True
        def run():
            last_size = 0
            while self.log_updater_running:
                try:
                    if os.path.exists(LOG_CSV):
                        size = os.path.getsize(LOG_CSV)
                        if size != last_size:
                            self.load_logs()
                            last_size = size
                except Exception:
                    pass
                time.sleep(1.0)
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def stop_log_updater(self):
        self.log_updater_running = False

    def fake_submit(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        if not user and not pwd:
            messagebox.showwarning("Empty", "Enter some values to simulate attacker input")
            return
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        first = not os.path.exists(CRED_CSV) or os.path.getsize(CRED_CSV) == 0
        with open(CRED_CSV, "a", newline='', encoding="utf-8") as f:
            w = csv.writer(f)
            if first:
                w.writerow(["timestamp","username","password","src_ip"])
            w.writerow([ts, user, pwd, "127.0.0.1"])
        # refresh creds display
        self.load_creds_display()
        # also write to connections log as an http attempt for visibility
        with open(LOG_CSV, "a", newline='', encoding="utf-8") as f:
            w = csv.writer(f)
            if os.path.getsize(LOG_CSV) == 0:
                w.writerow(["timestamp","service","src_ip","src_port","payload_summary","raw_payload"])
            w.writerow([ts, "http", "127.0.0.1", 0, f"FAKE_LOGIN user={user}", ""])
        self.load_logs()
        messagebox.showinfo("Captured", "Fake credentials captured (for demo)")

    def load_creds_display(self):
        self.creds_text.delete("1.0", tk.END)
        if not os.path.exists(CRED_CSV):
            return
        with open(CRED_CSV, "r", encoding="utf-8") as f:
            self.creds_text.insert(tk.END, f.read())

if __name__ == "__main__":
    import datetime
    root = tk.Tk()
    app = HoneypotGUI(root)
    app.load_creds_display()
    root.mainloop()