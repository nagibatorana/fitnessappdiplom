import sys
import os
import json
import sqlite3
import hashlib
import time
import uuid

import urllib3
import requests
import numpy as np

from PyQt5.QtCore import (
    Qt, QRect, QEvent, QTimer, QThread, pyqtSignal, QPropertyAnimation
)
from PyQt5.QtGui import (
    QColor, QPalette, QPixmap, QCursor, QFontDatabase, QFont
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QComboBox, QSpinBox, QMessageBox, QScrollArea, QFrame, QTabWidget, QRadioButton,
    QStackedWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QFormLayout, QGraphicsOpacityEffect, QButtonGroup
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from style import app_style
from exercises import exercises_info
from workouts import create_group_workouts, group_info
from workmodels import Exercise, Training
from information import sportpit, periodization, diet, work_weight

class UserDB:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def register(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                               (username, password_hash))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?",
                           (username, password_hash))
            row = cursor.fetchone()
        return row[0] if row else None

class UserDataStorage:
    @staticmethod
    def save_user_group(user_id, group_id):
        if user_id is None:
            return
        dir_path = UserDataStorage.get_user_dir(user_id)
        data = {"group_id": group_id}
        with open(os.path.join(dir_path, "user_settings.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)

    @staticmethod
    def load_user_group(user_id):
        if user_id is None:
            return 1
        file_path = os.path.join(UserDataStorage.get_user_dir(user_id), "user_settings.json")
        if not os.path.exists(file_path):
            return 1
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("group_id", 1)

    @staticmethod
    def get_user_dir(user_id):
        dir_name = f"user_data/user_{user_id}"
        os.makedirs(dir_name, exist_ok=True)
        return dir_name

    @staticmethod
    def save_trainings(user_id, trainings):
        if user_id is None:
            return
        dir_path = UserDataStorage.get_user_dir(user_id)
        data = []
        for tr in trainings:
            if tr.is_predefined:
                continue
            data.append({
                "name": tr.name,
                "exercises": [
                    {"name": ex.name, "description": ex.description,
                     "muscle_group": ex.muscle_group, "sets": ex.sets, "reps": ex.reps}
                    for ex in tr.exercises
                ]
            })
        with open(os.path.join(dir_path, "trainings.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_trainings(user_id):
        if user_id is None:
            return []
        file_path = os.path.join(UserDataStorage.get_user_dir(user_id), "trainings.json")
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        trainings = []
        for tr_data in data:
            tr = Training(tr_data["name"], is_predefined=False)
            for ex_data in tr_data["exercises"]:
                ex = Exercise(ex_data["name"], ex_data["description"], ex_data["muscle_group"],
                              ex_data["sets"], ex_data["reps"])
                tr.add_exercise(ex)
            trainings.append(tr)
        return trainings

    @staticmethod
    def save_gigachat_history(user_id, messages_history):
        if user_id is None:
            return
        dir_path = UserDataStorage.get_user_dir(user_id)
        data = [msg for msg in messages_history if msg.get("role") != "system"]
        with open(os.path.join(dir_path, "gigachat_history.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_gigachat_history(user_id):
        if user_id is None:
            return []
        file_path = os.path.join(UserDataStorage.get_user_dir(user_id), "gigachat_history.json")
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в приложение")
        self.setFixedSize(500, 500)
        self.setStyleSheet(app_style)
        self.user_db = UserDB()
        self.result_user_id = None
        self.logged_username = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        title = QLabel("Фитнес-приложение")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #e63946; letter-spacing: 3px;")
        layout.addWidget(title)
        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Логин:", self.username_edit)
        form.addRow("Пароль:", self.password_edit)
        layout.addLayout(form)

        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self.do_login)
        layout.addWidget(btn_login)

        btn_register = QPushButton("Зарегистрироваться")
        btn_register.clicked.connect(self.do_register)
        layout.addWidget(btn_register)

        btn_guest = QPushButton("Продолжить без входа")
        btn_guest.clicked.connect(self.do_guest)
        layout.addWidget(btn_guest)

        self.setLayout(layout)

    def do_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        user_id = self.user_db.login(username, password)
        if user_id:
            self.result_user_id = user_id
            self.logged_username = username
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def do_register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        if self.user_db.register(username, password):
            QMessageBox.information(self, "Успех", "Регистрация выполнена. Теперь войдите.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")

    def do_guest(self):
        self.result_user_id = None
        self.accept()

class ExerciseSelectionWindow(QDialog):
    exercise_selected = pyqtSignal(Exercise)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор упражнений")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(app_style)
        self.all_exercises = self.load_all_exercises()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        self.muscle_group_combo = QComboBox()
        self.muscle_group_combo.addItems(["Все группы", "Дельты", "Пресс", "Грудь", "Ноги", "Спина", "Руки", "Трапеция"])
        self.muscle_group_combo.currentIndexChanged.connect(self.filter_exercises)
        filter_layout.addWidget(QLabel("Группа мышц:"))
        filter_layout.addWidget(self.muscle_group_combo)
        layout.addLayout(filter_layout)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск упражнений...")
        self.search_input.textChanged.connect(self.filter_exercises)
        layout.addWidget(self.search_input)
        self.exercise_list = QListWidget()
        self.populate_exercise_list()
        layout.addWidget(self.exercise_list)

        reps_layout = QHBoxLayout()
        reps_layout.addWidget(QLabel("Подходы:"))
        self.sets_spin = QSpinBox()
        self.sets_spin.setRange(1, 10)
        self.sets_spin.setValue(3)
        reps_layout.addWidget(self.sets_spin)
        reps_layout.addWidget(QLabel("Повторения:"))
        self.reps_spin = QSpinBox()
        self.reps_spin.setRange(1, 30)
        self.reps_spin.setValue(10)
        reps_layout.addWidget(self.reps_spin)
        reps_layout.addStretch()
        layout.addLayout(reps_layout)

        buttons_layout = QHBoxLayout()
        select_button = QPushButton("Выбрать")
        select_button.clicked.connect(self.select_exercise)
        buttons_layout.addWidget(select_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_all_exercises(self):
        exercises = []
        deltas = [
            "Обратные разведения в тренажере Peck-Deck (бабочка)",
            "Разведение гантелей стоя",
            "Жим гантелей сидя",
            "Жим штанги стоя (армейский жим)"
        ]
        for ex in deltas:
            exercises.append(Exercise(ex, "Упражнение для дельтовидных мышц", "Дельты"))

        abs_list = [
            "Скручивание на римском стуле",
            "Скручивания на скамье с наклоном вниз",
            "Обратные скручивания",
            "Подъемы ног в висе",
        ]
        for ex in abs_list:
            exercises.append(Exercise(ex, "Упражнение для мышц пресса", "Пресс"))

        chest_list = [
            "Жим штанги лежа",
            "Жим штанги на скамье с наклоном",
            "Жим от груди в тренажере сидя",
            "Сведения в тренажере Peck-Deck (бабочка)",
            "Сведение в кроссовере через верхние блоки",
        ]
        for ex in chest_list:
            exercises.append(Exercise(ex, "Упражнение для грудных мышц", "Грудь"))

        legs_list = [
            "Приседания со штангой",
            "Приседания в тренажере Смита",
            "Гак-приседания",
            "Жим ногами",
            "Разгибания ног",
            "Румынский подъем",
            "Гиперэкстензия для мышц бедра",
            "Сгибание ног лежа",
            "Подъемы на носки сидя"
        ]
        for ex in legs_list:
            exercises.append(Exercise(ex, "Упражнение для мышц ног", "Ноги"))

        back_list = [
            "Подтягивания на перекладине",
            "Тяга штанги в наклоне",
            "Тяга Т-штанги",
            "Тяга гантели одной рукой в наклоне",
            "Вертикальная тяга широким хватом",
            "Горизонтальная тяга в блочном тренажере",
        ]
        for ex in back_list:
            exercises.append(Exercise(ex, "Упражнение для мышц спины", "Спина"))

        arms_list = [
            "Жим штанги узким хватом лежа",
            "Жим к низу в блочном тренажере",
            "Разгибание руки с гантелью из-за головы",
            "Подъем штанги на бицепс стоя",
            "Подъемы гантелей на бицепс стоя",
            "Подъем гантелей на бицепс сидя",
            "МОЛОТОК",
            "Сгибание рук на бицепс в кроссовере",
        ]
        for ex in arms_list:
            exercises.append(Exercise(ex, "Упражнение для мышц рук", "Руки"))

        traps_list = [
            "Шраги со штангой",
            "Шраги с гантелями",
        ]
        for ex in traps_list:
            exercises.append(Exercise(ex, "Упражнение для трапециевидных мышц", "Трапеция"))

        return exercises

    def populate_exercise_list(self):
        self.exercise_list.clear()
        for exercise in self.all_exercises:
            item = QListWidgetItem(f"{exercise.name} ({exercise.muscle_group})")
            item.setData(Qt.UserRole, exercise)
            self.exercise_list.addItem(item)

    def filter_exercises(self):
        search_text = self.search_input.text().lower()
        muscle_group = self.muscle_group_combo.currentText()
        self.exercise_list.clear()
        for exercise in self.all_exercises:
            matches = True
            if muscle_group != "Все группы" and exercise.muscle_group != muscle_group:
                matches = False
            if search_text and search_text not in exercise.name.lower():
                matches = False
            if matches:
                item = QListWidgetItem(f"{exercise.name} ({exercise.muscle_group})")
                item.setData(Qt.UserRole, exercise)
                self.exercise_list.addItem(item)

    def select_exercise(self):
        selected_items = self.exercise_list.selectedItems()
        if selected_items:
            exercise = selected_items[0].data(Qt.UserRole)
            custom_exercise = Exercise(
                name=exercise.name,
                description=exercise.description,
                muscle_group=exercise.muscle_group,
                sets=self.sets_spin.value(),
                reps=self.reps_spin.value()
            )
            self.exercise_selected.emit(custom_exercise)
            self.close()
class ExerciseDetailsDialog(QDialog):
    def __init__(self, details, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подробная информация")
        self.setStyleSheet(app_style)
        self.details = details
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(40, 30, 40, 30)

        short = QLabel(
            f"<b>Задействованные мышцы:</b> {self.details['muscles']}<br>"
            f"<b>Тип:</b> {self.details['type']}<br>"
            f"<b>Эффект:</b> {self.details['effect']}"
        )
        short.setWordWrap(True)
        short.setStyleSheet("background-color: #1e1e1e; padding: 15px; border-radius: 12px; font-size: 16px;")
        content_layout.addWidget(short)

        desc_label = QLabel("<b>Описание</b>")
        desc_label.setStyleSheet("font-size: 22px; margin-top: 20px;")
        content_layout.addWidget(desc_label)
        desc_text = QTextEdit()
        desc_text.setPlainText(self.details['description'])
        desc_text.setReadOnly(True)
        content_layout.addWidget(desc_text)

        tips_label = QLabel("<b>Советы</b>")
        tips_label.setStyleSheet("font-size: 22px; margin-top: 20px;")
        content_layout.addWidget(tips_label)
        tips_text = QTextEdit()
        tips_text.setPlainText(self.details['tips'])
        tips_text.setReadOnly(True)
        content_layout.addWidget(tips_text)

        app_label = QLabel("<b>Применение</b>")
        app_label.setStyleSheet("font-size: 22px; margin-top: 20px;")
        content_layout.addWidget(app_label)
        app_text = QTextEdit()
        app_text.setPlainText(self.details['application'])
        app_text.setReadOnly(True)
        content_layout.addWidget(app_text)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("font-size: 18px; padding: 12px; margin-top: 30px;")
        close_btn.clicked.connect(self.close)
        content_layout.addWidget(close_btn)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)

class ExerciseInfoWindow(QDialog):
    def __init__(self, exercise_name, parent=None):
        super().__init__(parent)
        self.exercise_name = exercise_name
        self.details = exercises_info.get(exercise_name, {})
        if not self.details:
            self.details = {
                "technique": "Информация пока отсутствует.",
                "muscles": "Информация пока отсутствует.",
                "muscles_list": [],
                "description": "Описание пока отсутствует."
            }
        self.setWindowTitle(f"Информация: {exercise_name}")
        self.setStyleSheet(app_style)
        self.muscles_popup = None
        self.popup_anim = None
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 30, 35, 30)
        title = QLabel(self.exercise_name)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #e63946; margin-bottom: 20px;")
        main_layout.addWidget(title)

        if not self.details.get("technique"):
            no_data = QLabel(f"Информация для упражнения '{self.exercise_name}' пока отсутствует.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("font-size: 18px;")
            main_layout.addWidget(no_data)
            close_btn = QPushButton("Закрыть")
            close_btn.clicked.connect(self.close)
            main_layout.addWidget(close_btn)
            return

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(30)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1e1e1e; border-radius: 15px; padding: 15px;")
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)
        left_layout.addWidget(self.image_label)
        self.load_image()

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        technique_title = QLabel("Техника выполнения")
        technique_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e63946;")
        right_layout.addWidget(technique_title)
        self.technique_text = QTextEdit()
        self.technique_text.setReadOnly(True)
        self.technique_text.setText(self.details.get("technique", ""))
        right_layout.addWidget(self.technique_text)

        content_layout.addWidget(left_widget, 55)
        content_layout.addWidget(right_widget, 45)
        main_layout.addWidget(content_widget)

        btn_layout = QHBoxLayout()
        more_btn = QPushButton("Подробнее")
        more_btn.clicked.connect(self.open_details)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(more_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)

        self.setup_muscles_popup()

    def setup_muscles_popup(self):
        self.muscles_popup = QFrame(self)
        self.muscles_popup.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 20, 240);
                border: 2px solid #e63946;
                border-radius: 18px;
            }
            QLabel { color: white; border: none; background: transparent; }
        """)
        self.muscles_popup.resize(480, 620)
        layout = QVBoxLayout(self.muscles_popup)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        title = QLabel("Задействованные мышцы")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e63946;")
        layout.addWidget(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)
        muscles = self.details.get("muscles_list", [])
        if muscles:
            for muscle in muscles:
                card = QFrame()
                card.setStyleSheet("background-color: #2d2d2d; border-radius: 12px; padding: 0px;")
                card_layout = QVBoxLayout(card)
                card_layout.setSpacing(4)
                top = QHBoxLayout()
                top.setSpacing(8)
                color = QLabel()
                color.setFixedSize(16, 16)
                color.setStyleSheet(f"background-color: {muscle.get('color', '#e63946')}; border-radius: 8px;")
                name = QLabel(muscle.get("name", "Мышца"))
                name.setWordWrap(True)
                name.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
                top.addWidget(color)
                top.addWidget(name)
                top.addStretch()
                card_layout.addLayout(top)
                location = QLabel(muscle.get("location", ""))
                location.setWordWrap(True)
                location.setStyleSheet("font-size: 13px; color: #ddd; padding-left: 24px;")
                card_layout.addWidget(location)
                function = QLabel(muscle.get("function", ""))
                function.setWordWrap(True)
                function.setStyleSheet("font-size: 12px; color: #aaa; font-style: italic; padding-left: 24px;")
                card_layout.addWidget(function)
                content_layout.addWidget(card)
        else:
            empty = QLabel("Информация о мышцах пока отсутствует.")
            empty.setStyleSheet("font-size: 16px; color: #cccccc;")
            content_layout.addWidget(empty)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.muscles_popup.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.popup_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.popup_anim.setDuration(220)
        self.popup_anim.finished.connect(self.on_popup_animation_finished)
        self.muscles_popup.hide()

    def on_popup_animation_finished(self):
        if self.opacity_effect.opacity() == 0:
            self.muscles_popup.hide()

    def show_muscles_popup(self):
        if not self.muscles_popup:
            return
        self.muscles_popup.show()
        x = self.image_label.geometry().right() + 15
        y = self.image_label.geometry().top()
        self.muscles_popup.move(x, y)
        self.popup_anim.stop()
        self.popup_anim.setStartValue(0)
        self.popup_anim.setEndValue(1)
        self.popup_anim.start()

    def hide_muscles_popup(self):
        if not self.muscles_popup:
            return
        self.popup_anim.stop()
        self.popup_anim.setStartValue(self.opacity_effect.opacity())
        self.popup_anim.setEndValue(0)
        self.popup_anim.start()

    def eventFilter(self, obj, event):
        if obj == self.image_label:
            if event.type() == QEvent.Enter:
                self.show_muscles_popup()
            elif event.type() == QEvent.Leave:
                QTimer.singleShot(100, self.check_mouse_position)
            elif event.type() == QEvent.MouseButtonPress:
                if self.muscles_popup.isVisible():
                    self.hide_muscles_popup()
                else:
                    self.show_muscles_popup()
                return True
        return super().eventFilter(obj, event)

    def check_mouse_position(self):
        cursor_pos = QCursor.pos()
        image_rect = QRect(self.image_label.mapToGlobal(self.image_label.rect().topLeft()), self.image_label.size())
        popup_rect = QRect(self.muscles_popup.mapToGlobal(self.muscles_popup.rect().topLeft()), self.muscles_popup.size())
        if not image_rect.contains(cursor_pos) and not popup_rect.contains(cursor_pos):
            self.hide_muscles_popup()

    def load_image(self):
        safe_name = self.exercise_name.replace(" ", "").lower()
        image_path = os.path.join(os.path.dirname(__file__), "exercises", f"{safe_name}.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
                return
        self.image_label.setText("Нет изображения")

    def resizeEvent(self, event):
        self.load_image()
        super().resizeEvent(event)

    def open_details(self):
        if not self.details:
            QMessageBox.information(self, "Нет данных", f"Для упражнения '{self.exercise_name}' информация отсутствует.")
            return
        dlg = ExerciseDetailsDialog(self.details, self)
        dlg.exec_()

    def closeEvent(self, event):
        if self.popup_anim:
            self.popup_anim.stop()
        if self.muscles_popup:
            self.muscles_popup.deleteLater()
        super().closeEvent(event)

class TrainingDetailsWindow(QDialog):
    def __init__(self, training, trainings_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle(training.name)
        self.setMinimumSize(600, 500)
        self.setStyleSheet(app_style)
        self.training = training
        self.trainings_window = trainings_window
        layout = QVBoxLayout()
        self.exercise_list = QListWidget()
        self.exercise_list.itemDoubleClicked.connect(self.view_exercises_info)
        self.populate_exercise_list()
        layout.addWidget(self.exercise_list)

        buttons_layout = QHBoxLayout()
        if not training.is_predefined:
            edit_button = QPushButton("Изменить тренировку")
            edit_button.clicked.connect(self.edit_training)
            buttons_layout.addWidget(edit_button)
            delete_button = QPushButton("Удалить тренировку")
            delete_button.clicked.connect(self.delete_training)
            buttons_layout.addWidget(delete_button)
        edit_sets_button = QPushButton("Изменить подходы/повторения")
        edit_sets_button.clicked.connect(self.edit_sets_reps)
        buttons_layout.addWidget(edit_sets_button)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.showMaximized()

    def populate_exercise_list(self):
        self.exercise_list.clear()
        for exercise in self.training.exercises:
            item = QListWidgetItem(f"{exercise.name} ({exercise.muscle_group}) - {exercise.sets} x {exercise.reps}")
            item.setData(Qt.UserRole, exercise)
            self.exercise_list.addItem(item)

    def view_exercises_info(self, item):
        exercise = item.data(Qt.UserRole)
        info_window = ExerciseInfoWindow(exercise.name, self)
        info_window.exec_()

    def edit_training(self):
        edit_dialog = CreateTrainingWindow(self, training_to_edit=self.training)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.populate_exercise_list()
            self.trainings_window.refresh_trainings()

    def delete_training(self):
        if self.training.is_predefined:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить предопределённую тренировку")
            return
        msg_box = QMessageBox(QMessageBox.Question, 'Удаление тренировки',
                              f'Вы уверены, что хотите удалить тренировку "{self.training.name}"?',
                              QMessageBox.Yes | QMessageBox.No, self)
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Нет")
        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            if self.training in self.trainings_window.user_trainings:
                self.trainings_window.user_trainings.remove(self.training)
                self.trainings_window.refresh_trainings()
            self.accept()

    def edit_sets_reps(self):
        selected_items = self.exercise_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для изменения")
            return
        row = self.exercise_list.row(selected_items[0])
        exercise = self.training.exercises[row]
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменение подходов и повторений")
        dialog.setMinimumSize(400, 250)
        dialog.setStyleSheet(app_style)
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        sets_spin = QSpinBox()
        sets_spin.setRange(1, 10)
        sets_spin.setValue(exercise.sets)
        form_layout.addRow("Подходы:", sets_spin)
        reps_spin = QSpinBox()
        reps_spin.setRange(1, 30)
        reps_spin.setValue(exercise.reps)
        form_layout.addRow("Повторения:", reps_spin)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_sets_reps(exercise, sets_spin.value(), reps_spin.value(), dialog))
        buttons_layout.addWidget(save_button)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        dialog.showMaximized()
        dialog.exec_()

    def save_sets_reps(self, exercise, sets, reps, dialog):
        exercise.sets = sets
        exercise.reps = reps
        self.populate_exercise_list()
        dialog.accept()

class CreateTrainingWindow(QDialog):
    def __init__(self, parent=None, training_to_edit=None):
        super().__init__(parent)
        self.setWindowTitle("Создать тренировку" if training_to_edit is None else "Изменить тренировку")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(app_style)
        layout = QVBoxLayout()
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название тренировки:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название тренировки")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        self.exercise_list = QListWidget()
        self.exercise_list.itemDoubleClicked.connect(self.view_exercises_info)
        layout.addWidget(self.exercise_list)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить упражнение")
        add_button.clicked.connect(self.add_exercise)
        buttons_layout.addWidget(add_button)
        remove_button = QPushButton("Удалить упражнение")
        remove_button.clicked.connect(self.remove_exercise)
        buttons_layout.addWidget(remove_button)
        layout.addLayout(buttons_layout)

        save_buttons_layout = QHBoxLayout()
        done_button = QPushButton("Сохранить")
        done_button.clicked.connect(self.finish_editing)
        save_buttons_layout.addWidget(done_button)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        save_buttons_layout.addWidget(cancel_button)
        layout.addLayout(save_buttons_layout)
        self.setLayout(layout)

        if training_to_edit:
            self.training = training_to_edit
            self.name_input.setText(training_to_edit.name)
        else:
            self.training = Training("Новая тренировка")
        self.update_exercise_list()
        self.showMaximized()

    def view_exercises_info(self, item):
        exercise = item.data(Qt.UserRole)
        info_window = ExerciseInfoWindow(exercise.name, self)
        info_window.exec_()

    def add_exercise(self):
        selection_dialog = ExerciseSelectionWindow(self)
        selection_dialog.exercise_selected.connect(self.handle_exercise_selected)
        selection_dialog.exec_()

    def handle_exercise_selected(self, exercise):
        self.training.add_exercise(exercise)
        self.update_exercise_list()

    def remove_exercise(self):
        selected_items = self.exercise_list.selectedItems()
        if selected_items:
            row = self.exercise_list.row(selected_items[0])
            self.training.remove_exercise(row)
            self.update_exercise_list()

    def update_exercise_list(self):
        self.exercise_list.clear()
        for exercise in self.training.exercises:
            item = QListWidgetItem(f"{exercise.name} ({exercise.muscle_group}) - {exercise.sets} x {exercise.reps}")
            item.setData(Qt.UserRole, exercise)
            self.exercise_list.addItem(item)

    def finish_editing(self):
        name = self.name_input.text().strip()
        if not name:
            name = "Без названия"
        self.training.name = name
        if not self.training.exercises:
            msg_box = QMessageBox(QMessageBox.Question, "Пустая тренировка",
                                  "В тренировке нет упражнений. Все равно сохранить?",
                                  QMessageBox.Yes | QMessageBox.No, self)
            yes_button = msg_box.button(QMessageBox.Yes)
            yes_button.setText("Да")
            no_button = msg_box.button(QMessageBox.No)
            no_button.setText("Нет")
            reply = msg_box.exec_()
            if reply == QMessageBox.No:
                return
        self.accept()

class TrainingWidget(QFrame):
    def __init__(self, training, trainings_window, parent=None):
        super().__init__(parent)
        self.training = training
        self.trainings_window = trainings_window
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            TrainingWidget {
                background-color: #1e1e1e;
                border-radius: 12px;
                padding: 15px;
                margin: 8px;
            }
            QLabel { color: white; font-size: 15px; }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9b1b30, stop:1 #6b101e);
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b71e3a, stop:1 #851525); }
        """)
        layout = QVBoxLayout()
        title_label = QLabel(training.name)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e63946;")
        layout.addWidget(title_label)
        exercises_label = QLabel(f"Упражнений: {len(training.exercises)}")
        layout.addWidget(exercises_label)
        muscle_groups = ", ".join(sorted({ex.muscle_group for ex in training.exercises}))
        groups_label = QLabel(f"Группы мышц: {muscle_groups}")
        groups_label.setWordWrap(True)
        layout.addWidget(groups_label)
        self.view_button = QPushButton("Просмотреть")
        self.view_button.clicked.connect(self.view_training)
        layout.addWidget(self.view_button)
        self.setLayout(layout)

    def view_training(self):
        details_window = TrainingDetailsWindow(self.training, self.trainings_window, self)
        details_window.exec_()

class TrainingsWindow(QDialog):
    def __init__(self, user_trainings, current_user_id, group_workouts_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Тренировки")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(app_style)
        self.user_trainings = user_trainings
        self.current_user_id = current_user_id
        self.group_workouts_dict = group_workouts_dict
        self.current_group = UserDataStorage.load_user_group(current_user_id)
        self.init_ui()
        self.update_trainings_list()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        group_panel = QFrame()
        group_panel.setFrameShape(QFrame.StyledPanel)
        group_layout = QHBoxLayout(group_panel)
        group_layout.addWidget(QLabel("Ваш уровень и состояние ОДА:"))

        self.group_buttons = []
        self.group_button_group = QButtonGroup(self)
        for gid, info in group_info.items():
            rb = QRadioButton(info["name"])
            rb.setToolTip(info["tooltip"])
            rb.setProperty("group_id", gid)
            self.group_buttons.append(rb)
            self.group_button_group.addButton(rb, gid)
            group_layout.addWidget(rb)
            if gid == self.current_group:
                rb.setChecked(True)
        group_layout.addStretch()
        self.group_button_group.buttonClicked[int].connect(self.on_group_changed)
        layout.addWidget(group_panel)

        self.trainings_scroll = QScrollArea()
        self.trainings_scroll.setWidgetResizable(True)
        self.trainings_container = QWidget()
        self.trainings_layout = QVBoxLayout()
        self.trainings_layout.setAlignment(Qt.AlignTop)
        self.trainings_container.setLayout(self.trainings_layout)
        self.trainings_scroll.setWidget(self.trainings_container)
        layout.addWidget(self.trainings_scroll)

        buttons_layout = QHBoxLayout()
        create_button = QPushButton("Создать свою тренировку")
        create_button.clicked.connect(self.create_training)
        buttons_layout.addWidget(create_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def on_group_changed(self, group_id):
        self.current_group = group_id
        UserDataStorage.save_user_group(self.current_user_id, group_id)
        self.update_trainings_list()

    def update_trainings_list(self):
        for i in reversed(range(self.trainings_layout.count())):
            widget = self.trainings_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        group_workouts = self.group_workouts_dict.get(self.current_group, [])
        for training in group_workouts:
            widget = TrainingWidget(training, self, self)
            self.trainings_layout.addWidget(widget)
        for training in self.user_trainings:
            widget = TrainingWidget(training, self, self)
            self.trainings_layout.addWidget(widget)

    def refresh_trainings(self):
        self.update_trainings_list()

    def create_training(self):
        create_dialog = CreateTrainingWindow(self, training_to_edit=None)
        if create_dialog.exec_() == QDialog.Accepted and create_dialog.training.exercises:
            self.user_trainings.append(create_dialog.training)
            self.update_trainings_list()

    def get_user_trainings(self):
        return self.user_trainings

class BjuWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор КБЖУ и водного баланса")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(app_style)
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        self.height_input = QLineEdit()
        self.weight_input = QLineEdit()
        self.age_input = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Женщина", "Мужчина"])
        self.goal_combo = QComboBox()
        self.goal_combo.addItems(["Похудение", "Поддержание веса", "Набор массы"])
        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            "Минимальная (сидячая работа, нет спорта)",
            "Низкая (лёгкие упражнения 1-3 раза/нед.)",
            "Средняя (умеренные тренировки 3-5 раз/нед.)",
            "Высокая (тяжёлые тренировки 6-7 раз/нед.)",
            "Экстремальная (очень активная работа + тренировки)"
        ])
        self.formula_combo = QComboBox()
        self.formula_combo.addItems([
            "Формула ВОЗ",
            "Миффлин - Сан Жеор",
            "Харрис - Бенедикт",
            "Таблица ВОО"
        ])
        self.training_hours = QLineEdit()
        self.training_hours.setPlaceholderText("Часы активных занятий в день (например, 1.5)")

        form_layout.addRow("Рост (см):", self.height_input)
        form_layout.addRow("Вес (кг):", self.weight_input)
        form_layout.addRow("Возраст (лет):", self.age_input)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Цель:", self.goal_combo)
        form_layout.addRow("Уровень активности:", self.activity_combo)
        form_layout.addRow("Формула расчёта калорий:", self.formula_combo)
        form_layout.addRow("Время тренировки (часы/день):", self.training_hours)
        layout.addLayout(form_layout)

        calc_button = QPushButton("Рассчитать КБЖУ")
        calc_button.clicked.connect(self.calculate)
        layout.addWidget(calc_button)

        self.train_recommend_btn = QPushButton("Сколько тренировок в неделю мне необходимо?")
        self.train_recommend_btn.clicked.connect(self.open_training_recommendation)
        layout.addWidget(self.train_recommend_btn)

        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("background-color: #1e1e1e; padding: 15px; border-radius: 12px; font-size: 16px;")
        layout.addWidget(self.result_label)

        self.water_label = QLabel()
        self.water_label.setWordWrap(True)
        self.water_label.setStyleSheet("background-color: #1e1e1e; padding: 15px; border-radius: 12px; font-size: 16px;")
        layout.addWidget(self.water_label)

        layout.addStretch(1)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Нижние кнопки всегда видны
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

    def open_training_recommendation(self):
        try:
            age = float(self.age_input.text().strip()) if self.age_input.text().strip() else None
            weight = float(self.weight_input.text().strip()) if self.weight_input.text().strip() else None
            height_cm = float(self.height_input.text().strip()) if self.height_input.text().strip() else None
            training_time = float(self.training_hours.text().strip()) if self.training_hours.text().strip() else None
            gender = self.gender_combo.currentText()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Заполните поля возраст, вес, рост, время тренировки корректными числами.")
            return

        if None in (age, weight, height_cm, training_time):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        if age < 18 or age > 59:
            QMessageBox.warning(self, "Вне диапазона", "Нейросеть обучена на возрасте от 18 до 59 лет. Результат может быть неточным.")
        if weight < 40.4 or weight > 129.9:
            QMessageBox.warning(self, "Вне диапазона", "Вес должен быть в пределах 40.4 - 129.9 кг.")
        height_m = height_cm / 100.0
        if height_m < 1.5 or height_m > 2.0:
            QMessageBox.warning(self, "Вне диапазона", "Рост должен быть в пределах 1.5 - 2.0 м (150-200 см).")
        if training_time < 0.5 or training_time > 2.0:
            QMessageBox.warning(self, "Вне диапазона", "Длительность тренировки должна быть в пределах 0.5 - 2.0 часов.")

        dialog = TrainingRecommendationDialog(age, weight, height_m, training_time, gender, self)
        dialog.exec_()
    def get_activity_factor(self):
        idx = self.activity_combo.currentIndex()
        factors = [1.2, 1.375, 1.55, 1.7, 1.9]
        return factors[idx]

    def get_who_activity_factor(self):
        idx = self.activity_combo.currentIndex()
        if idx <= 1:
            return 1.1
        elif idx <= 2:
            return 1.3
        else:
            return 1.5

    def get_table_activity_group(self):
        idx = self.activity_combo.currentIndex()
        groups = [1.4, 1.6, 1.9, 2.2, 2.5]
        return groups[idx]

    def calculate_bmr_who(self, weight, age, gender):
        if gender == "Женщина":
            if 18 <= age <= 30:
                return (0.062 * weight + 2.036) * 240
            elif 31 <= age <= 60:
                return (0.034 * weight + 3.538) * 240
            else:
                return (0.038 * weight + 2.755) * 240
        else:
            if 18 <= age <= 30:
                return (0.063 * weight + 2.896) * 240
            elif 31 <= age <= 60:
                return (0.0484 * weight + 3.653) * 240
            else:
                return (0.0491 * weight + 2.459) * 240

    def calculate_bmr_mifflin(self, weight, height, age, gender):
        if gender == "Женщина":
            return 10 * weight + 6.25 * height - 5 * age - 161
        else:
            return 10 * weight + 6.25 * height - 5 * age + 5

    def calculate_bmr_harris(self, weight, height, age, gender):
        if gender == "Женщина":
            return 447.6 + 9.2 * weight + 3.1 * height - 4.3 * age
        else:
            return 88.36 + 13.4 * weight + 4.8 * height - 5.7 * age

    def calculate_bmr_table(self, weight, age, gender):
        if gender == "Мужчина":
            if age < 30:
                ageg = 0
            elif age < 40:
                ageg = 1
            elif age < 60:
                ageg = 2
            else:
                ageg = 3
            table = {50: [1450,1370,1280,1180], 55: [1520,1430,1350,1240], 60: [1590,1500,1410,1300],
                     65: [1670,1570,1480,1360], 70: [1750,1650,1550,1430], 75: [1830,1720,1620,1500],
                     80: [1920,1810,1700,1570], 85: [2010,1900,1780,1640], 90: [2110,1990,1870,1720]}
        else:
            if age < 30:
                ageg = 0
            elif age < 40:
                ageg = 1
            elif age < 60:
                ageg = 2
            else:
                ageg = 3
            table = {40: [1080,1050,1020,960], 45: [1150,1120,1080,1030], 50: [1230,1190,1160,1100],
                     55: [1300,1260,1220,1170], 60: [1380,1340,1300,1230], 65: [1450,1410,1370,1290],
                     70: [1530,1490,1440,1360], 75: [1600,1550,1510,1430], 80: [1680,1630,1580,1500],
                     85: [1760,1710,1650,1570], 90: [1840,1790,1730,1650]}
        weights = sorted(table.keys())
        closest = min(weights, key=lambda x: abs(x - weight))
        return table[closest][ageg]

    def calculate_tdee(self):
        try:
            height = float(self.height_input.text())
            weight = float(self.weight_input.text())
            age = int(self.age_input.text())
            gender = self.gender_combo.currentText()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числовые данные")
            return None
        formula = self.formula_combo.currentText()
        if formula == "Формула ВОЗ":
            bmr = self.calculate_bmr_who(weight, age, gender)
            act = self.get_who_activity_factor()
        elif formula == "Миффлин - Сан Жеор":
            bmr = self.calculate_bmr_mifflin(weight, height, age, gender)
            act = self.get_activity_factor()
        elif formula == "Харрис - Бенедикт":
            bmr = self.calculate_bmr_harris(weight, height, age, gender)
            act = self.get_activity_factor()
        else:
            bmr = self.calculate_bmr_table(weight, age, gender)
            act = self.get_table_activity_group()
        return bmr * act

    def get_bju_percent_ranges(self):
        goal = self.goal_combo.currentText()
        if goal == "Похудение":
            return 40, 50, 30, 40, 10, 20
        elif goal == "Набор массы":
            return 25, 35, 15, 25, 40, 60
        else:
            return 25, 35, 25, 35, 30, 50

    def calculate_water(self, weight, training_hours, gender):
        if gender == "Женщина":
            normal = weight * 0.03
        else:
            normal = weight * 0.04
        intervals = training_hours * 4
        training_water = (weight * 0.002) * intervals
        return normal, training_water

    def calculate(self):
        tdee = self.calculate_tdee()
        if tdee is None:
            return
        goal = self.goal_combo.currentText()
        if goal == "Похудение":
            cal = tdee * 0.85
        elif goal == "Набор массы":
            cal = tdee * 1.1
        else:
            cal = tdee

        p_min, p_max, f_min, f_max, c_min, c_max = self.get_bju_percent_ranges()
        p_min_g = (cal * p_min / 100) / 4
        p_max_g = (cal * p_max / 100) / 4
        f_min_g = (cal * f_min / 100) / 9
        f_max_g = (cal * f_max / 100) / 9
        c_min_g = (cal * c_min / 100) / 4
        c_max_g = (cal * c_max / 100) / 4

        try:
            weight = float(self.weight_input.text())
            hours = float(self.training_hours.text() or "0")
            gender = self.gender_combo.currentText()
        except:
            return
        nw, tw = self.calculate_water(weight, hours, gender)
        total_water = nw + tw

        self.result_label.setText(
            f"<b>Выбранная формула:</b> {self.formula_combo.currentText()}<br>"
            f"<b>Суточная калорийность ({goal.lower()}):</b> {cal:.0f} ккал<br><br>"
            f"<b>Белки:</b> {p_min_g:.1f} - {p_max_g:.1f} г<br>"
            f"<b>Жиры:</b> {f_min_g:.1f} - {f_max_g:.1f} г<br>"
            f"<b>Углеводы:</b> {c_min_g:.1f} - {c_max_g:.1f} г"
        )
        self.water_label.setText(
            f"<b>Нормы потребления воды:</b><br>"
            f"• В обычный день: {nw:.2f} л ({nw*1000:.0f} мл)<br>"
            f"• <b>В день тренировки</b> ({hours:.1f} ч): <b>общая норма {total_water:.2f} л ({total_water*1000:.0f} мл)</b><br>"
            f"  — из них дополнительно во время нагрузки: {tw:.2f} л ({tw*1000:.0f} мл)<br>"
            f"  — это ~{weight*2:.0f} мл на каждые 15 минут занятий"
        )
class TrainingRecommendationDialog(QDialog):
    def __init__(self, age, weight, height_m, training_time, gender, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Рекомендация количества тренировок")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(app_style)
        self.age = age
        self.weight = weight
        self.height_m = height_m
        self.training_time = training_time
        self.gender = gender
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()

        info_label = QLabel(
            f"Возраст: {self.age} лет\n"
            f"Вес: {self.weight} кг\n"
            f"Рост: {self.height_m*100:.0f} см\n"
            f"Тренировка: {self.training_time} ч\n"
            f"Пол: {self.gender}"
        )
        info_label.setStyleSheet("background-color: #1e1e1e; padding: 12px; border-radius: 8px; font-size: 15px;")
        layout.addWidget(info_label)
        level_hint = QLabel(
            "Градация уровней подготовки (выберите соответствующий):\n"
            "1 (Начальный) – опыт тренировок до 1 года\n"
            "2 (Средний) – регулярные тренировки от 1 года до 3 лет\n"
            "3 (Продвинутый) – опыт более 3 лет"
        )
        level_hint.setWordWrap(True)
        level_hint.setStyleSheet("background-color: #1e1e1e; padding: 12px; border-radius: 8px; font-size: 14px;")
        layout.addWidget(level_hint)

        form = QFormLayout()
        self.level_combo = QComboBox()
        self.level_combo.addItems(["1", "2", "3"])
        form.addRow("Уровень физической подготовки:", self.level_combo)
        layout.addLayout(form)

        self.calc_btn = QPushButton("Рассчитать")
        self.calc_btn.clicked.connect(self.predict)
        layout.addWidget(self.calc_btn)

        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; padding: 20px; background-color: #1e1e1e; border-radius: 12px;")
        layout.addWidget(self.result_label)


        self.setLayout(layout)

    input_hidden_weights = np.array([
        [-6.33041905184032e-001, 1.13865156256914e+000, -3.87872707431945e+000, -3.04451157015612e+000, 2.86322415170449e+000, -1.90272431442296e+001, 4.95931027078255e+000, 1.24533139198186e+000],
        [9.93618327462426e-002, -1.57075746706646e+001, -1.72520081480736e+000, -3.85255993287899e+000, -4.64865113540829e+000, -1.38703120009881e+001, 1.48036942181622e+001, -5.62607750497377e-001],
        [-2.31598011900796e-001, -1.87178657025967e+001, 2.48707664871353e+000, -3.23498889708354e+000, 6.67118503756023e+000, -3.27453585530526e+000, 4.13030041895249e+000, 9.06098801713661e-001],
        [-2.07101922018950e-001, 1.55865561096134e+000, -2.37050077542348e-001, -4.25229491233125e+000, -1.72078399348777e+000, -1.35468787513641e+001, 7.25753033660002e+000, 3.22803348560577e+000],
        [-5.15941507988509e-001, -1.20806597197374e+001, -4.94014207635664e-001, -4.33053816114158e+000, -5.98595446529427e+000, 1.02904172179105e+001, -1.07833417705926e-001, -2.19393449584699e-001]
    ])
    hidden_bias = np.array([6.10769387932994e+000, 1.42478164439492e+001, 4.99113839339137e+000, 1.04584138976264e+001, -3.57392062758126e-001])
    hidden_output_weights = np.array([
        [2.85055537728237e-001, 9.14582866867302e-001, -2.59214630964298e+000, 1.41115838917598e+000, 4.88560363000405e-001],
        [1.52780133717961e-001, -1.35308613523872e+000, 3.69793250470887e+000, -2.00228693960850e-001, -1.75051670581819e+000],
        [-7.77602980496960e-003, 9.72917974779200e-002, -7.25259777226188e-002, -4.49142759455485e+000, 3.77606186026518e-002]
    ])
    output_bias = np.array([-6.61017388462872e-002, 1.01650911567315e-001, 4.46803373581722e+000])
    max_input = np.array([59.0, 129.9, 2.0, 2.0, 49.84, 3.0])
    min_input = np.array([18.0, 40.4, 1.5, 0.5, 12.32, 1.0])

    @staticmethod
    def logistic(x):
        x = np.clip(x, -100, 100)
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    def scale_inputs(self, raw):
        scaled = np.zeros(6)
        for i in range(6):
            delta = 1.0 / (self.max_input[i] - self.min_input[i])
            scaled[i] = -delta * self.min_input[i] + delta * raw[i]
        return scaled

    def compute(self, scaled_inputs, gender_flags):
        full = np.concatenate([scaled_inputs, gender_flags])
        hidden = self.logistic(np.dot(self.input_hidden_weights, full) + self.hidden_bias)
        output = np.tanh(np.dot(self.hidden_output_weights, hidden) + self.output_bias)
        return self.softmax(output)

    def predict(self):
        level = int(self.level_combo.currentText()[0])
        bmi = self.weight / (self.height_m ** 2)
        raw = np.array([self.age, self.weight, self.height_m, self.training_time, bmi, level])
        scaled = self.scale_inputs(raw)
        gender_flags = np.array([1.0, 0.0]) if self.gender == "Женщина" else np.array([0.0, 1.0])
        probs = self.compute(scaled, gender_flags)
        pred = np.argmax(probs) + 1
        if pred == 1:
            res = "<b>Рекомендуемое количество тренировок в неделю: 2</b>"
        elif pred == 2:
            res = "<b>Рекомендуемое количество тренировок в неделю: 3</b>"
        else:
            res = "<b>Рекомендуемое количество тренировок в неделю: 4</b>"
        self.result_label.setText(res)

class ReferenceWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справочная информация")
        self.setStyleSheet(app_style)
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        sports = QTextEdit()
        sports.setReadOnly(True)
        sports.setHtml(sportpit)
        sports.setStyleSheet("background-color: #1e1e1e; border: none; padding: 12px; font-size: 15px;")
        tabs.addTab(sports, "Спортивное питание")

        period = QTextEdit()
        period.setReadOnly(True)
        period.setHtml(periodization)
        period.setStyleSheet("background-color: #1e1e1e; border: none; padding: 12px; font-size: 15px;")
        tabs.addTab(period, "Периодизация")

        balanced = QTextEdit()
        balanced.setReadOnly(True)
        balanced.setHtml(diet)
        balanced.setStyleSheet("background-color: #1e1e1e; border: none; padding: 12px; font-size: 15px;")
        tabs.addTab(balanced, "Сбалансированное питание")

        weight = QTextEdit()
        weight.setReadOnly(True)
        weight.setHtml(work_weight)
        weight.setStyleSheet("background-color: #1e1e1e; border: none; padding: 12px; font-size: 15px;")
        tabs.addTab(weight, "Рабочий вес")
        layout.addWidget(tabs, 1)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

class GigaChatWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, auth_key, messages_history, new_question):
        super().__init__()
        self.auth_key = auth_key
        self.messages_history = messages_history
        self.new_question = new_question
        self._is_cancelled = False
        self._access_token = None
        self._token_expires_at = 0

    def cancel(self):
        self._is_cancelled = True

    def _get_access_token(self):
        now = time.time()
        if self._access_token and now < self._token_expires_at - 60:
            return self._access_token
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {"scope": "GIGACHAT_API_PERS"}
        resp = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"Ошибка получения токена: {resp.text}")
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expires_at = data.get("expires_at", 0) / 1000.0
        return self._access_token

    def run(self):
        try:
            if self._is_cancelled:
                return
            token = self._get_access_token()
            if self._is_cancelled:
                return

            history = self.messages_history.copy()
            history.append({"role": "user", "content": self.new_question})

            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {
                "RqUID": str(uuid.uuid4()),
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "GigaChat",
                "messages": history,
                "stream": False
            }
            resp = requests.post(url, headers=headers, json=payload, verify=False, timeout=60)
            if self._is_cancelled:
                return
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"]
                self.finished.emit(answer)
            else:
                self.error.emit(f"Ошибка API: {resp.status_code} - {resp.text}")
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(f"Ошибка: {str(e)}")


class GigaChatWidget(QDialog):
    def __init__(self, authorization_key, external_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ИИ фитнес-тренер")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(app_style)
        self.authorization_key = authorization_key
        self.worker = None
        self.last_question = ""
        self.system_prompt = {
            "role": "system",
            "content": "Ты — опытный фитнес-тренер. Отвечай на вопросы пользователя строго на русском языке, "
            "избегай любых вставок на других языках. Все аббревиатуры и специализированные термины всегда расшифровывай. "
            "Давай рекомендации, основанные на научных данных и проверенных методиках. Если не уверен в ответе — так и скажи."
            "Указывай на возможные противопоказания, даже если пользователь их не дал."
        }
        self.conversation_messages = external_history
        if not self.conversation_messages:
            self.conversation_messages.append(self.system_prompt)
        self.init_ui()
        self.restore_display_from_history()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Напишите ваш вопрос...")
        self.input_field.returnPressed.connect(self.send_request)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_request)
        input_layout.addWidget(self.send_button)

        self.help_button = QPushButton("❓ Подсказка")
        self.help_button.clicked.connect(self.show_help)
        input_layout.addWidget(self.help_button)

        self.help_button.setAutoDefault(False)
        self.help_button.setDefault(False)

        layout.addLayout(input_layout)
        self.clear_button = QPushButton("Очистить историю")
        self.clear_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_button)
        self.setLayout(layout)

    def show_help(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Как задавать вопросы")
        help_dialog.setStyleSheet(app_style)
        help_dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(help_dialog)

        text = QLabel(
            "• Не используйте общие фразы вроде «как мне похудеть», «напиши план тренировок» или «что есть на ужин».\n\n"
            "• Указывайте исходные данные: пол, рост, вес, травмы, болезни, предпочтения в еде и графике, опыт тренировок.\n\n"
            "• Если вы не разбираетесь в теме, попросите нейросеть сначала задать уточняющие вопросы.\n\n"
            "• Уточняйте ответы и добавляйте больше информации.\n\n"
            "• Попросите объяснить логику рекомендаций.\n\n"
            "• По возможности показывайте рекомендации тренеру или специалисту по питанию, просите дать им оценку.\n\n"
            "• Всегда помните: алгоритмы могут ошибаться."
        )
        text.setWordWrap(True)
        text.setStyleSheet("font-size: 16px; padding: 20px;")
        layout.addWidget(text)

        close_btn = QPushButton("Понятно")
        close_btn.clicked.connect(help_dialog.accept)
        layout.addWidget(close_btn)

        effect = QGraphicsOpacityEffect()
        help_dialog.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()

        help_dialog.exec_()

    def restore_display_from_history(self):
        self.chat_display.clear()
        for msg in self.conversation_messages:
            if msg.get("role") == "system":
                continue
            sender = "Вы" if msg["role"] == "user" else "Фитнес-тренер"
            color = "#e63946" if sender == "Фитнес-тренер" else "#aaaaaa"
            self.chat_display.append(f'<b><span style="color:{color};">{sender}:</span></b> {msg["content"]}')

    def add_message_to_display(self, sender, message):
        color = "#e63946" if sender == "Фитнес-тренер" else "#aaaaaa"
        self.chat_display.append(f'<b><span style="color:{color};">{sender}:</span></b> {message}')

    def send_request(self):
        question = self.input_field.text().strip()
        if not question:
            QMessageBox.warning(self, "Пустой запрос", "Введите текст вопроса.")
            return

        self.last_question = question
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.help_button.setEnabled(False)
        self.input_field.setEnabled(False)

        self.add_message_to_display("Вы", question)
        self.add_message_to_display("Фитнес-тренер", "Печатает...")

        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.quit()
            self.worker.wait(3000)

        self.worker = GigaChatWorker(self.authorization_key, self.conversation_messages, question)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, answer):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        self.add_message_to_display("Фитнес-тренер", answer)
        self.conversation_messages.append({"role": "user", "content": self.last_question})
        self.conversation_messages.append({"role": "assistant", "content": answer})

        self.send_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.help_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.worker = None

    def on_error(self, error_msg):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.movePosition(cursor.StartOfBlock, cursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        self.add_message_to_display("Фитнес-тренер", f"Ошибка: {error_msg}")
        self.send_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.help_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.worker = None

    def clear_history(self):
        self.conversation_messages.clear()
        self.conversation_messages.append(self.system_prompt)
        self.chat_display.clear()
        self.add_message_to_display("Фитнес-тренер", "История диалога очищена. Задайте новый вопрос.")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.quit()
            self.worker.wait(5000)
        self.worker = None
        event.accept()

class FitnessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фитнес-приложение")
        self.setStyleSheet(app_style)
        self.setMinimumSize(600, 400)
        self.current_user_id = None
        self.current_username = None
        self.custom_trainings = []
        self.gigachat_history = []
        self.init_ui()
        self.group_workouts = create_group_workouts()
        self.do_login()
        self.showMaximized()

    def init_ui(self):
        layout = QVBoxLayout()
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.setFixedSize(90, 40)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #e63946;
                border: 1px solid #e63946;
                font-size: 14px;
                border-radius: 4px;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(230, 57, 70, 0.2);
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(self.logout_btn)
        layout.addLayout(top_bar)
        layout.setSpacing(25)
        self.title_label = QLabel("Фитнес-приложение")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 52px; font-weight: bold; color: #e63946; letter-spacing: 5px; margin: 30px 0;")
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.trainings_btn = QPushButton("Тренировки")
        self.trainings_btn.setStyleSheet("font-size: 22px; padding: 20px;")
        self.trainings_btn.clicked.connect(self.open_trainings)
        layout.addWidget(self.trainings_btn)

        self.bju_btn = QPushButton("Калькулятор БЖУ")
        self.bju_btn.setStyleSheet("font-size: 22px; padding: 20px;")
        self.bju_btn.clicked.connect(self.open_bju)
        layout.addWidget(self.bju_btn)

        self.reference_btn = QPushButton("Справочная информация")
        self.reference_btn.setStyleSheet("font-size: 22px; padding: 20px;")
        self.reference_btn.clicked.connect(self.open_reference)
        layout.addWidget(self.reference_btn)

        self.gigachat_btn = QPushButton("ИИ-помощник")
        self.gigachat_btn.setStyleSheet("font-size: 22px; padding: 20px;")
        self.gigachat_btn.clicked.connect(self.open_gigachat)
        layout.addWidget(self.gigachat_btn)

        layout.addStretch(1)

        self.setLayout(layout)

    def do_login(self):
        login_dlg = LoginDialog(self)
        if login_dlg.exec_() == QDialog.Accepted:
            self.current_user_id = login_dlg.result_user_id
            self.current_username = login_dlg.logged_username
            if self.current_user_id is not None:
                self.custom_trainings = UserDataStorage.load_trainings(self.current_user_id)
                self.gigachat_history = UserDataStorage.load_gigachat_history(self.current_user_id)
            else:
                self.custom_trainings = []
                self.gigachat_history = []
                self.current_username = None
            self.update_title()
            return True
        else:
            return False

    def update_title(self):
        if self.current_user_id is None:
            self.setWindowTitle("Фитнес-приложение")
            self.title_label.setText("Фитнес-приложение")
        else:
            self.setWindowTitle("Фитнес-приложение")
            if self.current_username:
                self.title_label.setText(f"Здравствуйте, {self.current_username}")
            else:
                self.title_label.setText("Фитнес-приложение")

    def logout(self):
        self.save_current_user_data()
        self.current_user_id = None
        self.custom_trainings = []
        self.gigachat_history = []
        if not self.do_login():
            self.close()

    def save_current_user_data(self):
        if self.current_user_id is not None:
            UserDataStorage.save_trainings(self.current_user_id, self.custom_trainings)
            UserDataStorage.save_gigachat_history(self.current_user_id, self.gigachat_history)

    def closeEvent(self, event):
        self.save_current_user_data()
        for child in self.findChildren(QDialog):
            if child.isVisible():
                child.close()
        event.accept()

    def open_trainings(self):
        trainings_window = TrainingsWindow(self.custom_trainings, self.current_user_id, self.group_workouts, self)
        if trainings_window.exec_() == QDialog.Accepted:
            self.custom_trainings = trainings_window.get_user_trainings()
            self.save_current_user_data()

    def open_bju(self):
        bju_window = BjuWindow()
        bju_window.exec_()

    def open_reference(self):
        reference_window = ReferenceWindow()
        reference_window.exec_()

    def open_gigachat(self):
        authorization_key = "MDE5ZDk2NmUtNGRiNC03YjRjLWE2ZmMtNjExMjA3OWVhNjhjOmZlMjZiMGE5LWFkZmItNGQwZC1hMDA4LTE0ZDhkOTIwMGUxYQ=="
        gigachat_window = GigaChatWidget(authorization_key, self.gigachat_history, self)
        gigachat_window.exec_()
        self.save_current_user_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font_db = QFontDatabase()
    bold_id = font_db.addApplicationFont("fonts/Montserrat-Light.ttf")
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(18, 18, 18))
    pal.setColor(QPalette.WindowText, Qt.white)
    pal.setColor(QPalette.Base, QColor(30, 30, 30))
    pal.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    pal.setColor(QPalette.Text, Qt.white)
    pal.setColor(QPalette.Button, QColor(53, 53, 53))
    pal.setColor(QPalette.ButtonText, Qt.white)
    pal.setColor(QPalette.Highlight, QColor(230, 57, 70))
    app.setPalette(pal)
    window = FitnessApp()
    window.show()
    sys.exit(app.exec_())