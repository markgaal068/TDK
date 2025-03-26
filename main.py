import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                            QTabWidget, QListWidget, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent
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
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Abstract Processor")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create tabs
        local_tab = self.create_local_tab()
        url_tab = self.create_url_tab()
        
        # Add tabs to widget
        tabs.addTab(local_tab, "Local PDFs")
        tabs.addTab(url_tab, "URLs")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        layout.addWidget(self.log_area)
        
        # Initialize processor threads
        self.pdf_processor = None
        self.url_processor = None
        
    def create_local_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # File list
        self.file_list = DragDropListWidget()
        layout.addWidget(QLabel("Drag and drop PDF files here or use the button below:"))
        layout.addWidget(self.file_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
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
        layout.addWidget(process_button)
        
        return widget
        
    def create_url_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # URL input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter PDF URL")
        url_layout.addWidget(self.url_input)
        
        add_url_button = ModernButton("Add URL")
        add_url_button.clicked.connect(self.add_url)
        url_layout.addWidget(add_url_button)
        
        layout.addLayout(url_layout)
        
        # URL list
        self.url_list = QListWidget()
        layout.addWidget(QLabel("URLs to process:"))
        layout.addWidget(self.url_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
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
        layout.addWidget(process_button)
        
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
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec()) 