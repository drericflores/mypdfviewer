# mypdfviewer
A PDF viewer 

Application Specification and User Manual for the 
"My Python PDF Viewer" 

Note:  This PDF Viewer is a work in progress.

Application Specification

Note: This documentation provides a complete overview of the ‘My Python PDF Viewer application’, including its features, usage, and technical specifications. By following this guide, users should be able to effectively utilize the application for their PDF viewing and editing needs. 

1. Overview
    • Application Name: My Python PDF Viewer
    • Version: 1.10
    • Developer: Dr. Eric O. Flores
    • Project Start Date: August 11, 2024
    • Programming Language: Python 3
    • Framework: PyQt5, PyMuPDF (for PDF manipulation)
    • License: GNU General Public License v3.0
    • Description: My Python PDF Viewer is a lightweight and intuitive PDF viewer with advanced features such as annotation, search, bookmarking, and more. It is designed to provide users with a comprehensive tool for viewing, editing, and managing PDF documents.

2. Features
The application incorporates a broad range of features, categorized as follows:
Core Features:
    • PDF Viewing: Load and display PDF documents with multiple pages.
    • Zooming: Users can zoom in and out of pages.
    • Search: Allows searching for text within the PDF and navigating between search results.
    • Bookmarks: Users can bookmark pages for quick access.
    • Annotations: Add highlights, text notes, and drawings to PDF pages.
    • Thumbnails: Provides a thumbnail view for easy navigation through pages.
    • Table of Contents (TOC): Extracts and displays the TOC, allowing quick navigation.
    • Night Mode: Switches the viewer to a night mode for comfortable reading in low light.
Advanced Features:
    • Split and Merge PDFs: Split a PDF into parts or merge multiple PDFs into one.
    • PDF Metadata Viewer/Editor: View and edit PDF metadata, such as the author, title, and keywords.
    • Rotate Pages: Rotate individual pages or the entire document.
    • OCR Functionality: Convert scanned PDFs to editable text, with an option to export the content to LibreOffice .odt format.
    • Export Annotations: Export user-added annotations to a text file or embed them into the PDF.
    • Print PDF: Print the currently opened PDF.
    • Password Protection: Set or remove passwords on PDF files.
3. Implementation Considerations
    • Performance: Focus on optimizing the application for handling large PDFs and multiple open documents.
    • Cross-Platform Support: Ensure the application works seamlessly across Windows, macOS, and Linux.
    • User Experience: Prioritize an intuitive and user-friendly interface, making advanced features easily accessible.

User Manual

1. Getting Started
Installation:
    • Download and install the required dependencies: Python 3, PyQt5, PyMuPDF, and any other libraries mentioned in the requirements.txt file.
    • Run the application using the command python pdf_viewer.py in your terminal or command prompt.
Launching the Application:
    • Upon launching, the application opens with a clean interface where you can load PDF files via the "File" menu.
2. User Interface Overview
    • Menu Bar: Located at the top, providing access to all functions such as file operations, editing, viewing, and more.
    • Main Viewing Area: Displays the currently loaded PDF with navigation controls, such as zoom and page navigation.
    • Side Panels: Includes TOC, thumbnails, and bookmarks for enhanced navigation.
3. Core Functionality
Opening a PDF:
    • Go to the "File" menu and select "Open". Browse and select the desired PDF file.
Navigating Through a PDF:
    • Use the scroll wheel, scrollbar, or the thumbnail sidebar to move between pages.
Zooming In/Out:
    • Use the "View" menu to zoom in or out. You can also use keyboard shortcuts Ctrl + and Ctrl -.
Searching for Text:
    • Enter the text in the search bar located above the main viewing area and press "Search". Use "Next" and "Previous" to navigate between results.
Adding Annotations:
    • Select the annotation tool (highlight, rectangle, text note) from the toolbar. Click and drag on the PDF to create an annotation.
Bookmarking Pages:
    • Add bookmarks by selecting "Add Bookmark" from the "Bookmark" menu. View and navigate bookmarks from the same menu.
4. Advanced Features
Using the OCR Feature:
    • To convert a scanned PDF to editable text, go to the "OCR" menu and select "Convert PDF to LibreOffice". The text will be extracted and saved in .odt format.
Splitting and Merging PDFs:
    • Access the "Split PDF" and "Merge PDFs" options from the "File" menu. Follow the prompts to select pages or files and complete the operation.
Editing Metadata:
    • View and edit metadata by selecting "View/Edit Metadata" from the "Edit" menu. This allows you to update information such as the title, author, and keywords of the PDF.
Printing a PDF:
    • Print the document directly from the application by selecting "Print PDF" from the "File" menu.
Password Protection:
    • Add or remove a password from a PDF by selecting the appropriate option under the "File" menu.
5. Customization
Night Mode:
    • Switch between normal and night mode by toggling the "Night Mode" option in the "View" menu.
Toolbar Customization:
    • Customize the toolbar by dragging and dropping icons to rearrange them, or go to the "View" menu to add or remove tools.
6. Troubleshooting
    • Slow Performance: If the application becomes slow, especially with large files, try closing other programs or reducing the number of open PDFs.
    • OCR Issues: Ensure the PDF is of high enough quality for OCR to work effectively. Poorly scanned documents may yield inaccurate results.
7. Contact and Support
For support or to report issues, please contact Dr. Eric O. Flores at eoftoro@gmail.com.
