import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Création des widgets
        self.label1 = QLabel("Fenêtre 1")
        self.button1 = QPushButton("Ouvrir Fenêtre 1", self)

        self.label2 = QLabel("Fenêtre 2")
        self.button2 = QPushButton("Ouvrir Fenêtre 2", self)

        self.input1 = QLineEdit(self)
        self.input2 = QLineEdit(self)
        self.input3 = QLineEdit(self)
        self.input4 = QLineEdit(self)
        self.input5 = QLineEdit(self)

        # Mise en place de la disposition
        layout = QVBoxLayout(self)
        layout.addWidget(self.label1)
        layout.addWidget(self.button1)
        layout.addWidget(self.label2)
        layout.addWidget(self.button2)
        layout.addWidget(self.input1)
        layout.addWidget(self.input2)
        layout.addWidget(self.input3)
        layout.addWidget(self.input4)
        layout.addWidget(self.input5)

        # Configuration des signaux et slots
        self.button1.clicked.connect(self.open_window1)
        self.button2.clicked.connect(self.open_window2)

    def open_window1(self):
        window1 = MyDialog("Fenêtre 1", self)
        window1.exec_()

    def open_window2(self):
        window2 = MyDialog("Fenêtre 2", self)
        window2.exec_()


class MyDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        # Création des widgets
        self.label = QLabel(f"Contenu de {title}")
        self.input = QLineEdit(self)
        self.button = QPushButton("Fermer", self)

        # Mise en place de la disposition
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        # Configuration des signaux et slots
        self.button.clicked.connect(self.accept)

    def accept(self):
        # Action à effectuer lors de la fermeture de la fenêtre
        self.label.setText(f"Contenu de {self.windowTitle()}:\n{self.input.text()}")
        super().accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
