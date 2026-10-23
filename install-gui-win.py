"""
Evershade — GUI Installer for Windows
A visual wizard installer for the Evershade self-hosted AI agent platform.
Requires: Python 3.6+, Tkinter (usually pre-installed with Python on Windows).
Run with: python install-gui-win.py
"""

import ctypes
import os
import secrets
import shutil
import subprocess
import sys

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    print(
        "ERROR: Tkinter is not installed. Install Python from python.org (Tkinter is included by default)."
    )
    sys.exit(1)

# ─── Constants ────────────────────────────────────────────────────────
REPO_URL = "https://github.com/LukaG712/Evershade.git"
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Evershade")
PROFILES = {
    "minimal": {
        "name": "Minimal",
        "desc": "Core services only (4 services)",
        "services": ["Greenie", "Slinker", "Trapper", "Gobber"],
    },
    "standard": {
        "name": "Standard",
        "desc": "All services except dashboard (8 services)",
        "services": [
            "Greenie",
            "Slinker",
            "Trapper",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
        ],
    },
    "full": {
        "name": "Full",
        "desc": "Everything including Slammer dashboard (10 services)",
        "services": [
            "Greenie",
            "Slinker",
            "Trapper",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
            "Slammer",
            "Speedy",
        ],
    },
}

ALL_SERVICES = [
    {"name": "Greenie", "required": True, "desc": "Central API backend"},
    {"name": "Slinker", "required": True, "desc": "Code execution"},
    {"name": "Trapper", "required": True, "desc": "Web scraping"},
    {"name": "Gobber", "required": True, "desc": "Storage & search"},
    {"name": "Sneaker", "required": False, "desc": "Observability & alerting"},
    {"name": "Hider", "required": False, "desc": "Encrypted secrets management"},
    {
        "name": "Poltergeist",
        "required": False,
        "desc": "Notifications (Slack, Discord, Email, Telegram)",
    },
    {
        "name": "Shrewd",
        "required": False,
        "desc": "LLM providers (OpenAI, Anthropic, Google, Ollama)",
    },
    {"name": "Slammer", "required": False, "desc": "Web dashboard"},
    {"name": "Speedy", "required": False, "desc": "CLI tool"},
]

API_KEY_VARS = [
    "EVERSHADE_GREENIE_API_KEY",
    "EVERSHADE_SLINKER_API_KEY",
    "EVERSHADE_TRAPPER_API_KEY",
    "EVERSHADE_GOBBER_API_KEY",
    "EVERSHADE_SNEAKER_API_KEY",
    "EVERSHADE_HIDER_API_KEY",
    "EVERSHADE_POLTERGEIST_API_KEY",
    "EVERSHADE_SHREWD_API_KEY",
    "EVERSHADE_ENCRYPTION_KEY",
]


# ─── Helpers ──────────────────────────────────────────────────────────
def run_command(cmd, check=False, timeout=300):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except OSError as e:
        return -1, "", str(e)


def command_exists(cmd):
    return shutil.which(cmd) is not None


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except OSError:
        return False


def get_windows_username():
    """Get the current Windows username."""
    return os.environ.get("USERNAME", "user")


