import sys
import os
import config
import openai

from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtGui import QPainter, QPixmap, QFontMetrics, QBrush, QColor, QPainterPath, QFontDatabase, QFont
from PySide6.QtCore import Qt, QTimer, QUrl, QRect
from PySide6.QtMultimedia import QSoundEffect

from Logic import AiBestie  # ✅ Use your custom personality class

openai.api_key = config.OPENAI_API_KEY

ASSETS_DIR = r"C:\Users\NeyyN\Desktop\Programming\vs\Assets"

# ---- Use Installed System Font ----
custom_font = QFont("Pixel Operator", 14)  # Use installed font directly

def load_pixmap(filename):
    path = os.path.normpath(os.path.join(ASSETS_DIR, filename))
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return QPixmap()
    pixmap = QPixmap(path)
    if pixmap.isNull():
        print(f"Failed to load pixmap: {path}")
    return pixmap


class ChatBubble(QWidget):
    def __init__(self, text, icon_file, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.icon = load_pixmap(icon_file)
        self.ellipse_size = 32
        self.text = text

        metrics = QFontMetrics(custom_font)
        rect = metrics.boundingRect(0, 0, 280, 1000, Qt.TextWordWrap, text)
        self.bubble_width = rect.width() + 40
        self.bubble_height = rect.height() + 30

        self.setFixedHeight(self.bubble_height + 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(custom_font)

        margin = 10
        avatar_y = self.height() - self.ellipse_size

        if self.is_user:
            avatar_x = margin
            bubble_x = avatar_x + self.ellipse_size + 10
            text_color = Qt.black
            bubble_color = QColor("#C9C0BB")
        else:
            avatar_x = self.width() - self.ellipse_size - margin
            bubble_x = avatar_x - self.bubble_width - 10
            text_color = Qt.black
            bubble_color = QColor("#E3E4FA")

        bubble_y = margin

        path = QPainterPath()
        path.addRoundedRect(bubble_x, bubble_y, self.bubble_width, self.bubble_height, 15, 15)
        painter.fillPath(path, bubble_color)

        painter.setPen(text_color)
        painter.drawText(
            QRect(bubble_x + 15, bubble_y + 10, self.bubble_width - 30, self.bubble_height - 20),
            Qt.TextWordWrap, self.text
        )

        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(avatar_x, avatar_y, self.ellipse_size, self.ellipse_size)

        if not self.icon.isNull():
            icon_size = int(self.ellipse_size * 0.8)
            offset = (self.ellipse_size - icon_size) // 2
            scaled_icon = self.icon.scaled(icon_size, icon_size,
                                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(avatar_x + offset, avatar_y + offset, scaled_icon)


class SoundLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound = QSoundEffect()
        click_path = os.path.join(ASSETS_DIR, "click.wav")
        if os.path.exists(click_path):
            self.sound.setSource(QUrl.fromLocalFile(click_path))
            self.sound.setVolume(0.5)

        self.setFont(custom_font)

    def keyPressEvent(self, event):
        if event.key() not in (Qt.Key_Return, Qt.Key_Enter):
            if self.sound.source().isValid():
                self.sound.play()
        super().keyPressEvent(event)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BestieAI")
        self.resize(500, 600)

        self.background = load_pixmap("background.jpg")

        self.bestie = AiBestie()

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 50)

        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Input box
        self.input_box = SoundLineEdit(self)
        self.input_box.setPlaceholderText("Tell me your troubles dear <3")
        self.input_box.setStyleSheet(
            "font-size:15px; padding:10px; border-radius:10px; border:2px solid #A6A788; background:white; color:black;"
        )
        self.layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.send_message)

    def add_user_bubble(self, text):
        bubble = ChatBubble(text, "user_icon.png", True)
        self.scroll_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def add_ai_bubble(self, text):
        bubble = ChatBubble(text, "ai_icon.png", False)
        self.scroll_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return
        self.input_box.clear()
        self.add_user_bubble(text)

        QTimer.singleShot(500, lambda: self.get_ai_reply(text))

    def get_ai_reply(self, user_text):
        """Use AiBestie personality instead of raw OpenAI calls"""
        ai_text = self.bestie.talk(user_text)
        self.add_ai_bubble(ai_text)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)
        else:
            painter.fillRect(self.rect(), QColor("#CCCCCC"))


def run_gui():
    app = QApplication(sys.argv)
    app.setFont(custom_font)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
