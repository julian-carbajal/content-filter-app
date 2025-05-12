import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QLineEdit, QFrame, QMenuBar, QMenu, QStatusBar,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import (QColor, QPalette, QAction, QKeySequence,
                        QDragEnterEvent, QDropEvent, QShortcut)

MODES = [
    {
        'name': 'Child Safe Mode',
        'description': 'Strict filtering for children.'
    },
    {
        'name': 'High School Teen Safe Mode',
        'description': 'Moderate filtering for teens.'
    },
    {
        'name': 'Custom Mode',
        'description': 'Customize your own filtering.'
    }
]

class ContentFilter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mode_data = {
            mode['name']: {'whitelist': [], 'blacklist': []}
            for mode in MODES
        }
        self.current_mode = MODES[0]['name']
        self.init_ui()
        self.setup_shortcuts()
        self.setup_menubar()
        self.setup_statusbar()
        self.setAcceptDrops(True)
        
        # Load default configuration if exists
        default_config = Path('content_filter_config.json')
        if default_config.exists():
            try:
                self.load_configuration(default_config)
                self.statusBar().showMessage('Loaded default configuration', 3000)
            except Exception as e:
                self.statusBar().showMessage(f'Failed to load default configuration: {str(e)}', 5000)

    def init_ui(self):
        self.setWindowTitle('Content Filter')
        self.setMinimumSize(900, 600)
        
        # Set dark theme
        self.setup_dark_theme()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        modes_label = QLabel('Modes')
        modes_label.setStyleSheet('color: rgb(120, 60, 200); font-weight: bold;')
        sidebar_layout.addWidget(modes_label)

        for mode in MODES:
            btn = QPushButton(mode['name'])
            btn.clicked.connect(lambda checked, m=mode['name']: self.update_mode(m))
            btn.setFixedWidth(180)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        layout.addWidget(sidebar)

        # Create main area
        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        
        # Add search bars
        self.wl_search = QLineEdit()
        self.wl_search.setPlaceholderText('Search whitelist...')
        self.wl_search.textChanged.connect(lambda: self.filter_list('whitelist'))
        
        self.bl_search = QLineEdit()
        self.bl_search.setPlaceholderText('Search blacklist...')
        self.bl_search.textChanged.connect(lambda: self.filter_list('blacklist'))
        
        # Mode title and description
        self.mode_title = QLabel()
        self.mode_title.setStyleSheet('color: rgb(60, 60, 120); font-weight: bold;')
        self.mode_desc = QLabel()
        self.mode_desc.setWordWrap(True)
        
        main_layout.addWidget(self.mode_title)
        main_layout.addWidget(self.mode_desc)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Whitelist section
        whitelist_label = QLabel('Whitelist')
        whitelist_label.setStyleSheet('color: rgb(0, 150, 0); font-weight: bold;')
        main_layout.addWidget(whitelist_label)
        main_layout.addWidget(self.wl_search)

        wl_input_layout = QHBoxLayout()
        self.wl_input = QLineEdit()
        self.wl_input.setPlaceholderText('Add to whitelist...')
        wl_add_btn = QPushButton('Add to Whitelist')
        wl_add_btn.clicked.connect(lambda: self.add_to_list('whitelist'))
        
        wl_input_layout.addWidget(self.wl_input)
        wl_input_layout.addWidget(wl_add_btn)
        main_layout.addLayout(wl_input_layout)

        self.whitelist = QTextEdit()
        self.whitelist.setReadOnly(True)
        self.whitelist.setMaximumHeight(80)
        main_layout.addWidget(self.whitelist)

        wl_remove_btn = QPushButton('Remove Selected from Whitelist')
        wl_remove_btn.clicked.connect(lambda: self.remove_selected('whitelist'))
        main_layout.addWidget(wl_remove_btn)

        # Blacklist section
        blacklist_label = QLabel('Blacklist')
        blacklist_label.setStyleSheet('color: rgb(200, 0, 0); font-weight: bold;')
        main_layout.addWidget(blacklist_label)
        main_layout.addWidget(self.bl_search)

        bl_input_layout = QHBoxLayout()
        self.bl_input = QLineEdit()
        self.bl_input.setPlaceholderText('Add to blacklist...')
        bl_add_btn = QPushButton('Add to Blacklist')
        bl_add_btn.clicked.connect(lambda: self.add_to_list('blacklist'))
        
        bl_input_layout.addWidget(self.bl_input)
        bl_input_layout.addWidget(bl_add_btn)
        main_layout.addLayout(bl_input_layout)

        self.blacklist = QTextEdit()
        self.blacklist.setReadOnly(True)
        self.blacklist.setMaximumHeight(80)
        main_layout.addWidget(self.blacklist)

        bl_remove_btn = QPushButton('Remove Selected from Blacklist')
        bl_remove_btn.clicked.connect(lambda: self.remove_selected('blacklist'))
        main_layout.addWidget(bl_remove_btn)

        layout.addWidget(main_area)
        
        # Set initial mode
        self.update_mode(self.current_mode)

    def update_mode(self, mode_name):
        self.current_mode = mode_name
        self.mode_title.setText(mode_name)
        self.mode_desc.setText(next(m['description'] for m in MODES if m['name'] == mode_name))
        self.update_lists()

    def setup_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2a82da;
                border: none;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
            QLineEdit, QTextEdit {
                background-color: #232323;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                color: white;
            }
            QMenuBar {
                background-color: #353535;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #2a82da;
            }
            QMenu {
                background-color: #353535;
                color: white;
            }
            QMenu::item:selected {
                background-color: #2a82da;
            }
        """)

    def setup_menubar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        save_action = QAction('&Save Configuration', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_action)
        
        load_action = QAction('&Load Configuration', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        clear_action = QAction('&Clear All Lists', self)
        clear_action.triggered.connect(self.clear_all_lists)
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        sort_menu = edit_menu.addMenu('Sort Lists')
        sort_asc_action = QAction('Sort Ascending', self)
        sort_asc_action.triggered.connect(lambda: self.sort_lists('asc'))
        sort_menu.addAction(sort_asc_action)
        
        sort_desc_action = QAction('Sort Descending', self)
        sort_desc_action.triggered.connect(lambda: self.sort_lists('desc'))
        sort_menu.addAction(sort_desc_action)
        
        # Import/Export menu
        imp_exp_menu = menubar.addMenu('&Import/Export')
        
        export_csv_action = QAction('Export to CSV', self)
        export_csv_action.triggered.connect(lambda: self.export_lists('csv'))
        imp_exp_menu.addAction(export_csv_action)
        
        export_txt_action = QAction('Export to TXT', self)
        export_txt_action.triggered.connect(lambda: self.export_lists('txt'))
        imp_exp_menu.addAction(export_txt_action)
        
        imp_exp_menu.addSeparator()
        
        import_csv_action = QAction('Import from CSV', self)
        import_csv_action.triggered.connect(lambda: self.import_lists('csv'))
        imp_exp_menu.addAction(import_csv_action)
        
        import_txt_action = QAction('Import from TXT', self)
        import_txt_action.triggered.connect(lambda: self.import_lists('txt'))
        imp_exp_menu.addAction(import_txt_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        stats_action = QAction('Show Statistics', self)
        stats_action.triggered.connect(self.show_statistics)
        view_menu.addAction(stats_action)

    def setup_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)

    def setup_shortcuts(self):
        # Add item shortcuts
        QShortcut(QKeySequence('Return'), self.wl_input, lambda: self.add_to_list('whitelist'))
        QShortcut(QKeySequence('Return'), self.bl_input, lambda: self.add_to_list('blacklist'))
        
        # Delete item shortcuts
        QShortcut(QKeySequence('Delete'), self.whitelist, lambda: self.remove_selected('whitelist'))
        QShortcut(QKeySequence('Delete'), self.blacklist, lambda: self.remove_selected('blacklist'))

    def save_configuration(self, filename=None):
        if not filename:
            filename, _ = QFileDialog.getSaveFileName(self, 'Save Configuration',
                                                    'content_filter_config.json',
                                                    'JSON files (*.json)')
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.mode_data, f, indent=4)
                self.statusBar().showMessage(f'Configuration saved to {filename}', 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save configuration: {str(e)}')

    def load_configuration(self, filename=None):
        if isinstance(filename, Path):
            filename = str(filename)
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Load Configuration',
                                                    '',
                                                    'JSON files (*.json)')
        if filename:
            try:
                with open(filename) as f:
                    self.mode_data = json.load(f)
                self.update_lists()
                self.statusBar().showMessage(f'Configuration loaded from {filename}', 3000)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load configuration: {str(e)}')

    def clear_all_lists(self):
        reply = QMessageBox.question(self, 'Clear All Lists',
                                   'Are you sure you want to clear all lists in the current mode?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mode_data[self.current_mode]['whitelist'] = []
            self.mode_data[self.current_mode]['blacklist'] = []
            self.update_lists()
            self.statusBar().showMessage('All lists cleared', 3000)

    def filter_list(self, list_type):
        search_text = self.wl_search.text() if list_type == 'whitelist' else self.bl_search.text()
        items = self.mode_data[self.current_mode][list_type]
        
        if search_text:
            filtered_items = [item for item in items if search_text.lower() in item.lower()]
        else:
            filtered_items = items
            
        text_edit = self.whitelist if list_type == 'whitelist' else self.blacklist
        text_edit.setText('\n'.join(filtered_items))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        text = event.mimeData().text()
        if text:
            # Determine which list to add to based on drop position
            pos = event.position()
            target_widget = self.childAt(int(pos.x()), int(pos.y()))
            
            if isinstance(target_widget, QTextEdit):
                if target_widget == self.whitelist:
                    self.add_items_to_list('whitelist', text.split('\n'))
                elif target_widget == self.blacklist:
                    self.add_items_to_list('blacklist', text.split('\n'))

    def add_items_to_list(self, list_type, items):
        added = 0
        for item in items:
            item = item.strip()
            if item and item not in self.mode_data[self.current_mode][list_type]:
                self.mode_data[self.current_mode][list_type].append(item)
                added += 1
        
        if added > 0:
            self.update_lists()
            self.statusBar().showMessage(f'Added {added} items to {list_type}', 3000)

    def sort_lists(self, direction: str = 'asc'):
        for list_type in ['whitelist', 'blacklist']:
            items = self.mode_data[self.current_mode][list_type]
            self.mode_data[self.current_mode][list_type] = sorted(items, reverse=(direction == 'desc'))
        
        self.update_lists()
        self.statusBar().showMessage(f'Lists sorted {direction}ending', 3000)
    
    def export_lists(self, format_type: str):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f'content_filter_{self.current_mode}_{timestamp}'
        
        if format_type == 'csv':
            filename, _ = QFileDialog.getSaveFileName(self, 'Export Lists',
                                                    f'{default_name}.csv',
                                                    'CSV files (*.csv)')
            if filename:
                try:
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Type', 'Item'])
                        for item in self.mode_data[self.current_mode]['whitelist']:
                            writer.writerow(['whitelist', item])
                        for item in self.mode_data[self.current_mode]['blacklist']:
                            writer.writerow(['blacklist', item])
                    self.statusBar().showMessage(f'Lists exported to {filename}', 3000)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to export lists: {str(e)}')
        
        elif format_type == 'txt':
            filename, _ = QFileDialog.getSaveFileName(self, 'Export Lists',
                                                    f'{default_name}.txt',
                                                    'Text files (*.txt)')
            if filename:
                try:
                    with open(filename, 'w') as f:
                        f.write(f'=== {self.current_mode} ===\n\n')
                        f.write('=== Whitelist ===\n')
                        f.write('\n'.join(self.mode_data[self.current_mode]['whitelist']))
                        f.write('\n\n=== Blacklist ===\n')
                        f.write('\n'.join(self.mode_data[self.current_mode]['blacklist']))
                    self.statusBar().showMessage(f'Lists exported to {filename}', 3000)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to export lists: {str(e)}')
    
    def import_lists(self, format_type: str):
        if format_type == 'csv':
            filename, _ = QFileDialog.getOpenFileName(self, 'Import Lists',
                                                    '',
                                                    'CSV files (*.csv)')
            if filename:
                try:
                    with open(filename, newline='') as f:
                        reader = csv.reader(f)
                        next(reader)  # Skip header
                        for row in reader:
                            if len(row) == 2:
                                list_type, item = row
                                if list_type in ['whitelist', 'blacklist']:
                                    if item not in self.mode_data[self.current_mode][list_type]:
                                        self.mode_data[self.current_mode][list_type].append(item)
                    self.update_lists()
                    self.statusBar().showMessage(f'Lists imported from {filename}', 3000)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to import lists: {str(e)}')
        
        elif format_type == 'txt':
            filename, _ = QFileDialog.getOpenFileName(self, 'Import Lists',
                                                    '',
                                                    'Text files (*.txt)')
            if filename:
                try:
                    current_list = None
                    with open(filename) as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('=== Whitelist ==='):
                                current_list = 'whitelist'
                            elif line.startswith('=== Blacklist ==='):
                                current_list = 'blacklist'
                            elif line and not line.startswith('===') and current_list:
                                if line not in self.mode_data[self.current_mode][current_list]:
                                    self.mode_data[self.current_mode][current_list].append(line)
                    self.update_lists()
                    self.statusBar().showMessage(f'Lists imported from {filename}', 3000)
                except Exception as e:
                    QMessageBox.critical(self, 'Error', f'Failed to import lists: {str(e)}')
    
    def show_statistics(self):
        whitelist = self.mode_data[self.current_mode]['whitelist']
        blacklist = self.mode_data[self.current_mode]['blacklist']
        
        stats = f"""Statistics for {self.current_mode}:

