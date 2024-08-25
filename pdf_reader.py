import sys
import fitz  # PyMuPDF
import json
import pytesseract
from PIL import Image
import subprocess
import os  # Import the os module
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QLabel, QScrollArea,
    QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QListWidget,
    QInputDialog, QMessageBox, QDockWidget, QListWidgetItem, QColorDialog, QFormLayout, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QIcon, QPen, QBrush, QPalette
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

# Existing PDFViewer class with all your previous code
class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.pdf_document = None
        self.zoom_factor = 1.0  # Initial zoom factor
        self.current_page = 0
        self.search_results = []
        self.current_search_index = -1
        self.bookmarks = {}  # Dictionary to store bookmarks with names
        self.annotations = {}  # Dictionary to store annotations
        self.annotation_mode = None  # Current annotation mode
        self.current_annotation = None  # Temporary storage for the annotation being created
        self.is_night_mode = False  # Night mode flag

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout for central widget
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Search bar and buttons
        self.search_bar_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        self.search_bar_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search", self)
        # self.search_button.clicked.connect(self.search_text)
        self.search_bar_layout.addWidget(self.search_button)
        
        self.next_result_button = QPushButton("Next", self)
        # self.next_result_button.clicked.connect(self.next_search_result)
        self.search_bar_layout.addWidget(self.next_result_button)
        
        self.prev_result_button = QPushButton("Previous", self)
        # self.prev_result_button.clicked.connect(self.prev_search_result)
        self.search_bar_layout.addWidget(self.prev_result_button)
        
        self.main_layout.addLayout(self.search_bar_layout)

        # Scroll area to hold the PDF content
        self.scroll_area = QScrollArea(self)
        self.main_layout.addWidget(self.scroll_area)
        
        # Container widget inside scroll area to hold all page labels
        self.pages_widget = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_widget)
        self.scroll_area.setWidget(self.pages_widget)
        self.scroll_area.setWidgetResizable(True)

        # Create menu bar
        self.create_menu()

        # Dock widget for TOC
        self.toc_dock = QDockWidget("Table of Contents", self)
        self.toc_list_widget = QListWidget()
        self.toc_dock.setWidget(self.toc_list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.setVisible(False)
        self.toc_list_widget.itemClicked.connect(self.toc_item_clicked)

        # Dock widget for thumbnails
        self.thumbnail_dock = QDockWidget("Thumbnails", self)
        self.thumbnail_list_widget = QListWidget()
        self.thumbnail_list_widget.setIconSize(QSize(100, 150))  # Set icon size for thumbnails
        self.thumbnail_dock.setWidget(self.thumbnail_list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.thumbnail_dock)
        self.thumbnail_dock.setVisible(False)
        self.thumbnail_list_widget.itemClicked.connect(self.thumbnail_item_clicked)

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

    def create_menu(self):
        # Create the menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open action
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Print PDF action
        print_action = QAction('Print PDF', self)
        print_action.triggered.connect(self.print_pdf)
        file_menu.addAction(print_action)

        # Close PDF action
        close_action = QAction('Close PDF', self)
        close_action.triggered.connect(self.close_pdf)
        file_menu.addAction(close_action)
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        # Undo action
        undo_action = QAction('Undo', self)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        # Redo action
        redo_action = QAction('Redo', self)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        # View/Edit Metadata action
        metadata_action = QAction('View/Edit Metadata', self)
        metadata_action.triggered.connect(self.view_edit_metadata)
        edit_menu.addAction(metadata_action)
        
        # Rotate Page action
        rotate_page_action = QAction('Rotate Page', self)
        rotate_page_action.triggered.connect(self.rotate_current_page)
        edit_menu.addAction(rotate_page_action)
        
        # Rotate All Pages action
        rotate_all_pages_action = QAction('Rotate All Pages', self)
        rotate_all_pages_action.triggered.connect(self.rotate_all_pages)
        edit_menu.addAction(rotate_all_pages_action)
        
        # Split PDF action
        split_action = QAction('Split PDF', self)
        split_action.triggered.connect(self.split_pdf)
        edit_menu.addAction(split_action)
        
        # Merge PDFs action
        merge_action = QAction('Merge PDFs', self)
        merge_action.triggered.connect(self.merge_pdfs)
        edit_menu.addAction(merge_action)

        # View menu (formerly Zoom)
        view_menu = menubar.addMenu('View')
        
        # Zoom In action
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        # Zoom Out action
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        # Night Mode action
        night_mode_action = QAction('Toggle Night Mode', self)
        night_mode_action.triggered.connect(self.toggle_night_mode)
        view_menu.addAction(night_mode_action)

        # Bookmark menu
        bookmark_menu = menubar.addMenu('Bookmark')
        
        # Add Bookmark action
        add_bookmark_action = QAction('Add Bookmark', self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmark_menu.addAction(add_bookmark_action)
        
        # View Bookmarks action
        view_bookmarks_action = QAction('View Bookmarks', self)
        view_bookmarks_action.triggered.connect(self.view_bookmarks)
        bookmark_menu.addAction(view_bookmarks_action)

        # TOC menu
        toc_menu = menubar.addMenu('TOC')
        
        # View TOC action
        view_toc_action = QAction('View Table of Contents', self)
        view_toc_action.triggered.connect(self.toggle_toc)
        toc_menu.addAction(view_toc_action)

        # Thumbnail menu
        thumbnail_menu = menubar.addMenu('Thumbnails')
        
        # View Thumbnails action
        view_thumbnails_action = QAction('View Thumbnails', self)
        view_thumbnails_action.triggered.connect(self.toggle_thumbnails)
        thumbnail_menu.addAction(view_thumbnails_action)

        # OCR menu (Newly added)
        ocr_menu = menubar.addMenu('OCR')
        
        # Convert PDF to LibreOffice action
        convert_pdf_to_odt_action = QAction('Convert PDF to LibreOffice', self)
        convert_pdf_to_odt_action.triggered.connect(self.convert_pdf_to_odt)
        ocr_menu.addAction(convert_pdf_to_odt_action)

        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        """Show the About dialog with application information."""
        QMessageBox.about(self, "About My Python PDF Viewer",
                          "Application Name: My Python PDF Viewer\n"
                          "Version: 1.9\n"
                          "Developer: Developed by Dr. Eric O. Flores\n"
                          "Description: A simple PDF viewer with annotation, search, and bookmarking features.\n"
                          "License: GNU General Public License v3.0\n"
                          "Copyright: ©2024 Dr. Eric O. Flores.\n"
                          "Contact: eoftoro@gmail.com\n\n"
                          "This software is licensed under the GNU General Public License v3.0. You may redistribute "
                          "and/or modify this software under the terms of the GNU General Public License as published by "
                          "the Free Software Foundation, either version 3 of the License, or (at your option) any later "
                          "version.\n"
                          "For more details, see the full license at: https://www.gnu.org/licenses/gpl-3.0.en.html")

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        self.pdf_document = fitz.open(file_path)
        self.display_all_pages()
        self.load_toc()
        self.load_thumbnails()

    def close_pdf(self):
        """Close the current PDF and clear the display."""
        self.pdf_document = None
        self.search_results.clear()
        self.current_search_index = -1
        self.bookmarks.clear()
        self.annotations.clear()
        self.toc_list_widget.clear()
        self.thumbnail_list_widget.clear()
        for i in reversed(range(self.pages_layout.count())):
            widget = self.pages_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.setWindowTitle("PDF Viewer")
        self.toc_dock.setVisible(False)
        self.thumbnail_dock.setVisible(False)

    def display_all_pages(self):
        """Render and display all pages of the PDF document."""
        if self.pdf_document:
            # Clear the current layout
            for i in reversed(range(self.pages_layout.count())):
                widget = self.pages_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
            
            # Render each page and add to layout
            for page_number in range(len(self.pdf_document)):
                pixmap = self.render_page(page_number)
                page_label = QLabel(self)
                page_label.setPixmap(pixmap)
                page_label.mousePressEvent = lambda event, p=page_number: self.page_mouse_press(event, p)
                page_label.mouseMoveEvent = lambda event, p=page_number: self.page_mouse_move(event, p)
                page_label.mouseReleaseEvent = lambda event, p=page_number: self.page_mouse_release(event, p)
                self.pages_layout.addWidget(page_label)

    def render_page(self, page_number, highlight_rects=None):
        """Render a page as a QPixmap, with optional highlighted areas."""
        page = self.pdf_document.load_page(page_number)
        mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=mat)
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888 if pix.n == 3 else QImage.Format_RGBA8888)

        if highlight_rects:
            painter = QPainter(image)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 0, 100))  # Yellow with transparency
            for rect in highlight_rects:
                painter.drawRect(rect)
            painter.end()

        # Draw annotations on the page
        if page_number in self.annotations:
            painter = QPainter(image)
            for annotation in self.annotations[page_number]:
                annotation_type, data = annotation
                if annotation_type == 'highlight':
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(255, 255, 0, 100))  # Yellow with transparency
                    painter.drawRect(data)
                elif annotation_type == 'rectangle':
                    painter.setPen(QPen(QColor(0, 0, 255), 3, Qt.SolidLine))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(data)
                elif annotation_type == 'text_note':
                    painter.setPen(QPen(QColor(0, 0, 0)))
                    painter.drawText(data['pos'], data['text'])
            painter.end()

        return QPixmap.fromImage(image)

    def render_thumbnail(self, page_number):
        """Render a thumbnail for a specific page."""
        page = self.pdf_document.load_page(page_number)
        zoom = 0.2  # Thumbnail zoom factor (adjust for desired thumbnail size)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888 if pix.n == 3 else QImage.Format_RGBA8888)
        return QPixmap.fromImage(image)

    def add_bookmark(self):
        """Add a bookmark for the current page."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        current_page = self.scroll_area.verticalScrollBar().value()  # Get the current page based on scroll position
        name, ok = QInputDialog.getText(self, "Add Bookmark", "Enter a name for the bookmark:")

        if ok and name:
            self.bookmarks[name] = current_page
            QMessageBox.information(self, "Bookmark Added", f"Bookmark '{name}' added for page {current_page + 1}.")

    def view_bookmarks(self):
        """View and navigate to bookmarks."""
        if not self.bookmarks:
            QMessageBox.information(self, "No Bookmarks", "There are no bookmarks added.")
            return

        dialog = QInputDialog(self)
        dialog.setComboBoxItems(list(self.bookmarks.keys()))
        dialog.setWindowTitle("View Bookmarks")
        dialog.setLabelText("Select a bookmark to go to:")

        if dialog.exec_() == QInputDialog.Accepted:
            bookmark_name = dialog.textValue()
            if bookmark_name in self.bookmarks:
                page_number = self.bookmarks[bookmark_name]
                self.scroll_area.verticalScrollBar().setValue(page_number)
                QMessageBox.information(self, "Bookmark", f"Navigated to bookmark '{bookmark_name}' on page {page_number + 1}.")

    def load_toc(self):
        """Load the Table of Contents (TOC) from the PDF."""
        if not self.pdf_document:
            return
        
        toc = self.pdf_document.get_toc()  # Get the TOC as a list of tuples
        if toc:
            self.toc_list_widget.clear()
            for level, title, page in toc:
                item_text = f"{'  ' * (level - 1)}{title}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, page - 1)  # Store the page number (0-indexed)
                self.toc_list_widget.addItem(item)
            self.toc_dock.setVisible(True)
        else:
            QMessageBox.information(self, "No Table of Contents", "This PDF does not contain a table of contents.")

    def load_thumbnails(self):
        """Generate and display thumbnails for each page."""
        if not self.pdf_document:
            return

        self.thumbnail_list_widget.clear()
        for page_number in range(len(self.pdf_document)):
            thumbnail_pixmap = self.render_thumbnail(page_number)
            item = QListWidgetItem(QIcon(thumbnail_pixmap), f"Page {page_number + 1}")
            item.setData(Qt.UserRole, page_number)
            self.thumbnail_list_widget.addItem(item)
        self.thumbnail_dock.setVisible(True)

    def toc_item_clicked(self, item):
        """Navigate to the page corresponding to the clicked TOC item."""
        page_number = item.data(Qt.UserRole)
        self.scroll_to_page(page_number)

    def thumbnail_item_clicked(self, item):
        """Navigate to the page corresponding to the clicked thumbnail."""
        page_number = item.data(Qt.UserRole)
        self.scroll_to_page(page_number)

    def scroll_to_page(self, page_number):
        """Scroll to the specified page number."""
        label = self.pages_layout.itemAt(page_number).widget()
        if label:
            self.scroll_area.ensureWidgetVisible(label)

    def toggle_toc(self):
        """Toggle the visibility of the TOC dock."""
        self.toc_dock.setVisible(not self.toc_dock.isVisible())

    def toggle_thumbnails(self):
        """Toggle the visibility of the Thumbnails dock."""
        self.thumbnail_dock.setVisible(not self.thumbnail_dock.isVisible())

    def activate_highlight_mode(self):
        """Activate the highlight annotation mode."""
        self.annotation_mode = 'highlight'

    def activate_draw_rect_mode(self):
        """Activate the draw rectangle annotation mode."""
        self.annotation_mode = 'rectangle'

    def activate_text_note_mode(self):
        """Activate the text note annotation mode."""
        self.annotation_mode = 'text_note'

    def page_mouse_press(self, event, page_number):
        """Handle mouse press events for annotations."""
        if self.annotation_mode == 'highlight' or self.annotation_mode == 'rectangle':
            self.current_annotation = QRect(event.pos(), event.pos())
        elif self.annotation_mode == 'text_note':
            text, ok = QInputDialog.getText(self, "Add Text Note", "Enter your note:")
            if ok and text:
                self.current_annotation = {'pos': event.pos(), 'text': text}
                if page_number not in self.annotations:
                    self.annotations[page_number] = []
                self.annotations[page_number].append((self.annotation_mode, self.current_annotation))
                self.display_all_pages()

    def page_mouse_move(self, event, page_number):
        """Handle mouse move events for annotations."""
        if self.annotation_mode and self.current_annotation and isinstance(self.current_annotation, QRect):
            self.current_annotation.setBottomRight(event.pos())
            self.display_all_pages()

    def page_mouse_release(self, event, page_number):
        """Handle mouse release events for annotations."""
        if self.annotation_mode and self.current_annotation:
            if page_number not in self.annotations:
                self.annotations[page_number] = []
            self.annotations[page_number].append((self.annotation_mode, self.current_annotation))
            self.current_annotation = None
            self.display_all_pages()

    def zoom_in(self):
        """Increase the zoom factor and redisplay all pages."""
        self.zoom_factor += 0.1
        self.display_all_pages()

    def zoom_out(self):
        """Decrease the zoom factor and redisplay all pages."""
        if self.zoom_factor > 0.1:  # Ensure zoom factor doesn't go below a reasonable value
            self.zoom_factor -= 0.1
            self.display_all_pages()

    def enable_scroll(self):
        """Enable scrolling in the scroll area."""
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def disable_scroll(self):
        """Disable scrolling in the scroll area."""
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def export_annotations(self):
        """Export the annotations to a JSON file."""
        if not self.annotations:
            QMessageBox.information(self, "No Annotations", "There are no annotations to export.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Annotations", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            # Prepare annotations data for export
            export_data = {}
            for page_number, annots in self.annotations.items():
                export_data[page_number] = []
                for annotation_type, data in annots:
                    if annotation_type == 'highlight' or annotation_type == 'rectangle':
                        export_data[page_number].append({
                            'type': annotation_type,
                            'x': data.x(),
                            'y': data.y(),
                            'width': data.width(),
                            'height': data.height()
                        })
                    elif annotation_type == 'text_note':
                        export_data[page_number].append({
                            'type': annotation_type,
                            'pos': {'x': data['pos'].x(), 'y': data['pos'].y()},
                            'text': data['text']
                        })

            # Write the annotations to a JSON file
            with open(file_path, 'w') as json_file:
                json.dump(export_data, json_file, indent=4)

            QMessageBox.information(self, "Export Successful", f"Annotations exported successfully to {file_path}.")

    def split_pdf(self):
        """Split the current PDF into parts based on user-defined page ranges."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        # Get the page ranges from the user
        page_ranges, ok = QInputDialog.getText(self, "Split PDF", "Enter page ranges (e.g., 1-3, 5-7):")
        if ok and page_ranges:
            try:
                ranges = self.parse_page_ranges(page_ranges)
                options = QFileDialog.Options()
                output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)

                if output_dir:
                    for idx, (start, end) in enumerate(ranges):
                        output_path = f"{output_dir}/split_part_{idx + 1}.pdf"
                        doc = fitz.open()
                        for page_num in range(start, end + 1):
                            doc.insert_pdf(self.pdf_document, from_page=page_num, to_page=page_num)
                        doc.save(output_path)
                        doc.close()

                    QMessageBox.information(self, "Split Successful", f"PDF split successfully and saved in {output_dir}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while splitting the PDF: {e}")

    def parse_page_ranges(self, page_ranges):
        """Parse the page ranges input by the user."""
        ranges = []
        for part in page_ranges.split(','):
            start, end = map(int, part.split('-'))
            ranges.append((start - 1, end - 1))  # Adjust for 0-based indexing
        return ranges

    def merge_pdfs(self):
        """Merge multiple PDFs into a single document."""
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs to Merge", "", "PDF Files (*.pdf);;All Files (*)", options=options)

        if files:
            try:
                output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf);;All Files (*)", options=options)
                if output_path:
                    output_pdf = fitz.open()
                    for file in files:
                        doc = fitz.open(file)
                        output_pdf.insert_pdf(doc)
                        doc.close()

                    output_pdf.save(output_path)
                    output_pdf.close()

                    QMessageBox.information(self, "Merge Successful", f"PDFs merged successfully into {output_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while merging the PDFs: {e}")

    def rotate_current_page(self):
        """Rotate the current page 90 degrees clockwise."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        try:
            # Rotate the current page
            self.pdf_document.load_page(self.current_page).set_rotation(90)
            self.pdf_document.saveIncr()  # Save the rotation incrementally
            self.display_all_pages()
            QMessageBox.information(self, "Rotate Successful", f"Page {self.current_page + 1} rotated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while rotating the page: {e}")

    def rotate_all_pages(self):
        """Rotate all pages in the PDF 90 degrees clockwise."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        try:
            for page_num in range(len(self.pdf_document)):
                self.pdf_document.load_page(page_num).set_rotation(90)
            self.pdf_document.saveIncr()  # Save the rotation incrementally
            self.display_all_pages()
            QMessageBox.information(self, "Rotate Successful", "All pages rotated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while rotating the pages: {e}")

    def view_edit_metadata(self):
        """View and edit PDF metadata."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        # Get current metadata
        metadata = self.pdf_document.metadata

        # Create a form layout to display and edit metadata
        form_layout = QFormLayout()

        title_input = QLineEdit(metadata.get('title', ''))
        author_input = QLineEdit(metadata.get('author', ''))
        subject_input = QLineEdit(metadata.get('subject', ''))
        keywords_input = QLineEdit(metadata.get('keywords', ''))

        form_layout.addRow('Title:', title_input)
        form_layout.addRow('Author:', author_input)
        form_layout.addRow('Subject:', subject_input)
        form_layout.addRow('Keywords:', keywords_input)

        dialog = QDialog(self)
        dialog.setWindowTitle("View/Edit Metadata")
        dialog.setLayout(form_layout)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_metadata(title_input.text(), author_input.text(), subject_input.text(), keywords_input.text(), dialog))
        form_layout.addWidget(save_button)

        dialog.exec_()

    def save_metadata(self, title, author, subject, keywords, dialog):
        """Save the edited metadata back to the PDF."""
        try:
            # Set new metadata
            self.pdf_document.set_metadata({
                'title': title,
                'author': author,
                'subject': subject,
                'keywords': keywords
            })
            self.pdf_document.saveIncr()  # Save changes incrementally
            QMessageBox.information(self, "Save Successful", "Metadata updated successfully.")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving metadata: {e}")

    def print_pdf(self):
        """Print the currently opened PDF."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        try:
            printer = QPrinter(QPrinter.HighResolution)
            print_dialog = QPrintDialog(printer, self)

            if print_dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)

                for page_num in range(len(self.pdf_document)):
                    page = self.pdf_document.load_page(page_num)
                    mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
                    pix = page.get_pixmap(matrix=mat)
                    image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888 if pix.n == 3 else QImage.Format_RGBA8888)
                    rect = painter.viewport()
                    size = image.size()
                    size.scale(rect.size(), Qt.KeepAspectRatio)

                    painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                    painter.setWindow(image.rect())
                    painter.drawImage(0, 0, image)

                    if page_num < len(self.pdf_document) - 1:
                        printer.newPage()

                painter.end()
                QMessageBox.information(self, "Print Successful", "The document was printed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while printing the document: {e}")

    def toggle_night_mode(self):
        """Toggle between Night Mode and Normal Mode."""
        if self.is_night_mode:
            # Switch to normal mode
            self.setPalette(QApplication.style().standardPalette())
        else:
            # Switch to night mode
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)

        self.is_night_mode = not self.is_night_mode

    def undo(self):
        """Undo the last action."""
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action)
            # Implement undo logic based on the type of action
            self.display_all_pages()

    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            # Implement redo logic based on the type of action
            self.display_all_pages()

    def convert_pdf_to_odt(self):
        """Convert the currently open PDF to LibreOffice .odt format using OCR."""
        if not self.pdf_document:
            QMessageBox.warning(self, "No PDF Opened", "Please open a PDF file first.")
            return

        odt_output_path, _ = QFileDialog.getSaveFileName(self, "Save as LibreOffice ODT", "", "LibreOffice ODT Files (*.odt);;All Files (*)")
        if odt_output_path:
            try:
                # Perform OCR on the currently open PDF
                text = self.perform_ocr_on_open_pdf()
                # Convert the extracted text to LibreOffice ODT format
                self.save_text_as_odt(text, odt_output_path)
                QMessageBox.information(self, "Conversion Successful", f"PDF converted to LibreOffice ODT successfully and saved at {odt_output_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred during the conversion: {e}")

    def perform_ocr_on_open_pdf(self):
        """Perform OCR on the currently open PDF and extract the text."""
        text = ""
        for page_num in range(len(self.pdf_document)):
            page = self.pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img)
        return text

    def save_text_as_odt(self, text, odt_output_path):
        """Save extracted text as an ODT file using unoconv."""
        temp_txt_path = "temp_output.txt"
        with open(temp_txt_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(text)

        subprocess.run(['unoconv', '-f', 'odt', temp_txt_path])

        generated_odt = temp_txt_path.replace(".txt", ".odt")
        if os.path.exists(generated_odt):
            os.rename(generated_odt, odt_output_path)

        os.remove(temp_txt_path)

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


