import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                            QTabWidget, QListWidget, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent, QColor, QPalette
from tobbestEgyesbe import process_pdfs, process_urls, TextAnalyzer

class PDFProcessorThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, pdf_files, output_file):
        super().__init__()
        self.pdf_files = pdf_files
        self.output_file = output_file
        
    def run(self):
        try:
            success = process_pdfs(self.pdf_files, self.output_file)
            self.finished.emit(success)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(False)

class URLProcessorThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, urls, output_file):
        super().__init__()
        self.urls = urls
        self.output_file = output_file
        
    def run(self):
        try:
            success = process_urls(self.urls, self.output_file)
            self.finished.emit(success)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(False)

class DragDropListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #F5F7FA;
                border: 2px dashed #C1C7D0;
                border-radius: 8px;
                padding: 16px;
                font-size: 14px;
                color: #5E6C84;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #DFE1E6;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file in files:
            if file.lower().endswith('.pdf'):
                self.addItem(file)
            else:
                QMessageBox.warning(self, "Invalid File", 
                                  f"{file} is not a PDF file.")

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A6FA5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #3A5A8F;
            }
            QPushButton:pressed {
                background-color: #2A4A7F;
            }
            QPushButton:disabled {
                background-color: #CCD4E0;
                color: #7A869A;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Processor Professor")
        self.setMinimumSize(900, 700)
        
        # Set application palette for dark theme
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 241, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(23, 43, 77))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 241, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(23, 43, 77))
        palette.setColor(QPalette.ColorRole.Text, QColor(23, 43, 77))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 241, 245))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(23, 43, 77))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(64, 112, 192))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        QApplication.setPalette(palette)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("PDF Abstract Processor")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #172B4D;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Subheader
        subheader = QLabel("Extract and analyze text from PDF files or URLs")
        subheader.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #5E6C84;
                padding-bottom: 20px;
            }
        """)
        layout.addWidget(subheader)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #DFE1E6;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #F5F7FA;
                border: 1px solid #DFE1E6;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #5E6C84;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4A6FA5;
                color: #172B4D;
            }
            QTabBar::tab:hover {
                background: #EBECF0;
            }
        """)
        layout.addWidget(tabs)
        
        # Create tabs
        local_tab = self.create_local_tab()
        url_tab = self.create_url_tab()
        
        # Add tabs to widget
        tabs.addTab(local_tab, "Local PDFs")
        tabs.addTab(url_tab, "URLs")
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #F5F7FA;
                color: #5E6C84;
                border-top: 1px solid #DFE1E6;
                padding: 4px;
            }
        """)
        self.statusBar().showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #DFE1E6;
                border-radius: 4px;
                text-align: center;
                background: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4A6FA5;
                width: 10px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Log area
        log_label = QLabel("Processing Log:")
        log_label.setStyleSheet("font-weight: 600; color: #172B4D;")
        layout.addWidget(log_label)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #DFE1E6;
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
                color: #172B4D;
            }
        """)
        layout.addWidget(self.log_area)
        
        # Initialize processor threads
        self.pdf_processor = None
        self.url_processor = None
        
    def create_local_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # File list
        label = QLabel("Drag and drop PDF files here or use the button below:")
        label.setStyleSheet("color: #5E6C84;")
        layout.addWidget(label)
        
        self.file_list = DragDropListWidget()
        self.file_list.setMinimumHeight(200)
        layout.addWidget(self.file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = ModernButton("Add PDFs")
        add_button.clicked.connect(self.add_pdfs)
        button_layout.addWidget(add_button)
        
        remove_button = ModernButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_button)
        
        clear_button = ModernButton("Clear All")
        clear_button.clicked.connect(self.file_list.clear)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Process button
        process_button = ModernButton("Process PDFs")
        process_button.clicked.connect(self.process_local_pdfs)
        process_button.setStyleSheet("background-color: #5AAC44;")
        process_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        return widget
        
    def create_url_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter PDF URL (e.g., https://example.com/document.pdf)")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #DFE1E6;
                border-radius: 6px;
                background: white;
            }
        """)
        url_layout.addWidget(self.url_input)
        
        add_url_button = ModernButton("Add URL")
        add_url_button.clicked.connect(self.add_url)
        url_layout.addWidget(add_url_button)
        
        layout.addLayout(url_layout)
        
        # URL list
        label = QLabel("URLs to process:")
        label.setStyleSheet("color: #5E6C84;")
        layout.addWidget(label)
        
        self.url_list = QListWidget()
        self.url_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #DFE1E6;
                border-radius: 6px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #DFE1E6;
            }
        """)
        self.url_list.setMinimumHeight(150)
        layout.addWidget(self.url_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        remove_url_button = ModernButton("Remove Selected")
        remove_url_button.clicked.connect(self.remove_selected_url)
        button_layout.addWidget(remove_url_button)
        
        clear_urls_button = ModernButton("Clear All")
        clear_urls_button.clicked.connect(self.url_list.clear)
        button_layout.addWidget(clear_urls_button)
        
        layout.addLayout(button_layout)
        
        # Process button
        process_button = ModernButton("Process URLs")
        process_button.clicked.connect(self.process_urls)
        process_button.setStyleSheet("background-color: #5AAC44;")
        process_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(process_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        return widget
        
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for file in files:
            self.file_list.addItem(file)
            
    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            if url.lower().endswith('.pdf'):
                self.url_list.addItem(url)
                self.url_input.clear()
            else:
                QMessageBox.warning(self, "Invalid URL", 
                                  "URL must point to a PDF file.")
                
    def remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
            
    def remove_selected_url(self):
        for item in self.url_list.selectedItems():
            self.url_list.takeItem(self.url_list.row(item))
            
    def process_local_pdfs(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", 
                              "Please add PDF files to process.")
            return
            
        files = [self.file_list.item(i).text() 
                for i in range(self.file_list.count())]
        
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "Excel Files (*.xlsx)")
            
        if output_file:
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self.pdf_processor = PDFProcessorThread(files, output_file)
            self.pdf_processor.progress.connect(self.update_log)
            self.pdf_processor.finished.connect(self.processing_finished)
            self.pdf_processor.start()
            
    def process_urls(self):
        if self.url_list.count() == 0:
            QMessageBox.warning(self, "No URLs", 
                              "Please add URLs to process.")
            return
            
        urls = [self.url_list.item(i).text() 
                for i in range(self.url_list.count())]
        
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "Excel Files (*.xlsx)")
            
        if output_file:
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self.url_processor = URLProcessorThread(urls, output_file)
            self.url_processor.progress.connect(self.update_log)
            self.url_processor.finished.connect(self.processing_finished)
            self.url_processor.start()
            
    def update_log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum())
            
    def processing_finished(self, success):
        self.progress_bar.hide()
        if success:
            QMessageBox.information(self, "Success", 
                                  "Processing completed successfully!")
        else:
            QMessageBox.warning(self, "Error", 
                              "An error occurred during processing.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())