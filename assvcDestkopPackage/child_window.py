import os
import sys

from assvcPackage.history import howManyCommits, getCommits


from assvcPackage import compare, diff, commit

from PySide6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QApplication, QFrame, QPushButton, QStyle, QListWidget, QListWidgetItem, QSplitter, QTextEdit
)

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import QSize
from assvcDestkopPackage import menu, file_widget
from assvcDestkopPackage.loading import run_with_loading



class ChildWindow(QMainWindow):
    
    def __init__(self, path):
        super().__init__()
        self.setWindowTitle("ASSVC Desktop")
        self.resize(800, 600)
        self.repository_path = path
        
        from assvcPackage.utils import set_repository_path
        set_repository_path(path)
        
        self.selected = "Changes"
        self.number = 0
        self.fileList = []
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
        """)
        self.message = ""

        self.create_ui()
    def create_ui(self):
        self.create_sidebar()
        self.create_content()
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        menu.home_menu(self, menubar)
        menu.file_menu(self, menubar, True, self.repository_path)
        menu.repository_menu(self, menubar, self.repository_path)
        menu.help_menu(self, menubar)
        
    def create_sidebar(self):
        self.blue_color = "#1e90ff"

        self.button_style = f"""
        QPushButton {{
            min-width: 100px;
            min-height: 30px;
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            background: #2a2a2a;
            border-radius: 12px;
            border-bottom: 2px solid transparent; /* default no underline */
        }}
        QPushButton:hover {{
            background: #3a3a3a;
        }}
        """

        self.button_style_selected = f"""
        QPushButton {{
            min-width: 100px;
            min-height: 30px;
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            background: #4a4a4a;
            border-radius: 12px;
            border-bottom: 2px solid {self.blue_color}; /* blue underline */
        }}
        QPushButton:hover {{
            background: #3a3a3a;
        }}
        """

        self.button_style_refresh = f"""
        QPushButton {{
            max-width: 30px;
            max-height: 30px;
            min-width: 30px;
            min-height: 30px;
            padding: 2px;
            color: #ffffff;
            background: #2a2a2a;
            border-radius: 12px;
        }}
        QPushButton:hover {{
            background: #3a3a3a;
        }}
        """

        self.button_style_blue = f"""
        QPushButton {{
            min-width: 100px;
            min-height: 30px;
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
            background: {self.blue_color};
            border-radius: 12px;
        }}
        QPushButton:hover {{
            background: #1a75d1;  /* slightly darker on hover */
        }}
        """

        self.files_style = f"""
        QListWidget {{
            background: #2a2a2a;
            color: #ffffff;
            font-size: 14px;
            border: 0px;
        }}
        QListWidget::item {{
            padding: 5px;
        }}
        QListWidget::item:selected {{
            background: {self.blue_color};
        }}
        """

        self.message_input_style = f"""
        QLineEdit {{
            min-width: 200px;
            min-height: 30px;
            font-size: 14px;
            color: #ffffff;
            background: #2a2a2a;
            border: 1px solid #4a4a4a;
            border-radius: 5px;
            padding: 5px;
            outline: {self.blue_color};  /* blue outline */
        }}
        QLineEdit:focus {{
            border: 1px solid {self.blue_color};
            background: #3a3a3a;
        }}
        """


        if hasattr(self, 'sidebar') and self.sidebar is not None:
            return
        
        seperatorH = QFrame()
        seperatorH.setFrameShape(QFrame.HLine)
        seperatorH.setFrameShadow(QFrame.Sunken)
        seperatorV = QFrame()
        seperatorV.setFrameShape(QFrame.VLine)
        seperatorV.setFrameShadow(QFrame.Sunken)

        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setStyleSheet("background: #2a2a2a;")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(5)

        self.repository_path = os.path.dirname(self.repository_path)
        current_repo_label = QLabel(f"Repository:\n{os.path.basename(self.repository_path)}")
        current_repo_label.setStyleSheet("font-size: 16px; color: #ffffff; padding: 8px;")

        self.tabs = QWidget()
        self.tabs.setStyleSheet("background: #2a2a2a;")
        tabs_layout = QHBoxLayout(self.tabs)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)

        self.changes_button = QPushButton("Changes")
        self.history_button = QPushButton("History")


        self.changes_button.setStyleSheet(self.button_style_selected)
        self.changes_button.clicked.connect(lambda checked, b=self.changes_button: self.select_tab(b.text()))
        self.history_button.setStyleSheet(self.button_style)
        self.history_button.clicked.connect(lambda checked, b=self.history_button: self.select_tab(b.text()))


        
        tabs_layout.addWidget(self.changes_button)
        tabs_layout.addWidget(self.history_button)

        self.changednumber = QWidget()
        self.changednumber.setStyleSheet("background: #2a2a2a;")
        
        changednumber_layout = QHBoxLayout(self.changednumber)
        changednumber_layout.setContentsMargins(0, 0, 0, 0)
        changednumber_layout.setSpacing(0)

        self.changed_files_label = QLabel(f"{self.number} changed files")
        self.changed_files_label.setStyleSheet("font-size: 14px; color: #ffffff; padding: 8px;")

        refresh_button = QPushButton()
        refresh_button.setIcon(
            QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        )

        refresh_button.setStyleSheet(self.button_style_refresh)
        refresh_button.clicked.connect(self.on_refresh_clicked)

        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self.on_refresh_clicked)
        
        changednumber_layout.addWidget(self.changed_files_label)
        changednumber_layout.addWidget(refresh_button)


        self.changed_files_list = QListWidget()
        self.changed_files_list.setStyleSheet(self.files_style)
        self.changed_files_list.setIconSize(QSize(16, 16))
        from PySide6.QtWidgets import QSizePolicy
        self.changed_files_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for file in self.fileList:
            self.changed_files_list.addItem(file)

        self.commitnumber = QWidget()
        self.commitnumber.setStyleSheet("background: #2a2a2a;")
        
        commitnumber_layout = QHBoxLayout(self.commitnumber)
        commitnumber_layout.setContentsMargins(0, 0, 0, 0)
        commitnumber_layout.setSpacing(0)

        self.commit_label = QLabel(f"{howManyCommits(self.repository_path)} commits")
        self.commit_label.setStyleSheet("font-size: 14px; color: #ffffff; padding: 8px;")
        refresh_button = QPushButton()
        refresh_button.setIcon(
            QApplication.style().standardIcon(QStyle.SP_BrowserReload)
        )

        refresh_button.setStyleSheet(self.button_style_refresh)
        refresh_button.clicked.connect(self.on_refresh_clicked)
        
        commitnumber_layout.addWidget(self.commit_label)
        commitnumber_layout.addWidget(refresh_button)


        self.history_list = QListWidget()
        self.history_list.setStyleSheet(self.files_style)
        self.history_list.setIconSize(QSize(16, 16))
        from PySide6.QtWidgets import QSizePolicy
        self.history_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.action_buttons_container = QWidget()
        action_buttons_layout = QHBoxLayout(self.action_buttons_container)
        action_buttons_layout.setContentsMargins(0, 0, 0, 0)
        action_buttons_layout.setSpacing(5)
        
        self.stage_all_button = QPushButton("Stage All")
        self.stage_all_button.setStyleSheet(self.button_style)
        self.stage_all_button.clicked.connect(self.button_stage_toggle)
        
        self.revert_all_button = QPushButton("Revert All")
        self.revert_all_button.setStyleSheet(self.button_style)
        self.revert_all_button.clicked.connect(self.button_revert_all)
        
        action_buttons_layout.addWidget(self.stage_all_button)
        action_buttons_layout.addWidget(self.revert_all_button)

        input_field = QLineEdit()
        input_field.setPlaceholderText("Commit message...")
        input_field.setStyleSheet(self.message_input_style)
        

        commit_button = QPushButton("Commit")
        commit_button.setStyleSheet(self.button_style_blue)
        commit_button.clicked.connect(lambda: self.button_commit(input_field.text()))
        

        sidebar_layout.addWidget(current_repo_label)
        sidebar_layout.addWidget(self.create_separator())
        sidebar_layout.addWidget(self.tabs)
        sidebar_layout.addWidget(self.create_separator())
        sidebar_layout.addWidget(self.changednumber)
        sidebar_layout.addWidget(self.create_separator())
        sidebar_layout.addWidget(self.changed_files_list, 1)
        sidebar_layout.addWidget(self.commitnumber)
        sidebar_layout.addWidget(self.create_separator())
        sidebar_layout.addWidget(self.history_list, 1)
        sidebar_layout.addWidget(self.action_buttons_container)
        sidebar_layout.addWidget(input_field)
        sidebar_layout.addWidget(commit_button)
        
        self.commitnumber.hide()
        self.history_list.hide()


        self.content = QWidget()
        self.content.setStyleSheet("background: #1a1a1a;")
    
    def create_content(self):
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        self.path_label = QLabel("Select a file to view changes")
        self.path_label.setStyleSheet(f"""
            font-size: 14px;
            color: {self.blue_color};
            padding: 8px;
            background: #2a2a2a;
            border-radius: 5px;
        """)
        content_layout.addWidget(self.path_label)
        
        code_container = QWidget()
        code_layout = QHBoxLayout(code_container)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(10)
        
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        left_label = QLabel("Before")
        left_label.setStyleSheet("font-size: 12px; color: #ffffff; font-weight: bold;")
        
        self.left_code = QTextEdit()
        self.left_code.setReadOnly(True)
        self.left_code.setStyleSheet("""
            QTextEdit {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.left_code.setPlainText('NO FILE SELECTED')
        
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_code)
        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        right_label = QLabel("After")
        right_label.setStyleSheet("font-size: 12px; color: #ffffff; font-weight: bold;")
        
        self.right_code = QTextEdit()
        self.right_code.setReadOnly(True)
        self.right_code.setStyleSheet("""
            QTextEdit {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.right_code.setPlainText('NO FILE SELECTED')
        
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_code)
        

        code_layout.addWidget(left_container, 1)
        code_layout.addWidget(right_container, 1)
        
        content_layout.addWidget(code_container, 1)


        splitter = QSplitter()
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 560])

        self.setCentralWidget(splitter)

    def show_diff(self, path, labelpath):
        data = diff.diff("latest", path, noPrint=True)
        if data and len(data) > 0:
            file_data = data[0]
            if 'binary' not in file_data:
                old_content = file_data.get('old_content', '')
                new_content = file_data.get('new_content', '')
                diff_lines = file_data.get('diff', [])
                
                if diff_lines:
                    old_html_lines = []
                    new_html_lines = []
                    old_lineno = 0
                    new_lineno = 0
                    
                    i = 0
                    while i < len(diff_lines):
                        line = diff_lines[i].rstrip('\n')
                        
                        if line.startswith('---') or line.startswith('+++'):
                            i += 1
                            continue
                        
                        if line.startswith('@@'):
                            parts = line.split()
                            if len(parts) >= 3:
                                old_info = parts[1].lstrip('-').split(',')
                                new_info = parts[2].lstrip('+').split(',')
                                old_lineno = int(old_info[0])
                                new_lineno = int(new_info[0])
                            
                            if old_html_lines or new_html_lines:
                                old_html_lines.append('<span style="color: #888;">...</span>')
                                new_html_lines.append('<span style="color: #888;">...</span>')
                            i += 1
                            continue
                        
                        if line.startswith('-'):
                            content = line[1:].replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                            old_html_lines.append(f'<span style="color: #666;">{old_lineno:4d}</span> <span style="color: #ff6b6b;">-</span> <span style="background: #4a2020;">{content}</span>')
                            old_lineno += 1
                        elif line.startswith('+'):
                            content = line[1:].replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                            new_html_lines.append(f'<span style="color: #666;">{new_lineno:4d}</span> <span style="color: #51cf66;">+</span> <span style="background: #1a3a1a;">{content}</span>')
                            new_lineno += 1
                        else:
                            content = line[1:] if line.startswith(' ') else line
                            content = content.replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                            old_html_lines.append(f'<span style="color: #666;">{old_lineno:4d}</span> &nbsp; {content}')
                            new_html_lines.append(f'<span style="color: #666;">{new_lineno:4d}</span> &nbsp; {content}')
                            old_lineno += 1
                            new_lineno += 1
                        
                        i += 1
                    
                    old_html = '<pre style="margin: 0; font-family: \'Courier New\', monospace; font-size: 12px; background: #2a2a2a;">' + '<br>'.join(old_html_lines) + '</pre>'
                    new_html = '<pre style="margin: 0; font-family: \'Courier New\', monospace; font-size: 12px; background: #2a2a2a;">' + '<br>'.join(new_html_lines) + '</pre>'
                    
                    self.left_code.setHtml(old_html)
                    self.right_code.setHtml(new_html)
                else:
                    self.left_code.setPlainText(old_content)
                    self.right_code.setPlainText(new_content)
            else:
                self.left_code.setPlainText("Binary file - no preview available")
                self.right_code.setPlainText("Binary file - no preview available")
        self.path_label.setText(f"Showing changes for: {labelpath}")
        self.content.show()

    def select_tab(self, tab_name):
        self.selected = tab_name
        if tab_name == "Changes":
            self.changes_button.setStyleSheet(self.button_style_selected)
            self.history_button.setStyleSheet(self.button_style)
            self.content.show()
            self.changednumber.show()
            self.changed_files_list.show()
            self.action_buttons_container.show()
            self.commitnumber.hide()
            self.history_list.hide()
        else:
            self.changes_button.setStyleSheet(self.button_style)
            self.history_button.setStyleSheet(self.button_style_selected)
            self.content.hide()
            self.changednumber.hide()
            self.changed_files_list.hide()
            self.action_buttons_container.hide()
            self.commitnumber.show()
            self.history_list.show()
            self.populate_history_list()
        print(f"Selected tab: {self.selected}")

    def populate_history_list(self):
        """Populate the history list with commits"""
        self.history_list.clear()
        
        commits = getCommits(self.repository_path)
        
        if not commits:
            self.history_list.addItem("No commits yet")
            return
        
        for commit_sha, message, timestamp, commiter in commits:
            from assvcPackage.utils import shorten_sha, get_history, find_assvc
            assvc_path = find_assvc(self.repository_path)
            if assvc_path:
                short_sha = shorten_sha(commit_sha, get_history(assvc_path))
            else:
                short_sha = commit_sha[:7]
            
            display_text = f"{short_sha} - {message}"
            if timestamp:
                display_text += f" ({timestamp})"
            
            self.history_list.addItem(display_text)

    def in_repo_directory(self, func):
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.repository_path)
            return func()
        finally:
            os.chdir(original_cwd)

    def on_refresh_clicked(self):
        def do_refresh():
            return self.in_repo_directory(
                lambda: compare.compare("latest", False, True, True)
            )
        
        try:
            result = run_with_loading(
                self,
                do_refresh,
                title="Refreshing",
                message="Checking for changes...\nPlease wait."
            )
            
            if result:
                tempList, self.number = result
            else:
                tempList, self.number = [], 0
                
            self.changed_files_label.setText(f"{self.number} changed files")
            self.changed_files_list.clear()

            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            pictures_dir = os.path.join(base_path, "pictures")
            
            for file in tempList:
                path = file[0]
                status = file[1]
                
                relative_path = os.path.relpath(path, self.repository_path)
                
                if status == "MODIFIED":
                    icon_path = os.path.join(pictures_dir, "yellow_dot_outline.png")
                elif status == "NEW":
                    icon_path = os.path.join(pictures_dir, "green_plus_outline.png")
                elif status == "DELETED":
                    icon_path = os.path.join(pictures_dir, "red_minus_outline.png")
                else:
                    icon_path = ""
                

                item = QListWidgetItem(self.changed_files_list)
                item.setSizeHint(QSize(0, 35))
                
                custom_widget = file_widget.FileListItemWidget(relative_path, status, icon_path, self)
                
                self.changed_files_list.addItem(item)
                self.changed_files_list.setItemWidget(item, custom_widget)
                
                self.fileList.append(relative_path)
            
            commit_count = howManyCommits(self.repository_path)
            self.commit_label.setText(f"{commit_count} commits")
            
            self.update_stage_button()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Refresh Failed", f"Failed to refresh changes:\n{str(e)}")

    def button_commit(self, message):
        def do_commit():
            return self.in_repo_directory(
                lambda: commit.commit(message=message)
            )
        run_with_loading(
            self,
            do_commit,
            title="Committing",
            message="Committing changes...\nPlease wait."
        )
        input_field = self.findChild(QLineEdit)
        if input_field:
            input_field.clear()
        self.on_refresh_clicked()

    def update_stage_button(self):
        from assvcPackage.stage import isStaged
        
        try:
            all_staged = True
            for file_path in self.fileList:
                full_path = os.path.join(self.repository_path, file_path)
                if not isStaged(full_path):
                    all_staged = False
                    break
            
            if all_staged and len(self.fileList) > 0:
                self.stage_all_button.setText("Unstage All")
            else:
                self.stage_all_button.setText("Stage All")
        except Exception:
            self.stage_all_button.setText("Stage All")

    def button_stage_toggle(self):
        if self.stage_all_button.text() == "Stage All":
            self.button_stage_all()
        else:
            self.button_unstage_all()

    def button_stage_all(self):
        from assvcPackage.stage import stageAll
        def do_stage_all():
            return self.in_repo_directory(stageAll)
        
        try:
            run_with_loading(
                self,
                do_stage_all,
                title="Staging All",
                message="Staging all files...\nPlease wait."
            )
            self.on_refresh_clicked()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Stage All Failed", f"Failed to stage all files:\n{str(e)}")

    def button_unstage_all(self):
        from assvcPackage.stage import unstageAll
        def do_unstage_all():
            return self.in_repo_directory(unstageAll)
        
        try:
            run_with_loading(
                self,
                do_unstage_all,
                title="Unstaging All",
                message="Unstaging all files...\nPlease wait."
            )
            self.on_refresh_clicked()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Unstage All Failed", f"Failed to unstage all files:\n{str(e)}")

    def button_revert_all(self):
        from PySide6.QtWidgets import QMessageBox
        from assvcPackage.reverse import reverse
        
        reply = QMessageBox.question(
            self,
            "Revert All Changes",
            "Are you sure you want to revert all changes?\nThis cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            def do_revert_all():
                return self.in_repo_directory(
                    lambda: reverse(commit_sha="latest", isPrintArgument=False, isForce=True)
                )
            
            try:
                run_with_loading(
                    self,
                    do_revert_all,
                    title="Reverting All",
                    message="Reverting all changes...\nPlease wait."
                )
                self.on_refresh_clicked()
            except Exception as e:
                QMessageBox.critical(self, "Revert All Failed", f"Failed to revert all changes:\n{str(e)}")

    def create_separator(self, vertical=False):
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine if vertical else QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep
    
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ChildWindow("Test Repository")
    window.show()

    app.exec()