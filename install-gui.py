"""
Evershade — GUI Installer for Linux
A visual wizard installer for the Evershade self-hosted AI agent platform.
Requires: Python 3.6+, Tkinter (usually pre-installed on Ubuntu Desktop).
Run with: sudo python3 install-gui.py
"""

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
        "ERROR: Tkinter is not installed. Install it with: sudo apt install python3-tk"
    )
    sys.exit(1)

# ─── Constants ────────────────────────────────────────────────────────
REPO_URL = "https://github.com/LukaG712/Evershade.git"
DEFAULT_DIR = os.path.expanduser("~/Evershade")
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
def run_command(cmd, check=False):
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=300, check=False
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except OSError as e:
        return -1, "", str(e)


def command_exists(cmd):
    return shutil.which(cmd) is not None


def get_invoking_user():
    return os.environ.get("SUDO_USER", os.environ.get("USER", "root"))


def is_root():
    return os.geteuid() == 0


# ─── Installer Logic ──────────────────────────────────────────────────
class Installer:
    def __init__(self):
        self.profile = "standard"
        self.custom_services = []  # Populated when profile is "custom"
        self.install_dir = DEFAULT_DIR
        self.use_systemd = True
        self.use_desktop = True
        self.start_services_flag = True
        self.regenerate_keys = True
        self.user = get_invoking_user()
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
        for cmd in ["git", "curl", "wget"]:
            if not command_exists(cmd):
                missing.append(cmd)
        return missing

    def install_dependencies(self):
        """Install missing system dependencies."""
        rc, _out, _err = run_command("apt-get update -y")
        if rc != 0:
            return False, "Failed to update package lists"
        for cmd in ["git", "curl", "wget", "ca-certificates", "gnupg", "lsb-release"]:
            if not command_exists(cmd):
                rc, _out, _err = run_command(f"apt-get install -y {cmd}")
                if rc != 0:
                    return False, f"Failed to install {cmd}"
        return True, "Dependencies installed"

    def install_docker(self):
        """Install Docker Engine if not present."""
        if command_exists("docker") and run_command("docker compose version")[0] == 0:
            return True, "Docker already installed"

        # Remove old versions
        for old in [
            "docker.io",
            "docker-doc",
            "docker-compose",
            "docker-compose-v2",
            "podman-docker",
            "containerd",
            "runc",
        ]:
            run_command(f"apt-get remove -y {old}")

        # Add Docker GPG key
        run_command("install -m 0755 -d /etc/apt/keyrings")
        rc, _, err = run_command(
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc"
        )
        if rc != 0:
            return False, f"Failed to add Docker GPG key: {err}"
        run_command("chmod a+r /etc/apt/keyrings/docker.asc")

        # Detect arch
        rc, arch, _ = run_command("dpkg --print-architecture")
        if arch == "arm64":
            arch_var = "arm64"
        else:
            arch_var = "amd64"

        # Add Docker repo
        rc, codename, _ = run_command('. /etc/os-release && echo "$VERSION_CODENAME"')
        repo_line = f"deb [arch={arch_var} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu {codename} stable"
        run_command(
            f"echo '{repo_line}' | tee /etc/apt/sources.list.d/docker.list > /dev/null"
        )

        # Install Docker
        run_command("apt-get update -y")
        rc, _, err = run_command(
            "apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
        )
        if rc != 0:
            return False, f"Failed to install Docker: {err}"

        # Start Docker
        run_command("systemctl enable docker")
        run_command("systemctl start docker")

        return True, "Docker installed successfully"

    def setup_docker_group(self):
        """Add user to docker group."""
        if not command_exists("getent"):
            return True, "Skipped (getent not available)"
        run_command("groupadd docker 2>/dev/null || true")
        rc, _, _ = run_command(f"id {self.user} 2>/dev/null")
        if rc == 0:
            rc, _, _ = run_command(f"id -nG {self.user} 2>/dev/null | grep -qw docker")
            if rc != 0:
                run_command(f"usermod -aG docker {self.user}")
        return True, f"User '{self.user}' added to docker group"

    def clone_repo(self):
        """Clone or update the Evershade repository."""
        if os.path.isdir(self.install_dir):
            if os.path.isdir(os.path.join(self.install_dir, ".git")):
                # Update existing
                rc, _out, err = run_command(f"cd '{self.install_dir}' && git pull")
                if rc != 0:
                    return False, f"Failed to update repo: {err}"
                return True, "Repository updated"
            else:
                return False, "Directory exists but is not a git repo"
        else:
            rc, _out, err = run_command(f"git clone {REPO_URL} '{self.install_dir}'")
            if rc != 0:
                return False, f"Failed to clone repo: {err}"
            return True, "Repository cloned"

    def install_services(self):
        """Run the service installer script."""
        install_sh = os.path.join(self.install_dir, "install.sh")
        if not os.path.isfile(install_sh):
            return False, "install.sh not found"

        os.chmod(install_sh, 0o755)
        cmd = f"cd '{self.install_dir}' && bash install.sh --profile {self.profile}"
        if self.profile == "custom" and self.custom_services:
            cmd += f" --custom {','.join(self.custom_services)}"
        # Always run as root; chown in install.sh handles ownership.
        rc, _out, _err = run_command(cmd)
        if rc != 0:
            return False, f"Service install failed: {_err[:200]}"
        return True, "Services installed"

    def init_submodules(self):
        """Initialize and update git submodules."""
        cmd = f"cd '{self.install_dir}' && git submodule update --init --recursive"
        rc, _out, _err = run_command(cmd)
        if rc != 0:
            # Submodules might not be set up, that's ok if install.sh worked
            pass
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
        with open(env_path) as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            stripped = line.strip()
            for var, key in key_map.items():
                if stripped.startswith(f"{var}="):
                    new_lines.append(f"{var}={key}\n")
                    break
            else:
                new_lines.append(line)

        with open(env_path, "w") as f:
            f.writelines(new_lines)

        # Set ownership
        if self.user and self.user != "root":
            run_command(
                f"chown {self.user}:{self.user} '{env_path}' 2>/dev/null || true"
            )

        return True, ".env created with secure keys"

    def create_systemd_service(self):
        """Create systemd service file."""
        if not self.use_systemd:
            return True, "Skipped"

        service_content = f"""[Unit]
Description=Evershade AI Agent Platform
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=forking
User={self.user}
Group={self.user}
WorkingDirectory={self.install_dir}
ExecStart={self.install_dir}/start.sh --profile {self.profile}
ExecStop={self.install_dir}/stop.sh
Restart=on-failure
RestartSec=10
Environment=HOME={self.install_dir}

[Install]
WantedBy=multi-user.target
"""
        service_path = "/etc/systemd/system/evershade.service"
        try:
            with open(service_path, "w") as f:
                f.write(service_content)
            run_command("systemctl daemon-reload")
            return True, "Systemd service created"
        except OSError as e:
            return False, f"Failed to create systemd service: {e}"

    def create_desktop_entry(self):
        """Create desktop launcher icon."""
        if not self.use_desktop:
            return True, "Skipped"

        user_home = os.path.expanduser(f"~{self.user}")
        desktop_dir = os.path.join(user_home, ".local/share/applications")
        os.makedirs(desktop_dir, exist_ok=True)

        desktop_content = f"""[Desktop Entry]
Name=Evershade
Comment=Self-hosted AI Agent Platform
Exec=gnome-terminal -- bash -c "cd {self.install_dir} && ./start.sh --profile {self.profile}; exec bash"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=true
"""
        desktop_path = os.path.join(desktop_dir, "evershade.desktop")
        try:
            with open(desktop_path, "w") as f:
                f.write(desktop_content)
            if self.user and self.user != "root":
                run_command(
                    f"chown {self.user}:{self.user} '{desktop_path}' 2>/dev/null || true"
                )
            return True, "Desktop launcher created"
        except OSError as e:
            return False, f"Failed to create desktop entry: {e}"

    def start_services(self):
        """Start Evershade services."""
        if not self.start_services_flag:
            return True, "Skipped"

        start_sh = os.path.join(self.install_dir, "start.sh")
        if not os.path.isfile(start_sh):
            return False, "start.sh not found"

        os.chmod(start_sh, 0o755)
        cmd = f"cd '{self.install_dir}' && bash start.sh --profile {self.profile}"
        # Always run as root; ownership is set by install.sh.
        rc, out, err = run_command(cmd)
        if rc != 0:
            # Combine stdout and stderr for the error message.
            # start.sh prints to stdout, so show both when available.
            combined = out
            if err and err not in combined:
                combined = f"{combined}\n{err}" if combined else err
            if not combined:
                combined = (
                    "No output captured. Possible causes:\n"
                    "- Docker is not installed or not running\n"
                    "- .env file is missing or malformed\n"
                    "- Required service directories are not installed\n"
                    "- docker-compose.yml is missing\n"
                    "Try running manually: cd /root/Evershade && bash start.sh --profile full"
                )
            return False, f"Failed to start services:\n{combined[:800]}"
        return True, "Services started"