# ─── Installer Logic ──────────────────────────────────────────────────
class Installer:
    def __init__(self):
        self.profile = "standard"
        self.custom_services = []
        self.install_dir = DEFAULT_DIR
        self.start_services = True
        self.regenerate_keys = True
        self.create_shortcut = True
        self.user = get_windows_username()
        self.log = []

    def get_selected_services(self):
        """Return the list of services to install based on profile or custom selection."""
        if self.profile == "custom" and self.custom_services:
            return self.custom_services
        profile_info = PROFILES.get(self.profile, {})
        return profile_info.get("services", [])

    def log_msg(self, msg):
        self.log.append(msg)

    def check_dependencies(self):
        """Check if required system tools are available."""
        missing = []
        for cmd in ["git", "curl"]:
            if not command_exists(cmd):
                missing.append(cmd)
        return missing

    def check_docker(self):
        """Check if Docker Desktop is installed and running."""
        docker_exists = command_exists("docker")
        if not docker_exists:
            return False, "Docker Desktop not found"

        rc, ver, _ = run_command("docker --version")
        if rc != 0:
            return False, "Docker command failed"

        # Check if Docker daemon is running
        rc, _, err = run_command("docker info")
        if rc != 0:
            return False, f"Docker daemon not running: {err[:100]}"

        # Check Docker Compose
        rc, _compose_ver, _ = run_command("docker compose version")
        if rc != 0:
            return False, "Docker Compose plugin not found"

        return True, f"Docker {ver} with Compose"

    def clone_repo(self):
        """Clone or update the Evershade repository."""
        if os.path.isdir(self.install_dir):
            if os.path.isdir(os.path.join(self.install_dir, ".git")):
                rc, _out, err = run_command(f'cd "{self.install_dir}" && git pull')
                if rc != 0:
                    return False, f"Failed to update repo: {err}"
                return True, "Repository updated"
            else:
                return False, "Directory exists but is not a git repo"
        else:
            rc, _out, err = run_command(f'git clone {REPO_URL} "{self.install_dir}"')
            if rc != 0:
                return False, f"Failed to clone repo: {err}"
            return True, "Repository cloned"

    def install_services(self):
        """Run the Windows service installer script via PowerShell."""
        install_ps1 = os.path.join(self.install_dir, "install.ps1")
        if not os.path.isfile(install_ps1):
            return False, "install.ps1 not found"

        cmd = f'powershell -ExecutionPolicy Bypass -File "{install_ps1}" -Profile {self.profile}'
        if self.profile == "custom" and self.custom_services:
            cmd += f" -CustomServices '{','.join(self.custom_services)}'"

        rc, _out, _err = run_command(cmd, timeout=600)
        if rc != 0:
            return False, f"Service install failed: {_err[:200]}"
        return True, "Services installed"

    def init_submodules(self):
        """Initialize and update git submodules."""
        cmd = f'cd "{self.install_dir}" && git submodule update --init --recursive'
        rc, _out, _err = run_command(cmd)
        if rc != 0:
            pass  # Submodules might not be set up
        return True, "Submodules initialized"

    def create_env(self):
        """Create .env file with auto-generated keys."""
        env_path = os.path.join(self.install_dir, ".env")
        env_example = os.path.join(self.install_dir, ".env.example")

        if not os.path.isfile(env_example):
            return False, ".env.example not found"

        if os.path.isfile(env_path) and not self.regenerate_keys:
            return True, "Existing .env kept"

        # Copy example
        shutil.copy2(env_example, env_path)

        # Generate keys
        key_map = {}
        for var in API_KEY_VARS:
            key_map[var] = secrets.token_hex(32)

        # Read and replace
        with open(env_path, encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            stripped = line.strip()
            replaced = False
            for var, key in key_map.items():
                if stripped.startswith(f"{var}="):
                    new_lines.append(f"{var}={key}\n")
                    replaced = True
                    break
            if not replaced:
                new_lines.append(line)

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return True, ".env created with secure keys"

    def create_shortcut(self):
        """Create a desktop shortcut for starting Evershade."""
        if not self.create_shortcut:
            return True, "Skipped"

        try:
            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Evershade.lnk")

            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = "powershell.exe"
            shortcut.Arguments = f'-ExecutionPolicy Bypass -File "{os.path.join(self.install_dir, "start.ps1")}" -Profile {self.profile}'
            shortcut.WorkingDirectory = self.install_dir
            shortcut.Description = "Evershade AI Agent Platform"
            shortcut.IconLocation = "powershell.exe,0"
            shortcut.save()

            return True, "Desktop shortcut created"
        except ImportError:
            # pywin32 not available, create a batch file instead
            try:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                batch_path = os.path.join(desktop, "Start Evershade.bat")
                with open(batch_path, "w", encoding="utf-8") as f:
                    f.write("@echo off\n")
                    f.write(f'cd /d "{self.install_dir}"\n')
                    f.write(
                        f"powershell -ExecutionPolicy Bypass -File start.ps1 -Profile {self.profile}\n"
                    )
                    f.write("pause\n")
                return (
                    True,
                    "Desktop batch file created (pywin32 not available for .lnk shortcut)",
                )
            except OSError as e:
                return False, f"Failed to create shortcut: {e}"
        except OSError as e:
            return False, f"Failed to create shortcut: {e}"

    def start_services(self):
        """Start Evershade services."""
        if not self.start_services:
            return True, "Skipped"

        start_ps1 = os.path.join(self.install_dir, "start.ps1")
        if not os.path.isfile(start_ps1):
            return False, "start.ps1 not found"

        cmd = f'powershell -ExecutionPolicy Bypass -File "{start_ps1}" -Profile {self.profile}'
        rc, _out, err = run_command(cmd, timeout=300)
        if rc != 0:
            return False, f"Failed to start services: {err[:200]}"
        return True, "Services started"


# ─── GUI Application ──────────────────────────────────────────────────
class EvershadeInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Evershade Installer")
        self.root.geometry("750x550")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        # Style
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 11))
        self.style.configure("Heading.TLabel", font=("Segoe UI", 13, "bold"))
        self.style.configure(
            "Success.TLabel", foreground="green", font=("Segoe UI", 11, "bold")
        )
        self.style.configure(
            "Error.TLabel", foreground="red", font=("Segoe UI", 11, "bold")
        )
        self.style.configure("Info.TLabel", foreground="#555", font=("Segoe UI", 10))
        self.style.configure("Small.TLabel", font=("Segoe UI", 9))
        self.style.configure("Card.TFrame", background="#f5f5f5")
        self.style.configure("Card.TLabel", background="#f5f5f5")
        self.style.configure("Card.TLabelframe", background="#f5f5f5")
        self.style.configure(
            "Card.TLabelframe.Label", foreground="#333", font=("Segoe UI", 11, "bold")
        )
        self.style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        self.style.configure("TProgressbar", thickness=20)
        self.style.configure("Danger.TButton", foreground="red")
        self.style.configure("Green.TLabel", foreground="green")
        self.style.configure("Red.TLabel", foreground="red")
        self.style.configure("Orange.TLabel", foreground="orange")
        self.style.configure("Gray.TLabel", foreground="#666")

        # State
        self.installer = Installer()
        self.current_step = 0
        self.steps = []
        self.step_frames = []
        self.step_results = {}

        # Build UI
        self._build_header()
        self._build_progress()
        self._build_content_area()
        self._build_navigation()

        # Create steps
        self._create_steps()
        self._show_step(0)

    def _build_header(self):
        header = ttk.Frame(self.root, padding=(20, 15, 20, 5))
        header.pack(fill="x")

        title = ttk.Label(header, text="🏚️  Evershade Installer", style="Title.TLabel")
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Self-hosted AI Agent Platform — Windows Setup Wizard",
            style="Info.TLabel",
        )
        subtitle.pack(anchor="w")

    def _build_progress(self):
        prog_frame = ttk.Frame(self.root, padding=(20, 5, 20, 5))
        prog_frame.pack(fill="x")

        self.progress = ttk.Progressbar(prog_frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 5))

        self.step_label = ttk.Label(
            prog_frame, text="Step 1 of 7", style="Small.TLabel"
        )
        self.step_label.pack(anchor="w")

    def _build_content_area(self):
        # Container with canvas + scrollbar for scrollable content
        canvas_container = ttk.Frame(self.root)
        canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            canvas_container, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mouse wheel scrolling
        self.canvas.bind("<Enter>", self._on_canvas_enter)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        # Inner frame inside the canvas
        self.content_frame = ttk.Frame(self.canvas, padding=(20, 10, 20, 10))
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw"
        )

        # Update scroll region when content changes
        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_enter(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_canvas_leave(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _build_navigation(self):
        nav = ttk.Frame(self.root, padding=(20, 10, 20, 20))
        nav.pack(fill="x")

        self.back_btn = ttk.Button(
            nav, text="← Back", command=self._prev_step, style="Accent.TButton"
        )
        self.back_btn.pack(side="left")

        self.next_btn = ttk.Button(
            nav, text="Next →", command=self._next_step, style="Accent.TButton"
        )
        self.next_btn.pack(side="right")

        self.cancel_btn = ttk.Button(
            nav, text="Cancel", command=self._cancel, style="Danger.TButton"
        )
        self.cancel_btn.pack(side="right", padx=(0, 10))

    def _create_steps(self):
        """Define all wizard steps."""
        self.steps = [
            ("Welcome", self._step_welcome),
            ("System Check", self._step_system_check),
            ("Installation Options", self._step_options),
            ("Docker Check", self._step_docker),
            ("Clone & Install", self._step_clone),
            ("Configure", self._step_configure),
            ("Desktop Shortcut", self._step_shortcut),
            ("Start Services", self._step_start),
            ("Complete", self._step_complete),
        ]

    def _show_step(self, index):
        """Display a specific step."""
        self.current_step = index
        total = len(self.steps)
        pct = int((index / (total - 1)) * 100)
        self.progress["value"] = pct
        self.step_label.config(
            text=f"Step {index + 1} of {total}: {self.steps[index][0]}"
        )

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Reset scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Call step builder
        builder = self.steps[index][1]
        builder(self.content_frame)

        # Update nav buttons
        self.back_btn.pack_forget()
        self.next_btn.pack_forget()

        if index > 0:
            self.back_btn.pack(side="left")

        if index < total - 1:
            self.next_btn.pack(side="right")
        else:
            # Last step — show close button
            close_btn = ttk.Button(
                self.root.winfo_children()[-1],
                text="Close",
                command=self.root.quit,
                style="Accent.TButton",
            )
            close_btn.pack(side="right")

        self.root.update()

    def _next_step(self):
        # Save options when leaving the options step
        if self.current_step == 2:  # Options step
            self._save_options()
        self._show_step(self.current_step + 1)

    def _prev_step(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _cancel(self):
        if messagebox.askyesno(
            "Cancel Installation", "Are you sure you want to cancel?"
        ):
            self.root.quit()

    # ─── Step: Welcome ────────────────────────────────────────────────
    def _step_welcome(self, parent):
        card = ttk.LabelFrame(
            parent, text="Welcome to Evershade", padding=20, style="Card.TLabelframe"
        )
        card.pack(fill="both", expand=True)

        desc = ttk.Label(
            card,
            text=(
                "Evershade is a self-hosted AI agent platform that lets you create, manage, and run "
                "AI-powered agents on your own hardware. This wizard will guide you through the installation process."
            ),
            style="Subtitle.TLabel",
            wraplength=650,
            justify="left",
        )
        desc.pack(pady=(0, 20), anchor="w")

        features = ttk.Label(
            card,
            text=(
                "✓  Docker-based microservices\n"
                "✓  AI agents for code, web scraping, search, and more\n"
                "✓  Encrypted secrets management\n"
                "✓  Real-time notifications (Slack, Discord, Email, Telegram)\n"
                "✓  Web dashboard for management\n"
                "✓  Fully self-hosted — your data stays yours"
            ),
            style="Info.TLabel",
            justify="left",
        )
        features.pack(pady=(0, 20), anchor="w")

        req = ttk.Label(
            card,
            text="Requirements:\n  • Docker Desktop (will be checked)\n  • Git (will be checked)\n  • Python 3.6+ (already running this installer)",
            style="Info.TLabel",
            justify="left",
        )
        req.pack(anchor="w")

    # ─── Step: System Check ───────────────────────────────────────────
    def _step_system_check(self, parent):
        ttk.Label(parent, text="System Check", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Check Windows version
        win_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        win_info.pack(pady=(0, 10), anchor="w")

        # Check architecture
        arch_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        arch_info.pack(pady=(0, 10), anchor="w")

        # Check dependencies
        deps_frame = ttk.Frame(parent)
        deps_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(deps_frame, text="Required Tools:", style="Heading.TLabel").pack(
            anchor="w"
        )

        tools_frame = ttk.Frame(parent)
        tools_frame.pack(fill="x", pady=(0, 15))

        # Check Docker
        docker_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        docker_info.pack(pady=(0, 10), anchor="w")

        # Run checks
        # Windows version
        import platform

        win_ver = platform.version()
        win_release = platform.release()
        win_info.config(text=f"🖥  System: Windows {win_release} (Build {win_ver})")

        # Arch
        arch = platform.machine()
        arch_emoji = "✓" if arch in ("AMD64", "ARM64") else "⚠"
        arch_info.config(text=f"{arch_emoji}  Architecture: {arch}")

        # Tools
        missing = self.installer.check_dependencies()
        for tool in ["git", "curl", "python"]:
            exists = command_exists(tool)
            status = "✓" if exists else "✗"
            style_name = "Green.TLabel" if exists else "Red.TLabel"
            ttk.Label(
                tools_frame,
                text=f"  {status}  {tool}",
                style=style_name,
            ).pack(anchor="w")

        # PowerShell
        ps_exists = command_exists("powershell")
        status = "✓" if ps_exists else "✗"
        ps_style = "Green.TLabel" if ps_exists else "Red.TLabel"
        ttk.Label(
            tools_frame,
            text=f"  {status}  powershell",
            style=ps_style,
        ).pack(anchor="w")

        # Docker
        docker_ok, docker_msg = self.installer.check_docker()
        if docker_ok:
            docker_info.config(text=f"✓  {docker_msg}", style="Green.TLabel")
        else:
            docker_info.config(
                text=f"✗  {docker_msg} (Docker Desktop required)", style="Red.TLabel"
            )

        # Install button for missing deps
        if missing:
            info_lbl = ttk.Label(
                parent,
                text="Missing tools detected. Please install them before continuing:",
                style="Error.TLabel",
            )
            info_lbl.pack(pady=(5, 5), anchor="w")
            missing_list = ttk.Label(
                parent,
                text="  • Git: https://git-scm.com/download/win\n  • Curl: Included in Windows 10+",
                style="Small.TLabel",
                justify="left",
            )
            missing_list.pack(anchor="w")

    # ─── Step: Installation Options ───────────────────────────────────
    def _step_options(self, parent):
        ttk.Label(parent, text="Installation Options", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Profile selection
        prof_frame = ttk.LabelFrame(
            parent, text="Installation Profile", padding=15, style="Card.TLabelframe"
        )
        prof_frame.pack(fill="x", pady=(0, 15))

        self.profile_var = tk.StringVar(value=self.installer.profile)
        self.custom_frame = None
        self.service_vars = {}

        for key, info in PROFILES.items():
            rb = ttk.Radiobutton(
                prof_frame,
                text=f"{info['name']}",
                variable=self.profile_var,
                value=key,
                command=lambda: self._update_profile_desc(),
            )
            rb.pack(anchor="w", pady=2)
            desc_lbl = ttk.Label(
                prof_frame,
                text=f"   {info['desc']}",
                style="Gray.TLabel",
            )
            desc_lbl.pack(anchor="w")

        # Custom radio button
        custom_rb = ttk.Radiobutton(
            prof_frame,
            text="Custom",
            variable=self.profile_var,
            value="custom",
            command=lambda: self._update_profile_desc(),
        )
        custom_rb.pack(anchor="w", pady=2)
        custom_desc_lbl = ttk.Label(
            prof_frame,
            text="   Choose individual services below",
            style="Gray.TLabel",
        )
        custom_desc_lbl.pack(anchor="w")

        self.profile_desc = ttk.Label(prof_frame, text="", style="Info.TLabel")
        self.profile_desc.pack(pady=(5, 0), anchor="w")

        # Custom service selection frame (hidden by default)
        self.custom_frame = ttk.LabelFrame(
            parent, text="Select Services", padding=15, style="Card.TLabelframe"
        )

        # Required services
        req_frame = ttk.Frame(self.custom_frame)
        req_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(
            req_frame,
            text="Required (cannot be removed):",
            style="Gray.TLabel",
        ).pack(anchor="w")

        req_check_frame = ttk.Frame(self.custom_frame)
        req_check_frame.pack(fill="x", pady=(0, 10))

        for svc in ALL_SERVICES:
            if svc["required"]:
                var = tk.BooleanVar(value=True)
                self.service_vars[svc["name"]] = var
                cb = ttk.Checkbutton(
                    req_check_frame,
                    text=f"{svc['name']} — {svc['desc']}",
                    variable=var,
                    state="disabled",
                )
                cb.pack(anchor="w", pady=1)

        # Optional services
        opt_frame = ttk.Frame(self.custom_frame)
        opt_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(opt_frame, text="Optional:", style="Gray.TLabel").pack(anchor="w")

        opt_check_frame = ttk.Frame(self.custom_frame)
        opt_check_frame.pack(fill="x", pady=(0, 5))

        for svc in ALL_SERVICES:
            if not svc["required"]:
                var = tk.BooleanVar(value=False)
                self.service_vars[svc["name"]] = var
                cb = ttk.Checkbutton(
                    opt_check_frame, text=f"{svc['name']} — {svc['desc']}", variable=var
                )
                cb.pack(anchor="w", pady=1)

        # Select All / Deselect All buttons
        btn_frame = ttk.Frame(self.custom_frame)
        btn_frame.pack(fill="x", pady=(5, 0))
        ttk.Button(
            btn_frame, text="Select All Optional", command=self._select_all_optional
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame, text="Deselect All Optional", command=self._deselect_all_optional
        ).pack(side="left")

        # Hide custom frame initially
        self.custom_frame.pack_forget()

        # Update profile description now that custom_frame exists
        self._update_profile_desc()

        # Install directory
        dir_frame = ttk.LabelFrame(
            parent, text="Installation Directory", padding=15, style="Card.TLabelframe"
        )
        dir_frame.pack(fill="x", pady=(0, 15))

        dir_row = ttk.Frame(dir_frame)
        dir_row.pack(fill="x")

        self.dir_var = tk.StringVar(value=self.installer.install_dir)
        dir_entry = ttk.Entry(dir_row, textvariable=self.dir_var, width=50)
        dir_entry.pack(side="left", padx=(0, 10))

        browse_btn = ttk.Button(dir_row, text="Browse...", command=self._browse_dir)
        browse_btn.pack(side="left")

        default_btn = ttk.Button(
            dir_row, text="Default", command=lambda: self.dir_var.set(DEFAULT_DIR)
        )
        default_btn.pack(side="left", padx=(10, 0))

        # Options
        opt_frame = ttk.LabelFrame(
            parent, text="Options", padding=15, style="Card.TLabelframe"
        )
        opt_frame.pack(fill="x")

        self.shortcut_var = tk.BooleanVar(value=self.installer.create_shortcut)
        self.start_var = tk.BooleanVar(value=self.installer.start_services)
        self.regen_var = tk.BooleanVar(value=self.installer.regenerate_keys)

        ttk.Checkbutton(
            opt_frame, text="Create desktop shortcut", variable=self.shortcut_var
        ).pack(anchor="w", pady=3)
        ttk.Checkbutton(
            opt_frame, text="Start services after installation", variable=self.start_var
        ).pack(anchor="w", pady=3)
        ttk.Checkbutton(
            opt_frame,
            text="Regenerate API keys (if .env exists)",
            variable=self.regen_var,
        ).pack(anchor="w", pady=3)

    def _select_all_optional(self):
        for svc in ALL_SERVICES:
            if not svc["required"] and svc["name"] in self.service_vars:
                self.service_vars[svc["name"]].set(True)

    def _deselect_all_optional(self):
        for svc in ALL_SERVICES:
            if not svc["required"] and svc["name"] in self.service_vars:
                self.service_vars[svc["name"]].set(False)

    def _update_profile_desc(self):
        key = self.profile_var.get()

        # Guard: custom_frame may not be created yet
        if self.custom_frame is None:
            return

        # Show/hide custom frame
        if key == "custom":
            self.custom_frame.pack(fill="x", pady=(0, 15))

            selected = self._get_custom_services()
            self.profile_desc.config(
                text=f"   Selected ({len(selected)}): {', '.join(selected)}"
            )
        else:
            self.custom_frame.pack_forget()
            info = PROFILES.get(key, {})
            services = info.get("services", [])
            self.profile_desc.config(
                text=f"   Services ({len(services)}): {', '.join(services)}"
            )

    def _get_custom_services(self):
        """Get list of selected services from checkboxes."""
        selected = []
        for svc in ALL_SERVICES:
            var = self.service_vars.get(svc["name"])
            if var and var.get():
                selected.append(svc["name"])
        return selected

    def _browse_dir(self):
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)

    def _save_options(self):
        if not hasattr(self, "profile_var"):
            return
        self.installer.profile = self.profile_var.get()
        if hasattr(self, "dir_var"):
            self.installer.install_dir = self.dir_var.get()
        if hasattr(self, "shortcut_var"):
            self.installer.create_shortcut = self.shortcut_var.get()
        if hasattr(self, "start_var"):
            self.installer.start_services = self.start_var.get()
        if hasattr(self, "regen_var"):
            self.installer.regenerate_keys = self.regen_var.get()

        if self.installer.profile == "custom":
            self.installer.custom_services = self._get_custom_services()

    # ─── Step: Docker Check ─────────────────────────────────────────
    def _step_docker(self, parent):
        ttk.Label(parent, text="Docker Desktop Check", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        info = ttk.Label(
            parent,
            text="Docker Desktop is required to run Evershade services on Windows. "
            "Unlike Linux, Docker on Windows uses Docker Desktop which includes Compose.",
            style="Info.TLabel",
            wraplength=650,
            justify="left",
        )
        info.pack(pady=(0, 15), anchor="w")

        # Check current state
        docker_ok, docker_msg = self.installer.check_docker()
        if docker_ok:
            status = ttk.Label(parent, text=f"✓  {docker_msg}", style="Success.TLabel")
            status.pack(pady=10, anchor="w")
        else:
            status = ttk.Label(parent, text=f"✗  {docker_msg}", style="Error.TLabel")
            status.pack(pady=10, anchor="w")

            install_info = ttk.Label(
                parent,
                text="To install Docker Desktop:\n"
                "  1. Download from https://www.docker.com/products/docker-desktop/\n"
                "  2. Run the installer and follow the wizard\n"
                "  3. Restart if prompted\n"
                "  4. Re-run this installer",
                style="Info.TLabel",
                justify="left",
            )
            install_info.pack(pady=10, anchor="w")

            # Open download link button
            download_btn = ttk.Button(
                parent,
                text="Open Docker Desktop Download Page",
                command=lambda: os.startfile(
                    "https://www.docker.com/products/docker-desktop/"
                ),
                style="Accent.TButton",
            )
            download_btn.pack(pady=5)

        self.docker_log = tk.Text(
            parent,
            height=6,
            width=80,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.docker_log.pack(fill="both", expand=True, pady=10)

        check_btn = ttk.Button(
            parent,
            text="Re-check Docker",
            command=self._check_docker_callback,
            style="Accent.TButton",
        )
        check_btn.pack(pady=5)

    def _log_to_text(self, text_widget, msg):
        text_widget.config(state="normal")
        text_widget.insert("end", msg + "\n")
        text_widget.see("end")
        text_widget.config(state="disabled")
        self.root.update()

    def _check_docker_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Checking...")
                break

        self._log_to_text(self.docker_log, "Checking Docker Desktop...")
        docker_ok, docker_msg = self.installer.check_docker()
        if docker_ok:
            self._log_to_text(self.docker_log, f"✓ {docker_msg}")
            self._log_to_text(self.docker_log, "Docker is ready to use!")
        else:
            self._log_to_text(self.docker_log, f"✗ {docker_msg}")
            self._log_to_text(
                self.docker_log, "Please install Docker Desktop and try again."
            )

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ Done" if docker_ok else "Retry")
                break

    # ─── Step: Clone & Install ────────────────────────────────────────
    def _step_clone(self, parent):
        ttk.Label(parent, text="Clone & Install Services", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        info = ttk.Label(
            parent,
            text=f"Cloning Evershade to: {self.installer.install_dir}",
            style="Info.TLabel",
            justify="left",
        )
        info.pack(pady=(0, 5), anchor="w")

        services = self.installer.get_selected_services()
        if self.installer.profile == "custom":
            prof_label = ttk.Label(
                parent,
                text=f"Profile: Custom ({len(services)} services: {', '.join(services)})",
                style="Info.TLabel",
                justify="left",
            )
        else:
            profile_info = PROFILES.get(self.installer.profile, {})
            prof_label = ttk.Label(
                parent,
                text=f"Profile: {profile_info.get('name', self.installer.profile)} ({len(services)} services)",
                style="Info.TLabel",
                justify="left",
            )
        prof_label.pack(pady=(0, 15), anchor="w")

        self.clone_log = tk.Text(
            parent,
            height=12,
            width=80,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.clone_log.pack(fill="both", expand=True, pady=10)

        install_btn = ttk.Button(
            parent,
            text="Install",
            command=self._install_callback,
            style="Accent.TButton",
        )
        install_btn.pack(pady=5)

    def _install_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Installing...")
                break

        # Clone repo
        self._log_to_text(self.clone_log, "Cloning Evershade repository...")
        ok, msg = self.installer.clone_repo()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")
        if not ok:
            self._enable_install_btn()
            return

        # Init submodules
        self._log_to_text(self.clone_log, "Initializing git submodules...")
        ok, msg = self.installer.init_submodules()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")

        # Install services
        self._log_to_text(
            self.clone_log,
            f"Installing services (profile: {self.installer.profile})...",
        )
        ok, msg = self.installer.install_services()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.clone_log, "Installation complete!")
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="✓ Done")
                    break
        else:
            self._enable_install_btn()

    def _enable_install_btn(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="Retry")
                break

    # ─── Step: Configure ──────────────────────────────────────────────
    def _step_configure(self, parent):
        ttk.Label(parent, text="Configuration", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        info = ttk.Label(
            parent,
            text="Setting up environment variables and API keys.",
            style="Info.TLabel",
            wraplength=650,
            justify="left",
        )
        info.pack(pady=(0, 15), anchor="w")

        env_path = os.path.join(self.installer.install_dir, ".env")
        exists = os.path.isfile(env_path)

        status = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        status.pack(pady=(0, 10), anchor="w")

        if exists:
            if self.installer.regenerate_keys:
                status.config(
                    text="⚠  Existing .env will be regenerated with new API keys.",
                    style="Orange.TLabel",
                )
            else:
                status.config(
                    text="✓  Existing .env will be kept.",
                    style="Green.TLabel",
                )
        else:
            status.config(
                text="A new .env file will be created with auto-generated secure API keys.",
                style="Green.TLabel",
            )

        self.config_log = tk.Text(
            parent,
            height=8,
            width=80,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.config_log.pack(fill="both", expand=True, pady=10)

        config_btn = ttk.Button(
            parent,
            text="Configure",
            command=self._configure_callback,
            style="Accent.TButton",
        )
        config_btn.pack(pady=5)

    def _configure_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Configuring...")
                break

        self._log_to_text(self.config_log, "Creating .env configuration...")
        ok, msg = self.installer.create_env()
        self._log_to_text(self.config_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.config_log, "API keys generated for:")
            for var in API_KEY_VARS:
                self._log_to_text(self.config_log, f"  • {var}")
            self._log_to_text(self.config_log, "Configuration complete!")

            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="✓ Done")
                    break
        else:
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="Retry")
                    break

    # ─── Step: Desktop Shortcut ───────────────────────────────────────
    def _step_shortcut(self, parent):
        ttk.Label(parent, text="Desktop Shortcut", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        info = ttk.Label(
            parent,
            text="Optionally create a desktop shortcut to easily start Evershade.",
            style="Info.TLabel",
            wraplength=650,
            justify="left",
        )
        info.pack(pady=(0, 15), anchor="w")

        self.shortcut_log = tk.Text(
            parent,
            height=6,
            width=80,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.shortcut_log.pack(fill="both", expand=True, pady=10)

        setup_btn = ttk.Button(
            parent,
            text="Create Shortcut",
            command=self._shortcut_callback,
            style="Accent.TButton",
        )
        setup_btn.pack(pady=5)

    def _shortcut_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Creating...")
                break

        if self.installer.create_shortcut:
            self._log_to_text(self.shortcut_log, "Creating desktop shortcut...")
            ok, msg = self.installer.create_shortcut()
            self._log_to_text(self.shortcut_log, f"{'✓' if ok else '✗'} {msg}")
        else:
            self._log_to_text(
                self.shortcut_log, "Skipping desktop shortcut (disabled in options)"
            )

        self._log_to_text(self.shortcut_log, "Shortcut step complete!")

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ Done")
                break

    # ─── Step: Start Services ─────────────────────────────────────────
    def _step_start(self, parent):
        ttk.Label(parent, text="Start Services", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        if self.installer.start_services:
            info = ttk.Label(
                parent,
                text="Ready to start Evershade services. This may take a minute as Docker pulls images.",
                style="Info.TLabel",
                wraplength=650,
                justify="left",
            )
        else:
            info = ttk.Label(
                parent,
                text="Starting services is disabled. You can start them manually later.",
                style="Info.TLabel",
                wraplength=650,
                justify="left",
            )
        info.pack(pady=(0, 15), anchor="w")

        self.start_log = tk.Text(
            parent,
            height=10,
            width=80,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.start_log.pack(fill="both", expand=True, pady=10)

        start_btn = ttk.Button(
            parent,
            text="Start Services",
            command=self._start_callback,
            style="Accent.TButton",
        )
        start_btn.pack(pady=5)

    def _start_callback(self):
        if not self.installer.start_services:
            self._log_to_text(self.start_log, "Starting services is disabled.")
            self._log_to_text(
                self.start_log,
                f"To start manually: cd {self.installer.install_dir} && .\\start.ps1 -Profile {self.installer.profile}",
            )
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="OK")
                    break
            return

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Starting...")
                break

        self._log_to_text(self.start_log, "Starting Evershade services...")
        ok, msg = self.installer.start_services()
        self._log_to_text(self.start_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.start_log, "")
            self._log_to_text(self.start_log, "Services are running!")
            self._log_to_text(self.start_log, "  API:     http://localhost:8080")
            self._log_to_text(
                self.start_log,
                "  Dashboard: http://localhost:5173 (if Slammer installed)",
            )

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ Done" if ok else "Retry")
                break

    # ─── Step: Complete ───────────────────────────────────────────────
    def _step_complete(self, parent):
        card = ttk.LabelFrame(
            parent, text="Installation Complete!", padding=25, style="Card.TLabelframe"
        )
        card.pack(fill="both", expand=True)

        success = ttk.Label(
            card,
            text="✓  Evershade has been successfully installed!",
            style="Success.TLabel",
            font=("Segoe UI", 14, "bold"),
        )
        success.pack(pady=(0, 20), anchor="w")

        # Summary
        services = self.installer.get_selected_services()
        if self.installer.profile == "custom":
            profile_name = f"Custom ({len(services)} services)"
        else:
            profile_name = PROFILES.get(self.installer.profile, {}).get(
                "name", self.installer.profile
            )

        summary_text = f"""Installation Summary:
  Directory:    {self.installer.install_dir}
  Profile:      {profile_name}
  Services:     {", ".join(services)}
  User:         {self.installer.user}
  Shortcut:     {"Yes" if self.installer.create_shortcut else "No"}

Quick Commands:
  cd {self.installer.install_dir}
  .\\start.ps1 -Profile {self.installer.profile}     # Start services
  .\\stop.ps1                        # Stop services
  .\\update.ps1                      # Update services

Web Interfaces:
  API:       http://localhost:8080
  Dashboard: http://localhost:5173 (if Slammer installed)

For LLM providers, edit {self.installer.install_dir}\\.env and add your API keys:
  EVERSHADE_OPENAI_API_KEY
  EVERSHADE_ANTHROPIC_API_KEY
  EVERSHADE_GOOGLE_API_KEY"""

        summary = tk.Text(
            card,
            height=18,
            width=80,
            wrap="word",
            font=("Consolas", 9),
            padx=10,
            pady=10,
        )
        summary.insert("1.0", summary_text)
        summary.config(state="disabled")
        summary.pack(fill="x", pady=10)

        welcome = ttk.Label(
            card,
            text="Welcome to Evershade! 🏚️",
            style="Success.TLabel",
            font=("Segoe UI", 12, "italic"),
        )
        welcome.pack(pady=(10, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = EvershadeInstallerGUI(root)
    root.mainloop()