Whitelist:
- Total items: {len(whitelist)}
- Average item length: {sum(len(x) for x in whitelist) / len(whitelist) if whitelist else 0:.1f}
- Shortest item: {min((len(x), x) for x in whitelist)[1] if whitelist else 'N/A'}
- Longest item: {max((len(x), x) for x in whitelist)[1] if whitelist else 'N/A'}

Blacklist:
- Total items: {len(blacklist)}
- Average item length: {sum(len(x) for x in blacklist) / len(blacklist) if blacklist else 0:.1f}
- Shortest item: {min((len(x), x) for x in blacklist)[1] if blacklist else 'N/A'}
- Longest item: {max((len(x), x) for x in blacklist)[1] if blacklist else 'N/A'}
"""
        
        QMessageBox.information(self, 'List Statistics', stats)
    
    def update_lists(self):
        # Update the lists while preserving any active filters
        self.filter_list('whitelist')
        self.filter_list('blacklist')

    def add_to_list(self, list_type):
        input_field = self.wl_input if list_type == 'whitelist' else self.bl_input
        item = input_field.text().strip()
        
        if item and item not in self.mode_data[self.current_mode][list_type]:
            self.mode_data[self.current_mode][list_type].append(item)
            input_field.clear()
            self.update_lists()

    def remove_selected(self, list_type):
        text_edit = self.whitelist if list_type == 'whitelist' else self.blacklist
        cursor = text_edit.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            if selected in self.mode_data[self.current_mode][list_type]:
                self.mode_data[self.current_mode][list_type].remove(selected)
                self.update_lists()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = ContentFilter()
    window.show()
    
    # Show welcome message
    window.statusBar().showMessage('Welcome to Content Filter! Press Ctrl+H for help', 5000)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()