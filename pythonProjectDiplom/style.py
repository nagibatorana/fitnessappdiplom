app_style = """
* {
    font-family: 'Montserrat', 'Segoe UI', sans-serif;
    font-size: 17px;
    font-weight: 600;   
    outline: none;
}
QWidget {
    background-color: #121212;
    color: #ffffff;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9b1b30, stop:1 #6b101e);
    color: white;
    border: none;
    padding: 14px 28px;
    min-width: 130px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b71e3a, stop:1 #851525);
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6b101e, stop:1 #4a0b14);
}
QLineEdit {
    background-color: #1e1e1e;
    color: white;
    border: none;
    border-bottom: 2px solid #e63946;
    padding: 10px 4px;
    font-size: 16px;
    border-radius: 4px;
}
QLineEdit:focus {
    border-bottom: 2px solid #ff5c6c;
    background-color: #222222;
}
QTextEdit {
    background-color: #1e1e1e;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 10px;
    font-size: 15px;
    selection-background-color: #9b1b30;
}
QComboBox {
    background-color: #1e1e1e;
    color: white;
    border: 1px solid #e63946;         
    padding: 10px;
    border-radius: 8px;
    font-size: 15px;
    min-width: 120px;
}
QComboBox:hover {
    border: 1px solid #ff5c6c;          
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    color: white;
    selection-background-color: #9b1b30;
    border: none;
}
QListWidget {
    background-color: #1e1e1e;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 5px;
    font-size: 15px;
}
QListWidget::item {
    padding: 12px;
    border-radius: 8px;
}
QListWidget::item:selected {
    background-color: #9b1b30;
}
QTabWidget::pane {
    border: none;
    background: #1e1e1e;
    border-radius: 10px;
    margin-top: 5px;
}
QTabBar::tab {
    background: #2a2a2a;
    color: #aaa;
    padding: 12px 25px;
    border: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9b1b30, stop:1 #6b101e);
    color: white;
}
QScrollArea {
    border: none;
    background: transparent;
}
QFrame {
    background-color: #1e1e1e;
    border-radius: 12px;
    padding: 10px;
}
QLabel {
    color: #ffffff;
    font-size: 15px;
}
QMessageBox {
    background-color: #1e1e1e;
}
QMessageBox QLabel {
    color: #ffffff;
    font-size: 14px;
}
QMessageBox QPushButton {
    min-width: 80px;
}
QSpinBox {
    background-color: #1e1e1e;
    color: white;
    border: none;
    padding: 6px;
    border-radius: 8px;
}
QRadioButton {
    spacing: 10px;
    color: #ddd;
    font-size: 15px;
}
QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid #777;
    background: transparent;
}
QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9b1b30, stop:1 #6b101e);
    border: 2px solid #e63946;
}
QRadioButton::indicator:hover {
    border: 2px solid #e63946;
}
QScrollBar:vertical {
    background: #121212;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #555;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #121212;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #555;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""