'''
this is a working version,
with ChatGPT, in an interactiev way
'''

'''
refresh this conversation

write a rich document editor which can have embedded attachments which with python: 
- use QSplitter to split the main window into two panes: top, bottom
    - list embedded files in the bottom pane
- use QSplitter to split the top pane into two panes: left, right
    - set the right pane as QTextEdit
    - user can edit the document with markdown syntax in the left pane
    - automatically show the rendered web page of the document in the right pane 
- has a menu item to to open existing document
- has a menu item to save the document

directly give me the complete code
'''

import os 
os.environ["DISPLAY"] = "10.33.72.34:0.0"


import sys
import os
import markdown
import base64
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QListWidget, QAction, QFileDialog, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class RichDocumentEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.file_content = {}
        self.file_name = {}

    def initUI(self):
        self.setWindowTitle('Rich Document Editor')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('icon.png'))

        self.splitter_main = QSplitter(Qt.Vertical)
        self.splitter_main.setHandleWidth(1)

        self.splitter_top = QSplitter(Qt.Horizontal)
        self.splitter_top.setHandleWidth(1)

        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self.updatePreview)

        self.preview = QTextEdit(self)
        self.preview.setReadOnly(True)

        self.splitter_top.addWidget(self.text_edit)
        self.splitter_top.addWidget(self.preview)

        self.splitter_main.addWidget(self.splitter_top)

        self.list_widget = QListWidget(self)

        self.splitter_main.addWidget(self.list_widget)
        self.splitter_main.setSizes([400, 200])

        self.setCentralWidget(self.splitter_main)

        self.createActions()
        self.createMenus()

        self.attachments = []

    def createActions(self):
        self.openAction = QAction(QIcon('open.png'), 'Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.openDocument)

        self.saveAction = QAction(QIcon('save.png'), 'Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.saveDocument)

        self.addAttachmentAction = QAction(QIcon('attachment.png'), 'Add Attachment', self)
        self.addAttachmentAction.setShortcut('Ctrl+A')
        self.addAttachmentAction.triggered.connect(self.addAttachment)

    def createMenus(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.addAttachmentAction)

    def openDocument(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Document', '', 'Markdown Files (*.md)')
        if filename:
            with open(filename, 'r') as file:
                content = file.read()
                self.text_edit.setPlainText(content)
                self.attachments = self.extractAttachments(content)
                self.updateAttachmentList()

    def saveDocument(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Document', '', 'Markdown Files (*.md)')
        if filename:
            content = self.text_edit.toPlainText()
            content_with_attachments = self.embedAttachments(content)
            with open(filename, 'w') as file:
                file.write(content_with_attachments)

    def addAttachment(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, 'Add Attachment', '', 'All Files (*)')
        if filenames:
            for filename in filenames:
                self.attachments.append(filename)
                item = QListWidgetItem(os.path.basename(filename))
                item.setData(Qt.UserRole, filename)
                self.list_widget.addItem(item)

                with open(filename, 'rb') as file:
                    data = file.read()
                    encoded_data = base64.b64encode(data).decode('utf-8')
                    fname = os.path.basename(filename)
                    embedded_image = f'![attachment:{fname}](data:image/png;base64,{encoded_data})'
                    self.file_content[fname] = embedded_image
                    self.file_name[fname] = fname

                # attachment_reference = f'![attachment:{os.path.basename(filename)}]'
                # self.text_edit.insertPlainText(attachment_reference)



    def updatePreview(self):
        markdown_text = self.text_edit.toPlainText()
        html = markdown.markdown(markdown_text)
        for key in self.file_content.keys():
            str_to_replace = ':/' + key
            html = html.replace(str_to_replace, self.file_content[key][len(f'![attachment:'+key+']')+1:-1])
        self.preview.setHtml(html)

    def extractAttachments(self, content):
        new_content = ''
        lines = content.split('\n')
        attachments = []
        for line in lines:
            if line.startswith('![attachment:'):
                # filename = line[12:-1]
                filename = line[13:line.find(']')]
                attachments.append(filename)
                self.file_content[filename] = line
                self.file_name[filename] = filename
            else:
                new_content += line + '\n'

        self.text_edit.setPlainText(new_content)
        return attachments

    def updateAttachmentList(self):
        self.list_widget.clear()
        # for filename in self.attachments:
        for filename in self.file_content.keys():
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, filename)
            self.list_widget.addItem(item)

    def embedAttachments(self, content):
        # for attachment in self.attachments:
        #     with open(attachment, 'rb') as file:
        #         data = file.read()
        #         encoded_data = base64.b64encode(data).decode('utf-8')
        #         embedded_image = f'![attachment:{os.path.basename(attachment)}](data:image/png;base64,{encoded_data})'
        #         content = content.replace(f'![attachment:{os.path.basename(attachment)}]', embedded_image)
        # content+=EMBED_START
        for key in self.file_content.keys():
            content+=self.file_content[key]+'\n'
        return content

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = RichDocumentEditor()
    editor.show()
    sys.exit(app.exec_())










