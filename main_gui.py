import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font
from modules.downloader import download_journal_issues
from modules.text_extractor import TextExtractor
from modules.file_merger import merge_excel_files
from modules.data_cleaner import clean_data
from modules.keyword_analyzer import analyze_keywords
from config import CONFIG
import webbrowser

class ModernJournalProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Academic Processor Pro")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set theme colors
        self.bg_color = "#f0f2f5"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.accent_color = "#4fc3f7"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        
        # Custom fonts
        self.title_font = Font(family="Segoe UI", size=12, weight="bold")
        self.normal_font = Font(family="Segoe UI", size=10)
        self.button_font = Font(family="Segoe UI", size=10, weight="bold")
        
        # Initialize processor
        self.text_extractor = TextExtractor()
        
        self.setup_ui()
        self.create_menu()
        
        # Bind F1 key to help
        self.root.bind("<F1>", lambda e: self.show_help())
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text="Academic Processor Pro",
            font=self.title_font,
            foreground=self.secondary_color
        ).pack(side=tk.LEFT)
        
        # Source selection notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # URL Tab
        url_frame = ttk.Frame(self.notebook)
        self.setup_url_tab(url_frame)
        self.notebook.add(url_frame, text="URL Source")
        
        # File Tab
        file_frame = ttk.Frame(self.notebook)
        self.setup_file_tab(file_frame)
        self.notebook.add(file_frame, text="File Upload")
        
        # Options Frame
        options_frame = ttk.LabelFrame(
            main_frame,
            text="Processing Options",
            padding=(15, 10)
        )
        options_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.extract_var = tk.BooleanVar(value=True)
        self.clean_var = tk.BooleanVar(value=True)
        self.analyze_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            options_frame,
            text="Extract Content & Keywords",
            variable=self.extract_var,
            style="Toggle.TCheckbutton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(
            options_frame,
            text="Clean Data",
            variable=self.clean_var,
            style="Toggle.TCheckbutton"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(
            options_frame,
            text="Analyze Keywords",
            variable=self.analyze_var,
            style="Toggle.TCheckbutton"
        ).pack(side=tk.LEFT, padx=10)
        
        # Progress area
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=600,
            mode='determinate'
        )
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.process_btn = ttk.Button(
            progress_frame,
            text="Start Processing",
            command=self.process_data,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Console output
        console_frame = ttk.LabelFrame(
            main_frame,
            text="Processing Log",
            padding=(10, 5)
        )
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = tk.Text(
            console_frame,
            height=10,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=self.normal_font,
            bg="white",
            fg=self.text_color
        )
        self.console_scroll = ttk.Scrollbar(
            console_frame,
            command=self.console.yview
        )
        self.console.config(yscrollcommand=self.console_scroll.set)
        
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_bar = ttk.Label(
            main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Configure styles
        self.configure_styles()
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.', background=self.bg_color, foreground=self.text_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, font=self.normal_font)
        style.configure('TButton', font=self.button_font)
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', padding=[10, 5], font=self.normal_font)
        
        # Accent button
        style.configure('Accent.TButton', 
                      background=self.accent_color,
                      foreground="white",
                      font=self.button_font)
        style.map('Accent.TButton',
                 background=[('active', self.secondary_color)])
        
        # Toggle buttons
        style.configure('Toggle.TCheckbutton', font=self.normal_font)
        
        # Progress bar
        style.configure("Horizontal.TProgressbar",
                      thickness=20,
                      background=self.accent_color,
                      troughcolor="#e0e0e0")
    
    def setup_url_tab(self, parent):
        ttk.Label(
            parent,
            text="Enter journal base URL:",
            font=self.normal_font
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.url_entry = ttk.Entry(
            parent,
            width=60,
            font=self.normal_font
        )
        self.url_entry.insert(0, CONFIG["download"]["base_url"])
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            parent,
            text="Example: https://example.com/journals/",
            font=Font(family="Segoe UI", size=9),
            foreground="#666666"
        ).pack(anchor=tk.W)
    
    def setup_file_tab(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Select Files",
            command=self.select_files,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Clear Selection",
            command=self.clear_files
        ).pack(side=tk.LEFT)
        
        self.file_list = tk.Listbox(
            parent,
            height=10,
            selectmode=tk.MULTIPLE,
            font=self.normal_font,
            bg="white",
            fg=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=self.file_list.yview
        )
        self.file_list.config(yscrollcommand=scrollbar.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Open Output Folder",
            command=self.open_output_folder,
            accelerator="Ctrl+O"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=self.root.quit,
            accelerator="Alt+F4"
        )
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="Clear Log",
            command=self.clear_log,
            accelerator="Ctrl+L"
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Documentation",
            command=self.show_help,
            accelerator="F1"
        )
        help_menu.add_command(
            label="About",
            command=self.show_about
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Bind shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_output_folder())
        self.root.bind("<Control-l>", lambda e: self.clear_log())
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Academic Files",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("HTML Files", "*.html"),
                ("All Supported Files", ("*.pdf", "*.docx", "*.html")),
                ("All Files", "*.*")
            ]
        )
        self.file_list.delete(0, tk.END)
        for file in files:
            self.file_list.insert(tk.END, file)
    
    def clear_files(self):
        self.file_list.delete(0, tk.END)
    
    def clear_log(self):
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
    
    def open_output_folder(self):
        output_dir = os.path.dirname(CONFIG["extraction"]["output_file"])
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            self.show_error("Folder Not Found", "Output folder doesn't exist yet.")
    
    def show_about(self):
        about_text = (
            "Academic Processor Pro\n"
            "Version 2.1\n\n"
            "A powerful tool for extracting and analyzing academic content\n"
            "© 2023 Research Tools Team"
        )
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        help_url = "https://example.com/help"  # Replace with actual help URL
        webbrowser.open(help_url)
    
    def show_error(self, title, message):
        error_window = tk.Toplevel(self.root)
        error_window.title(title)
        error_window.geometry("500x300")
        error_window.resizable(True, True)
        
        frame = ttk.Frame(error_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(
            frame,
            wrap=tk.WORD,
            font=self.normal_font,
            bg="white",
            fg="#d32f2f"  # Error red color
        )
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.insert(tk.END, message)
        text.config(state=tk.DISABLED)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(error_window)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="OK",
            command=error_window.destroy,
            style="Accent.TButton"
        ).pack()
    
    def log_message(self, message, level="info"):
        tag = level.lower()
        self.console.config(state=tk.NORMAL)
        
        if tag == "error":
            self.console.insert(tk.END, message + "\n", "error")
        else:
            self.console.insert(tk.END, message + "\n")
            
        self.console.config(state=tk.DISABLED)
        self.console.see(tk.END)
        self.root.update()
    
    def update_progress(self, value):
        self.progress['value'] = value
        self.status_bar.config(text=f"Progress: {int(value)}%")
        self.root.update()
    
    def process_data(self):
        try:
            self.process_btn.config(state=tk.DISABLED)
            self.update_progress(0)
            self.status_bar.config(text="Processing...")
            self.log_message("\n=== Starting new processing job ===")
            
            if self.notebook.index(self.notebook.select()) == 0:  # URL tab
                self.process_journal_url()
            else:  # File tab
                self.process_uploaded_files()
            
            self.update_progress(100)
            self.status_bar.config(text="Processing completed successfully!")
            self.log_message("=== Processing completed successfully ===")
            messagebox.showinfo("Success", "Processing completed successfully!")
        
        except Exception as e:
            self.log_message(f"\nERROR: {str(e)}", "error")
            self.show_error("Processing Error", str(e))
            self.status_bar.config(text="Error occurred")
        finally:
            self.process_btn.config(state=tk.NORMAL)
    
    def process_uploaded_files(self):
        raw_dir = CONFIG["download"]["output_dir"]
        os.makedirs(raw_dir, exist_ok=True)
        total_files = self.file_list.size()
        
        if total_files == 0:
            raise ValueError("No files selected for processing")
        
        self.log_message(f"\nCopying {total_files} files to processing directory...")
        
        for i in range(total_files):
            src = self.file_list.get(i)
            filename, ext = os.path.splitext(os.path.basename(src))
            dst = os.path.join(raw_dir, f"uploaded_{i+1}{ext}")
            
            self.log_message(f"Copying: {os.path.basename(src)}")
            with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                f_dst.write(f_src.read())
            
            self.update_progress((i+1)/total_files * 20)
        
        self.run_processing_pipeline()
    
    def process_journal_url(self):
        url = self.url_entry.get().strip()
        if not url:
            raise ValueError("Please enter a valid URL")
        
        CONFIG["download"]["base_url"] = url
        self.log_message(f"\nUsing URL: {url}")
        
        self.log_message("\nDownloading journal issues...")
        download_journal_issues()
        self.update_progress(20)
        
        self.run_processing_pipeline()
    
    def run_processing_pipeline(self):
        if self.extract_var.get():
            self.log_message("\nExtracting content and keywords...")
            self.text_extractor.process_files()
            self.update_progress(40)
        
        if self.clean_var.get():
            self.log_message("\nCleaning data...")
            clean_data()
            self.update_progress(70)
        
        if self.analyze_var.get():
            self.log_message("\nAnalyzing keywords...")
            analyze_keywords()
            self.update_progress(90)
        
        self.log_message("\nFinalizing results...")
        merge_excel_files()
        self.update_progress(100)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernJournalProcessorApp(root)
    
    # Configure console tags for colored text
    app.console.tag_config("error", foreground="#d32f2f")
    app.console.tag_config("warning", foreground="#ffa000")
    app.console.tag_config("success", foreground="#388e3c")
    
    root.mainloop()