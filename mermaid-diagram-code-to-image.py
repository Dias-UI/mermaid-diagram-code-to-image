import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import subprocess
import tempfile
import json
from pathlib import Path

class MermaidDiagramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mermaid Diagram Generator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.setup_styles()
        
        # Create main frame
        main_frame = ttk.Frame(root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Mermaid Diagram Generator", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Mermaid Code", 
                                   style='Section.TLabelframe')
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Text area for mermaid code
        self.text_area = scrolledtext.ScrolledText(
            input_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#333333',
            insertbackground='#007acc',
            selectbackground='#007acc',
            selectforeground='white'
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample text
        sample_text = """graph LR
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
        
        self.text_area.insert('1.0', sample_text)
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Format selection
        format_frame = ttk.LabelFrame(options_frame, text="Output Format")
        format_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.format_var = tk.StringVar(value="png")
        formats = [("PNG", "png"), ("SVG", "svg"), ("PDF", "pdf")]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, variable=self.format_var, 
                           value=value).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Resolution selection
        res_frame = ttk.LabelFrame(options_frame, text="Resolution (for PNG)")
        res_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.resolution_var = tk.StringVar(value="2")
        resolutions = [("1x", "1"), ("2x", "2"), ("3x", "3"), ("4x", "4")]
        
        for text, value in resolutions:
            ttk.Radiobutton(res_frame, text=text, variable=self.resolution_var, 
                           value=value).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Theme selection
        theme_frame = ttk.LabelFrame(options_frame, text="Theme")
        theme_frame.pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value="default")
        themes = [("Default", "default"), ("Dark", "dark"), ("Forest", "forest")]
        
        for text, value in themes:
            ttk.Radiobutton(theme_frame, text=text, variable=self.theme_var, 
                           value=value).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Transparent background option
        self.transparent_var = tk.BooleanVar(value=False)
        transparent_chk = ttk.Checkbutton(options_frame, text="Transparent Background", variable=self.transparent_var)
        transparent_chk.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear", 
                              command=self.clear_text, style='Action.TButton')
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load file button
        load_btn = ttk.Button(button_frame, text="Load File", 
                             command=self.load_file, style='Action.TButton')
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Generate button
        generate_btn = ttk.Button(button_frame, text="Generate & Save Image", 
                                 command=self.generate_diagram, 
                                 style='Primary.TButton')
        generate_btn.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              style='Status.TLabel')
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure styles
        style.configure('Main.TFrame', background='#f0f0f0')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), 
                       background='#f0f0f0', foreground='#2c3e50')
        style.configure('Section.TLabelframe', background='#f0f0f0')
        style.configure('Section.TLabelframe.Label', background='#f0f0f0', 
                       font=('Arial', 10, 'bold'))
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.configure('Action.TButton', font=('Arial', 9))
        style.configure('Status.TLabel', background='#f0f0f0', 
                       foreground='#7f8c8d', font=('Arial', 9))
        
    def clear_text(self):
        self.text_area.delete('1.0', tk.END)
        self.status_var.set("Text cleared")
        
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Mermaid file",
            filetypes=[("Text files", "*.txt"), ("Mermaid files", "*.mmd"),     
                      ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert('1.0', content)
                    self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def generate_diagram(self):
        mermaid_code = self.text_area.get('1.0', tk.END).strip()
        
        if not mermaid_code:
            messagebox.showwarning("Warning", "Please enter Mermaid diagram code")
            return
        
        try:
            self.status_var.set("Generating diagram...")
            self.root.update()
            
            # Get current script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Ask user for save location and filename
            file_format = self.format_var.get()
            save_path = filedialog.asksaveasfilename(
                title="Save diagram as",
                initialdir=script_dir,
                defaultextension=f".{file_format}",
                filetypes=[(f"{file_format.upper()} files", f"*.{file_format}"), 
                          ("All files", "*.*")]
            )
            
            if not save_path:
                self.status_var.set("Save cancelled")
                return
            
            # Create temporary mermaid file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', 
                                           delete=False, encoding='utf-8') as temp_file:
                temp_file.write(mermaid_code)
                temp_mmd_path = temp_file.name
            
            temp_css_path = None
            try:
                # Build mermaid CLI command
                cmd = [r'C:\Users\Brian\AppData\Roaming\npm\mmdc.cmd', '-i', temp_mmd_path, '-o', save_path]
                
                # Add format-specific options
                if file_format == 'png':
                    scale = self.resolution_var.get()
                    cmd.extend(['-s', scale])
                
                # Add theme if not default
                theme = self.theme_var.get()
                if theme != 'default':
                    cmd.extend(['-t', theme])
                    # Use custom CSS for dark mode
                    if theme == 'dark':
                        # Write embedded CSS to a temp file
                        dark_css = '''.edgePath path {\n  stroke: #fff !important;\n  stroke-width: 3px !important;\n}\n.marker {\n  stroke: #fff !important;\n  fill: #fff !important;\n}\n'''
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8') as css_file:
                            css_file.write(dark_css)
                            temp_css_path = css_file.name
                        cmd.extend(['--cssFile', temp_css_path])
            
                # Add background color or transparency
                if file_format in ('png', 'svg'):
                    if self.transparent_var.get():
                        cmd.extend(['-b', 'transparent'])
                    elif file_format == 'png':
                        cmd.extend(['-b', 'white'])
                
                # Execute mermaid CLI
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      timeout=30)
                
                if result.returncode == 0:
                    self.status_var.set(f"Diagram saved successfully: {os.path.basename(save_path)}")
                    messagebox.showinfo("Success", 
                                      f"Diagram saved successfully!\n\nLocation: {save_path}")
                else:
                    error_msg = result.stderr or "Unknown error occurred"
                    raise Exception(error_msg)
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_mmd_path)
                except:
                    pass
                if temp_css_path:
                    try:
                        os.unlink(temp_css_path)
                    except:
                        pass
                    
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Generation timed out. Please try again.")
            self.status_var.set("Generation timed out")
        except FileNotFoundError:
            messagebox.showerror("Error", 
                               "Mermaid CLI not found!\n\n" + 
                               "Please install mermaid-cli:\n" +
                               "npm install -g @mermaid-js/mermaid-cli")
            self.status_var.set("Mermaid CLI not found")
        except Exception as e:
            error_msg = str(e)
            if "ENOENT" in error_msg or "command not found" in error_msg:
                messagebox.showerror("Error", 
                                   "Mermaid CLI not found!\n\n" + 
                                   "Please install mermaid-cli:\n" +
                                   "npm install -g @mermaid-js/mermaid-cli")
            else:
                messagebox.showerror("Error", f"Failed to generate diagram:\n{error_msg}")
            self.status_var.set(f"Error: {error_msg}")

def main():
    root = tk.Tk()
    app = MermaidDiagramGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == '__main__':
    main()