# ─── GUI Application ──────────────────────────────────────────────────
class EvershadeInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Evershade Installer")
        self.root.geometry("750x550")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)

        # Style — Brutalist black-and-white theme matching the website
        self.style = ttk.Style()
        self.style.configure(".", font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 11))
        self.style.configure(
            "Heading.TLabel", font=("Helvetica", 13, "bold"), foreground="#000"
        )
        self.style.configure(
            "Success.TLabel", foreground="#000", font=("Helvetica", 11, "bold")
        )
        self.style.configure(
            "Error.TLabel", foreground="#c00", font=("Helvetica", 11, "bold")
        )
        self.style.configure("Info.TLabel", foreground="#555", font=("Helvetica", 10))
        self.style.configure("Small.TLabel", font=("Helvetica", 9))
        self.style.configure(
            "Card.TFrame", background="#fff", borderwidth=1, relief="solid"
        )
        self.style.configure("Card.TLabel", background="#fff")
        self.style.configure(
            "Card.TLabelframe", background="#fff", borderwidth=1, relief="solid"
        )
        self.style.configure(
            "Card.TLabelframe.Label", foreground="#000", font=("Helvetica", 11, "bold")
        )
        self.style.configure(
            "Accent.TButton",
            font=("Helvetica", 10, "bold"),
            background="#000",
            foreground="#fff",
            borderwidth=1,
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#fff")],
            foreground=[("active", "#000")],
        )
        self.style.configure("TProgressbar", thickness=16, troughcolor="#e5e5e5")
        self.style.map("TProgressbar", background=[("active", "#000")])
        self.style.configure(
            "Danger.TButton", font=("Helvetica", 10), foreground="#c00"
        )
        self.style.configure("Green.TLabel", foreground="#000")
        self.style.configure("Red.TLabel", foreground="#c00")
        self.style.configure("Orange.TLabel", foreground="#888")
        self.style.configure("Gray.TLabel", foreground="#777")
        self.style.configure("Mono.TLabel", font=("Courier", 9))
        self.style.configure("Label.TLabel", font=("Helvetica", 10), foreground="#000")

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
        # Black header bar matching website's brutalist style
        header = tk.Frame(self.root, bg="#000", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="EVERSHADE INSTALLER",
            font=("Helvetica", 16, "bold"),
            fg="#fff",
            bg="#000",
            anchor="w",
        )
        title.pack(side="left", padx=20, pady=(0, 0))

        subtitle = tk.Label(
            header,
            text="SELF-HOSTED AI AGENT PLATFORM",
            font=("Helvetica", 9),
            fg="#aaa",
            bg="#000",
            anchor="e",
        )
        subtitle.pack(side="right", padx=20, pady=(0, 0))

        # Divider line
        divider = tk.Frame(self.root, bg="#000", height=2)
        divider.pack(fill="x")
        divider.pack_propagate(False)

    def _build_progress(self):
        prog_frame = ttk.Frame(self.root, padding=(20, 10, 20, 5))
        prog_frame.pack(fill="x")

        self.progress = ttk.Progressbar(prog_frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 5))

        self.step_label = ttk.Label(prog_frame, text="STEP 1 OF 7", style="Mono.TLabel")
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
        # Windows mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        # Linux mouse wheel (scroll up/down)
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel_linux)

    def _on_canvas_leave(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mouse_wheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _build_navigation(self):
        # Divider before nav
        divider = tk.Frame(self.root, bg="#e5e5e5", height=1)
        divider.pack(fill="x")
        divider.pack_propagate(False)

        nav = ttk.Frame(self.root, padding=(20, 10, 20, 20))
        nav.pack(fill="x")

        self.back_btn = ttk.Button(
            nav, text="← BACK", command=self._prev_step, style="Accent.TButton"
        )
        self.back_btn.pack(side="left")

        self.next_btn = ttk.Button(
            nav, text="NEXT →", command=self._next_step, style="Accent.TButton"
        )
        self.next_btn.pack(side="right")

        self.cancel_btn = ttk.Button(
            nav, text="CANCEL", command=self._cancel, style="Danger.TButton"
        )
        self.cancel_btn.pack(side="right", padx=(0, 10))

    def _create_steps(self):
        """Define all wizard steps."""
        self.steps = [
            ("Welcome", self._step_welcome),
            ("System Check", self._step_system_check),
            ("Installation Options", self._step_options),
            ("Install Docker", self._step_docker),
            ("Clone & Install", self._step_clone),
            ("Configure", self._step_configure),
            ("System Integration", self._step_integration),
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
            text=f"STEP {index + 1} OF {total}: {self.steps[index][0].upper()}"
        )

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Call step builder
        builder = self.steps[index][1]
        builder(self.content_frame)

        # Update scroll region after content is built
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

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
                text="CLOSE",
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
        # Section label
        ttk.Label(parent, text="WELCOME TO EVERSHADE", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        desc = ttk.Label(
            parent,
            text=(
                "Evershade is a self-hosted AI agent platform that lets you create, manage, and run "
                "AI-powered agents on your own hardware. This wizard will guide you through the installation process."
            ),
            style="Subtitle.TLabel",
            wraplength=650,
            justify="left",
        )
        desc.pack(pady=(0, 20), anchor="w")

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        features = ttk.Label(
            parent,
            text=(
                "  DOCKER-BASED MICROSERVICES\n"
                "  AI AGENTS FOR CODE, WEB SCRAPING, SEARCH\n"
                "  ENCRYPTED SECRETS MANAGEMENT\n"
                "  REAL-TIME NOTIFICATIONS (SLACK, DISCORD, EMAIL, TELEGRAM)\n"
                "  WEB DASHBOARD FOR MANAGEMENT\n"
                "  FULLY SELF-HOSTED — YOUR DATA STAYS YOURS"
            ),
            style="Mono.TLabel",
            justify="left",
        )
        features.pack(pady=(0, 20), anchor="w")

        # Divider
        div2 = tk.Frame(parent, bg="#e5e5e5", height=1)
        div2.pack(fill="x", pady=(0, 15))
        div2.pack_propagate(False)

        warn = ttk.Label(
            parent,
            text="⚠ THIS INSTALLER REQUIRES ROOT (SUDO) PRIVILEGES FOR DOCKER.",
            style="Orange.TLabel",
        )
        warn.pack(anchor="w")

        if not is_root():
            err = ttk.Label(
                parent,
                text="❌ NOT RUNNING AS ROOT. PLEASE RUN: sudo python3 install-gui.py",
                style="Error.TLabel",
            )
            err.pack(pady=10, anchor="w")

    # ─── Step: System Check ───────────────────────────────────────────
    def _step_system_check(self, parent):
        ttk.Label(parent, text="SYSTEM CHECK", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        # Check Ubuntu
        ubuntu_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        ubuntu_info.pack(pady=(0, 10), anchor="w")

        # Check architecture
        arch_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        arch_info.pack(pady=(0, 10), anchor="w")

        # Divider
        div2 = tk.Frame(parent, bg="#e5e5e5", height=1)
        div2.pack(fill="x", pady=(0, 10))
        div2.pack_propagate(False)

        # Check dependencies
        deps_frame = ttk.Frame(parent)
        deps_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(deps_frame, text="REQUIRED TOOLS:", style="Heading.TLabel").pack(
            anchor="w"
        )

        tools_frame = ttk.Frame(parent)
        tools_frame.pack(fill="x", pady=(0, 15))

        # Check Docker
        docker_info = ttk.Label(parent, text="", style="Info.TLabel", justify="left")
        docker_info.pack(pady=(0, 10), anchor="w")

        # Run checks
        # Ubuntu
        if os.path.isfile("/etc/os-release"):
            with open("/etc/os-release") as f:
                release = {}
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        release[k] = v.strip().strip('"')
            version = release.get("VERSION_ID", "unknown")
            pretty = release.get("PRETTY_NAME", "unknown")
            ubuntu_info.config(text=f"🖥  System: {pretty}")
            try:
                version_tuple = tuple(map(int, version.split(".")))
                if version_tuple < (20, 4):
                    ubuntu_info.config(
                        style="Error.TLabel",
                        text=f"❌ Ubuntu 20.04+ required. Detected: {version}",
                    )
            except ValueError:
                pass
        else:
            ubuntu_info.config(
                style="Error.TLabel", text="⚠ Not Ubuntu — proceeding anyway"
            )

        # Arch
        _rc, arch, _ = run_command(
            "dpkg --print-architecture 2>/dev/null || echo unknown"
        )
        arch_emoji = "✓" if arch in ("amd64", "arm64") else "⚠"
        arch_info.config(text=f"{arch_emoji}  Architecture: {arch}")

        # Tools
        missing = self.installer.check_dependencies()
        for tool in ["git", "curl", "wget", "python3"]:
            exists = command_exists(tool)
            status = "✓" if exists else "✗"
            style_name = "Green.TLabel" if exists else "Red.TLabel"
            ttk.Label(
                tools_frame,
                text=f"  {status}  {tool}",
                style=style_name,
            ).pack(anchor="w")

        # Docker
        docker_exists = command_exists("docker")
        compose_exists = docker_exists and run_command("docker compose version")[0] == 0
        if docker_exists and compose_exists:
            _rc, _ver, _ = run_command("docker --version | awk '{print $3}'")
            docker_info.config(
                text=f"✓  Docker: {_ver} (Compose available)",
                style="Green.TLabel",
            )
        elif docker_exists:
            docker_info.config(
                text="⚠  Docker installed but Compose missing",
                style="Orange.TLabel",
            )
        else:
            docker_info.config(
                text="✗  Docker not installed (will be installed)",
                style="Red.TLabel",
            )

        # Install button for missing deps
        if missing:
            install_btn = ttk.Button(
                parent,
                text="INSTALL MISSING DEPENDENCIES",
                command=self._install_deps_callback,
                style="Accent.TButton",
            )
            install_btn.pack(pady=10)
            self._deps_install_btn = install_btn

    def _install_deps_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="Installing...")
                break
        ok, _msg = self.installer.install_dependencies()
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                if ok:
                    child.config(text="✓ DEPENDENCIES INSTALLED")
                else:
                    child.config(state="normal", text="RETRY INSTALL")
                self.root.update()
                break

    # ─── Step: Installation Options ───────────────────────────────────
    def _step_options(self, parent):
        ttk.Label(parent, text="INSTALLATION OPTIONS", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        # Profile selection
        prof_frame = ttk.LabelFrame(
            parent, text="INSTALLATION PROFILE", padding=15, style="Card.TLabelframe"
        )
        prof_frame.pack(fill="x", pady=(0, 15))

        self.profile_var = tk.StringVar(value=self.installer.profile)
        self.custom_frame = None  # Will hold the custom checkboxes frame
        self.service_vars = {}  # Stores checkbox variables for custom mode

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
            parent, text="SELECT SERVICES", padding=15, style="Card.TLabelframe"
        )

        # Required services
        req_frame = ttk.Frame(self.custom_frame)
        req_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(
            req_frame,
            text="REQUIRED (CANNOT BE REMOVED):",
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
        ttk.Label(opt_frame, text="OPTIONAL:", style="Gray.TLabel").pack(anchor="w")

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

        # Select All / Deselect All buttons for optional services
        btn_frame = ttk.Frame(self.custom_frame)
        btn_frame.pack(fill="x", pady=(5, 0))
        ttk.Button(
            btn_frame, text="SELECT ALL", command=self._select_all_optional
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame, text="DESELECT ALL", command=self._deselect_all_optional
        ).pack(side="left")

        # Hide custom frame initially
        self.custom_frame.pack_forget()

        # Update profile description now that custom_frame exists
        self._update_profile_desc()

        # Install directory
        dir_frame = ttk.LabelFrame(
            parent, text="INSTALLATION DIRECTORY", padding=15, style="Card.TLabelframe"
        )
        dir_frame.pack(fill="x", pady=(0, 15))

        dir_row = ttk.Frame(dir_frame)
        dir_row.pack(fill="x")

        self.dir_var = tk.StringVar(value=self.installer.install_dir)
        dir_entry = ttk.Entry(dir_row, textvariable=self.dir_var, width=50)
        dir_entry.pack(side="left", padx=(0, 10))

        browse_btn = ttk.Button(dir_row, text="BROWSE", command=self._browse_dir)
        browse_btn.pack(side="left")

        default_btn = ttk.Button(
            dir_row, text="DEFAULT", command=lambda: self.dir_var.set(DEFAULT_DIR)
        )
        default_btn.pack(side="left", padx=(10, 0))

        # Options
        opt_frame = ttk.LabelFrame(
            parent, text="OPTIONS", padding=15, style="Card.TLabelframe"
        )
        opt_frame.pack(fill="x")

        self.systemd_var = tk.BooleanVar(value=self.installer.use_systemd)
        self.desktop_var = tk.BooleanVar(value=self.installer.use_desktop)
        self.start_var = tk.BooleanVar(value=self.installer.start_services_flag)
        self.regen_var = tk.BooleanVar(value=self.installer.regenerate_keys)

        ttk.Checkbutton(
            opt_frame,
            text="Create systemd service (auto-start on boot)",
            variable=self.systemd_var,
        ).pack(anchor="w", pady=3)
        ttk.Checkbutton(
            opt_frame, text="Create desktop launcher icon", variable=self.desktop_var
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
            self.custom_frame.pack(fill="x", pady=(0, 15), before=None)
            # Repack custom frame after profile frame and before dir frame
            self.custom_frame.pack_forget()
            self.custom_frame.pack(fill="x", pady=(0, 15))

            # Count selected services
            selected = self._get_custom_services()
            self.profile_desc.config(
                text=f"   Selected ({len(selected)}): {', '.join(selected)}"
            )
        else:
            # Hide custom frame
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
        if hasattr(self, "systemd_var"):
            self.installer.use_systemd = self.systemd_var.get()
        if hasattr(self, "desktop_var"):
            self.installer.use_desktop = self.desktop_var.get()
        if hasattr(self, "start_var"):
            self.installer.start_services_flag = self.start_var.get()
        if hasattr(self, "regen_var"):
            self.installer.regenerate_keys = self.regen_var.get()

        # Save custom services if custom profile selected
        if self.installer.profile == "custom":
            self.installer.custom_services = self._get_custom_services()

    # ─── Step: Install Docker ─────────────────────────────────────────
    def _step_docker(self, parent):
        ttk.Label(parent, text="DOCKER SETUP", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        info = ttk.Label(
            parent,
            text="Docker is required to run Evershade services. The installer will set up Docker Engine and Compose.",
            style="Info.TLabel",
            wraplength=650,
            justify="left",
        )
        info.pack(pady=(0, 15), anchor="w")

        # Check current state
        docker_ok = (
            command_exists("docker") and run_command("docker compose version")[0] == 0
        )
        if docker_ok:
            _rc, _ver, _ = run_command("docker --version | awk '{print $3}'")
            status = ttk.Label(
                parent,
                text=f"✓  Docker {_ver} is already installed and ready.",
                style="Success.TLabel",
            )
            status.pack(pady=10, anchor="w")

            group_rc, _, _ = run_command(
                f"id -nG {self.installer.user} 2>/dev/null | grep -qw docker"
            )
            if group_rc == 0:
                grp_status = ttk.Label(
                    parent,
                    text=f"✓  User '{self.installer.user}' is in the docker group.",
                    style="Success.TLabel",
                )
            else:
                grp_status = ttk.Label(
                    parent,
                    text=f"⚠  User '{self.installer.user}' will be added to docker group.",
                    style="Orange.TLabel",
                )
            grp_status.pack(pady=5, anchor="w")
        else:
            status = ttk.Label(
                parent,
                text="Docker will be installed during this step.",
                style="Orange.TLabel",
            )
            status.pack(pady=10, anchor="w")

        self.docker_log = tk.Text(
            parent,
            height=10,
            width=80,
            wrap="word",
            state="disabled",
            font=("Courier", 9),
        )
        self.docker_log.pack(fill="both", expand=True, pady=10)

        install_btn = ttk.Button(
            parent,
            text="INSTALL DOCKER",
            command=self._install_docker_callback,
            style="Accent.TButton",
        )
        install_btn.pack(pady=5)

        self.docker_done = False

    def _log_to_text(self, text_widget, msg):
        text_widget.config(state="normal")
        text_widget.insert("end", msg + "\n")
        text_widget.see("end")
        text_widget.config(state="disabled")
        self.root.update()

    def _install_docker_callback(self):
        # Find button
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="INSTALLING...")
                break

        self._log_to_text(self.docker_log, "CHECKING DOCKER INSTALLATION...")
        docker_ok = (
            command_exists("docker") and run_command("docker compose version")[0] == 0
        )

        if not docker_ok:
            self._log_to_text(self.docker_log, "INSTALLING DOCKER ENGINE...")
            ok, msg = self.installer.install_docker()
            if ok:
                self._log_to_text(self.docker_log, f"✓ {msg}")
            else:
                self._log_to_text(self.docker_log, f"✗ {msg}")
                # Re-enable button
                for child in self.content_frame.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.config(state="normal", text="RETRY")
                        break
                return
        else:
            self._log_to_text(self.docker_log, "DOCKER ALREADY INSTALLED, SKIPPING...")

        self._log_to_text(
            self.docker_log,
            f"SETTING UP DOCKER GROUP FOR USER '{self.installer.user}'...",
        )
        ok, msg = self.installer.setup_docker_group()
        self._log_to_text(self.docker_log, f"{'✓' if ok else '✗'} {msg}")

        self._log_to_text(self.docker_log, "DOCKER SETUP COMPLETE!")

        # Re-enable button
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ DONE")
                break

    # ─── Step: Clone & Install ────────────────────────────────────────
    def _step_clone(self, parent):
        ttk.Label(parent, text="CLONE & INSTALL SERVICES", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

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
            font=("Courier", 9),
        )
        self.clone_log.pack(fill="both", expand=True, pady=10)

        install_btn = ttk.Button(
            parent,
            text="INSTALL",
            command=self._install_callback,
            style="Accent.TButton",
        )
        install_btn.pack(pady=5)

    def _install_callback(self):
        # Find and disable button
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="INSTALLING...")
                break

        # Clone repo
        self._log_to_text(self.clone_log, "CLONING EVERSHADE REPOSITORY...")
        ok, msg = self.installer.clone_repo()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")
        if not ok:
            self._enable_install_btn()
            return

        # Init submodules
        self._log_to_text(self.clone_log, "INITIALIZING GIT SUBMODULES...")
        ok, msg = self.installer.init_submodules()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")

        # Install services
        self._log_to_text(
            self.clone_log,
            f"INSTALLING SERVICES (PROFILE: {self.installer.profile})...",
        )
        ok, msg = self.installer.install_services()
        self._log_to_text(self.clone_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.clone_log, "INSTALLATION COMPLETE!")
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="✓ DONE")
                    break
        else:
            self._enable_install_btn()

    def _enable_install_btn(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="RETRY")
                break

    # ─── Step: Configure ──────────────────────────────────────────────
    def _step_configure(self, parent):
        ttk.Label(parent, text="CONFIGURATION", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

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
            font=("Courier", 9),
        )
        self.config_log.pack(fill="both", expand=True, pady=10)

        config_btn = ttk.Button(
            parent,
            text="CONFIGURE",
            command=self._configure_callback,
            style="Accent.TButton",
        )
        config_btn.pack(pady=5)

    def _configure_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="CONFIGURING...")
                break

        self._log_to_text(self.config_log, "CREATING .ENV CONFIGURATION...")
        ok, msg = self.installer.create_env()
        self._log_to_text(self.config_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.config_log, "API KEYS GENERATED FOR:")
            for var in API_KEY_VARS:
                self._log_to_text(self.config_log, f"  • {var}")
            self._log_to_text(self.config_log, "CONFIGURATION COMPLETE!")

            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="✓ DONE")
                    break
        else:
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="RETRY")
                    break

    # ─── Step: System Integration ─────────────────────────────────────
    def _step_integration(self, parent):
        ttk.Label(parent, text="SYSTEM INTEGRATION", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        info = ttk.Label(
            parent,
            text="Optional: Set up systemd service and desktop launcher for easy management.",
            style="Info.TLabel",
            wraplength=650,
            justify="left",
        )
        info.pack(pady=(0, 15), anchor="w")

        self.integ_log = tk.Text(
            parent,
            height=8,
            width=80,
            wrap="word",
            state="disabled",
            font=("Courier", 9),
        )
        self.integ_log.pack(fill="both", expand=True, pady=10)

        setup_btn = ttk.Button(
            parent,
            text="SETUP INTEGRATION",
            command=self._integ_callback,
            style="Accent.TButton",
        )
        setup_btn.pack(pady=5)

    def _integ_callback(self):
        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="SETTING UP...")
                break

        # Systemd
        if self.installer.use_systemd:
            self._log_to_text(self.integ_log, "CREATING SYSTEMD SERVICE...")
            ok, msg = self.installer.create_systemd_service()
            self._log_to_text(self.integ_log, f"{'✓' if ok else '✗'} {msg}")
            if ok:
                self._log_to_text(self.integ_log, "  MANAGE WITH:")
                self._log_to_text(self.integ_log, "    sudo systemctl start evershade")
                self._log_to_text(
                    self.integ_log,
                    "    sudo systemctl enable evershade  # AUTO-START ON BOOT",
                )
        else:
            self._log_to_text(self.integ_log, "SKIPPING SYSTEMD SERVICE (DISABLED)")

        # Desktop
        if self.installer.use_desktop:
            self._log_to_text(self.integ_log, "CREATING DESKTOP LAUNCHER...")
            ok, msg = self.installer.create_desktop_entry()
            self._log_to_text(self.integ_log, f"{'✓' if ok else '✗'} {msg}")
        else:
            self._log_to_text(self.integ_log, "SKIPPING DESKTOP LAUNCHER (DISABLED)")

        self._log_to_text(self.integ_log, "SYSTEM INTEGRATION COMPLETE!")

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ DONE")
                break

    # ─── Step: Start Services ─────────────────────────────────────────
    def _step_start(self, parent):
        ttk.Label(parent, text="START SERVICES", style="Heading.TLabel").pack(
            pady=(0, 15), anchor="w"
        )

        # Divider
        div = tk.Frame(parent, bg="#e5e5e5", height=1)
        div.pack(fill="x", pady=(0, 15))
        div.pack_propagate(False)

        if self.installer.start_services_flag:
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
            font=("Courier", 9),
        )
        self.start_log.pack(fill="both", expand=True, pady=10)

        start_btn = ttk.Button(
            parent,
            text="START SERVICES",
            command=self._start_callback,
            style="Accent.TButton",
        )
        start_btn.pack(pady=5)

    def _start_callback(self):
        if not self.installer.start_services_flag:
            self._log_to_text(self.start_log, "STARTING SERVICES IS DISABLED.")
            self._log_to_text(
                self.start_log,
                f"TO START MANUALLY: cd {self.installer.install_dir} && ./start.sh --profile {self.installer.profile}",
            )
            for child in self.content_frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.config(state="normal", text="OK")
                    break
            return

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="disabled", text="STARTING...")
                break

        self._log_to_text(self.start_log, "STARTING EVERSHADE SERVICES...")
        ok, msg = self.installer.start_services()
        self._log_to_text(self.start_log, f"{'✓' if ok else '✗'} {msg}")

        if ok:
            self._log_to_text(self.start_log, "")
            self._log_to_text(self.start_log, "SERVICES ARE RUNNING!")
            self._log_to_text(self.start_log, "  API:     http://localhost:8080")
            self._log_to_text(
                self.start_log,
                "  DASHBOARD: http://localhost:5173 (IF SLAMMER INSTALLED)",
            )

        for child in self.content_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state="normal", text="✓ DONE" if ok else "RETRY")
                break

    # ─── Step: Complete ───────────────────────────────────────────────
    def _step_complete(self, parent):
        card = ttk.LabelFrame(
            parent, text="INSTALLATION COMPLETE!", padding=25, style="Card.TLabelframe"
        )
        card.pack(fill="both", expand=True)

        success = ttk.Label(
            card,
            text="✓  EVERSHADE HAS BEEN SUCCESSFULLY INSTALLED!",
            style="Success.TLabel",
            font=("Helvetica", 14, "bold"),
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

        summary_text = f"""INSTALLATION SUMMARY:
  DIRECTORY:    {self.installer.install_dir}
  PROFILE:      {profile_name}
  SERVICES:     {", ".join(services)}
  USER:         {self.installer.user}
  SYSTEMD:      {"YES" if self.installer.use_systemd else "NO"}
  DESKTOP ICON: {"YES" if self.installer.use_desktop else "NO"}

QUICK COMMANDS:
  cd {self.installer.install_dir}
  ./start.sh --profile {self.installer.profile}     # START SERVICES
  ./stop.sh                        # STOP SERVICES
  ./update.sh                      # UPDATE SERVICES

WEB INTERFACES:
  API:       http://localhost:8080
  DASHBOARD: http://localhost:5173 (IF SLAMMER INSTALLED)

FOR LLM PROVIDERS, EDIT {self.installer.install_dir}/.env AND ADD YOUR API KEYS:
  EVERSHADE_OPENAI_API_KEY
  EVERSHADE_ANTHROPIC_API_KEY
  EVERSHADE_GOOGLE_API_KEY"""

        summary = tk.Text(
            card,
            height=18,
            width=80,
            wrap="word",
            font=("Courier", 9),
            padx=10,
            pady=10,
        )
        summary.insert("1.0", summary_text)
        summary.config(state="disabled")
        summary.pack(fill="x", pady=10)

        welcome = ttk.Label(
            card,
            text="WELCOME TO EVERSHADE! 🏚️",
            style="Success.TLabel",
            font=("Helvetica", 12, "bold"),
        )
        welcome.pack(pady=(10, 0))


if __name__ == "__main__":
    if not is_root():
        print("⚠  WARNING: This installer works best with sudo privileges.")
        print("   Run: sudo python3 install-gui.py")
        print()
        answer = input("   Continue without sudo? (y/N): ")
        if answer.lower() != "y":
            print("Aborted. Run with sudo for full functionality.")
            sys.exit(1)

    root = tk.Tk()
    app = EvershadeInstallerGUI(root)
    root.mainloop()
