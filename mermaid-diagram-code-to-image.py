import os
import shutil
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk


def find_mermaid_cli():
    """Return the installed Mermaid CLI path, or None if it cannot be found."""
    candidates = [
        shutil.which("mmdc.cmd"),
        shutil.which("mmdc"),
    ]

    # npm's normal per-user Windows installation location.
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "npm" / "mmdc.cmd")

    # Keep compatibility with the path used by the older project script.
    candidates.append(Path(r"C:\Users\Brian\AppData\Roaming\npm\mmdc.cmd"))

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def configure_puppeteer():
    """Use Chrome when it is installed, without requiring one exact location."""
    chrome_candidates = [
        os.environ.get("CHROME_PATH"),
        os.environ.get("PROGRAMFILES", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("PROGRAMFILES(X86)", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("LOCALAPPDATA", "") + r"\Google\Chrome\Application\chrome.exe",
    ]
    for chrome_path in chrome_candidates:
        if chrome_path and Path(chrome_path).is_file():
            os.environ["PUPPETEER_EXECUTABLE_PATH"] = chrome_path
            return chrome_path
    return None


class MermaidDiagramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mermaid Diagram Generator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        configure_puppeteer()
        self.setup_styles()

        main_frame = ttk.Frame(root, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(
            main_frame,
            text="Mermaid Diagram Generator",
            style="Title.TLabel",
        ).pack(pady=(0, 20))

        input_frame = ttk.LabelFrame(
            main_frame, text="Mermaid Code", style="Section.TLabelframe"
        )
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.text_area = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#333333",
            insertbackground="#007acc",
            selectbackground="#007acc",
            selectforeground="white",
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_area.insert("1.0", self.default_mermaid_code())

        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        format_frame = ttk.LabelFrame(options_frame, text="Output Format")
        format_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.format_var = tk.StringVar(value="png")
        for label, value in (("PNG", "png"), ("SVG", "svg"), ("PDF", "pdf")):
            ttk.Radiobutton(
                format_frame, text=label, variable=self.format_var, value=value
            ).pack(side=tk.LEFT, padx=5, pady=5)

        res_frame = ttk.LabelFrame(options_frame, text="Resolution (for PNG)")
        res_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.resolution_var = tk.StringVar(value="2")
        for label, value in (("1x", "1"), ("2x", "2"), ("3x", "3"), ("4x", "4")):
            ttk.Radiobutton(
                res_frame, text=label, variable=self.resolution_var, value=value
            ).pack(side=tk.LEFT, padx=5, pady=5)

        theme_frame = ttk.LabelFrame(options_frame, text="Theme")
        theme_frame.pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="default")
        for label, value in (("Default", "default"), ("Dark", "dark"), ("Forest", "forest")):
            ttk.Radiobutton(
                theme_frame, text=label, variable=self.theme_var, value=value
            ).pack(side=tk.LEFT, padx=5, pady=5)

        self.transparent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Transparent Background",
            variable=self.transparent_var,
        ).pack(side=tk.LEFT, padx=(10, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="Load File", command=self.load_file).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(
            button_frame,
            text="Generate & Save Image",
            command=self.generate_diagram,
        ).pack(side=tk.RIGHT)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel").pack(
            fill=tk.X, pady=(10, 0)
        )

    @staticmethod
    def default_mermaid_code():
        return """graph LR
    A[PV Output
    21,435.82 kWh
    100%] --> B[Inverter Input
    4,484.80 kWh
    20.9%]
    A --> C[Excess
    16,843.14 kWh
    78.6%]
    B --> D[Inverter Output
    4,260.56 kWh
    19.9%]
    B --> IL[Inverter Losses
    224.24 kWh
    1.0%]
    A --> BAT[Battery
    1,093.16 kWh in
    985.28 kWh out]
    BAT --> BL[Battery Losses
    107.88 kWh
    0.5%]
    BAT --> B
    D --> E[Load
    4,260.56 kWh
    19.9%]
    F[Grid Purchases
    0.00 kWh
    0.0%] --> E"""

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Main.TFrame", background="#f0f0f0")
        style.configure(
            "Title.TLabel", font=("Arial", 16, "bold"),
            background="#f0f0f0", foreground="#2c3e50"
        )
        style.configure("Section.TLabelframe", background="#f0f0f0")
        style.configure(
            "Section.TLabelframe.Label", background="#f0f0f0",
            font=("Arial", 10, "bold")
        )
        style.configure("Status.TLabel", background="#f0f0f0", foreground="#7f8c8d")

    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.status_var.set("Text cleared")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Mermaid file",
            filetypes=[("Mermaid files", "*.mmd"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            content = Path(file_path).read_text(encoding="utf-8")
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.status_var.set(f"Loaded: {Path(file_path).name}")
        except OSError as error:
            messagebox.showerror("Error", f"Failed to load file:\n{error}")

    def generate_diagram(self):
        mermaid_code = self.text_area.get("1.0", tk.END).strip()
        if not mermaid_code:
            messagebox.showwarning("Warning", "Please enter Mermaid diagram code")
            return

        mmdc_path = find_mermaid_cli()
        if not mmdc_path:
            messagebox.showerror(
                "Mermaid CLI not found",
                "Install Mermaid CLI with:\n\n"
                "npm install -g @mermaid-js/mermaid-cli\n\n"
                "Then restart this program.",
            )
            self.status_var.set("Mermaid CLI not found")
            return

        file_format = self.format_var.get()
        save_path = filedialog.asksaveasfilename(
            title="Save diagram as",
            initialdir=str(Path(__file__).parent),
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}"), ("All files", "*.*")],
        )
        if not save_path:
            self.status_var.set("Save cancelled")
            return

        self.status_var.set("Generating diagram...")
        self.root.update_idletasks()
        temp_mmd_path = None
        temp_css_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".mmd", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(mermaid_code)
                temp_mmd_path = temp_file.name

            cmd = [mmdc_path, "-i", temp_mmd_path, "-o", save_path]
            if file_format == "png":
                cmd.extend(["-s", self.resolution_var.get()])

            theme = self.theme_var.get()
            if theme != "default":
                cmd.extend(["-t", theme])
                if theme == "dark":
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".css", delete=False, encoding="utf-8"
                    ) as css_file:
                        css_file.write(
                            ".edgePath path { stroke: #fff !important; stroke-width: 3px !important; }\n"
                            ".marker { stroke: #fff !important; fill: #fff !important; }\n"
                        )
                        temp_css_path = css_file.name
                    cmd.extend(["--cssFile", temp_css_path])

            if file_format in ("png", "svg"):
                cmd.extend(["-b", "transparent" if self.transparent_var.get() else "white"])

            startupinfo = None
            creationflags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            if result.returncode != 0:
                details = result.stderr.strip() or result.stdout.strip() or "Unknown Mermaid CLI error."
                raise RuntimeError(details)

            self.status_var.set(f"Saved: {Path(save_path).name}")
            messagebox.showinfo("Success", f"Diagram saved successfully!\n\nLocation: {save_path}")
        except subprocess.TimeoutExpired:
            self.status_var.set("Generation timed out")
            messagebox.showerror("Error", "Generation timed out after 60 seconds.")
        except (OSError, RuntimeError) as error:
            self.status_var.set("Generation failed")
            messagebox.showerror("Generation failed", str(error))
        finally:
            for temporary_path in (temp_mmd_path, temp_css_path):
                if temporary_path:
                    try:
                        Path(temporary_path).unlink(missing_ok=True)
                    except OSError:
                        pass


def main():
    root = tk.Tk()
    MermaidDiagramGUI(root)
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()
