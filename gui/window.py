import os
import sys
import webbrowser

# import cv2 # uncomment if using raspberry pi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from easyocr import Reader

from gui.camera import Worker
from gui.canvas import Canvas
# from printer import linedraw  # uncomment if using raspberry pi


class MainWindow(QMainWindow):
    valueChanged = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        # setting geometry
        self.setGeometry(100, 50, 1400, 600)
        # fixing the geometry
        self.setFixedSize(1400, 600)

        # setting window title
        self.setWindowTitle("Personal Note Writer")

        self.thread = False

        self.valueChanged.connect(self.on_value_changed)
        self.start_state = True

        # setting style sheet
        self.base_path = os.getcwd()
        oImage = QImage(os.path.join(self.base_path, 'images/background.png'))
        sImage = oImage.scaled(QSize(1400, 600))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        # setting the cursor
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # creating a status bar
        self.statusBar().showMessage('Welcome to Personal Note Writer!')
        self.statusBar().addPermanentWidget(QLabel("MIT License   "))

        # path to save
        self.save_path = ""

        self.setFocusPolicy(Qt.StrongFocus)

        self.main_layout()

        self.create_menu()

        self.create_toolbar()

        # showing the main window
        self.show()

    def create_menu(self):
        # creating menu
        file_menu = self.menuBar().addMenu('File')
        edit_menu = self.menuBar().addMenu('Edit')
        # options_menu = self.menuBar().addMenu('Options')
        help_menu = self.menuBar().addMenu('Help')

        # actions for file menu
        self.open_action = file_menu.addAction('Open', lambda: self.change_status("Opened!"))
        self.save_action = file_menu.addAction('Save', lambda: self.change_status("Saved!"))
        self.quit_action = file_menu.addAction('Quit', self.destroy)

        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)

        # actions for edit menu
        edit_menu.addAction('Copy', self.textEdit.copy)
        redo_action = QAction('Redo', self)
        redo_action.triggered.connect(self.textEdit.redo)
        edit_menu.addAction(redo_action)
        edit_menu.addAction('Clear', self.window_clear)

        # actions for help menu
        help_menu.addAction('About', self.about_dialog)
        help_menu.addAction('Contribute', self.contrib_dialog)
        help_menu.addAction('Visit Website!', self.open_website)

        # State Machine for Modes
        self.machine = QStateMachine()
        self.math_state = QState()
        self.math_state.assignProperty(self.math_mode, 'text', 'Math Mode')
        self.text_state = QState()
        self.text_state.assignProperty(self.text_mode, 'text', 'Text Mode')

        self.text_state.addTransition(self.math_mode.clicked, self.math_state)
        self.math_state.addTransition(self.text_mode.clicked, self.text_state)

        self.machine.addState(self.math_state)
        self.machine.addState(self.text_state)
        self.machine.setInitialState(self.text_state)
        self.machine.start()

    def create_toolbar(self):
        toolbar = self.addToolBar('File')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(Qt.TopToolBarArea)

        open_icon = QIcon(os.path.join(self.base_path, 'images/new.svg'))
        save_icon = QIcon(os.path.join(self.base_path, 'images/save.svg'))
        erase_icon = QIcon(os.path.join(self.base_path, 'images/eraser.svg'))
        pen_icon = QIcon(os.path.join(self.base_path, 'images/pen.svg'))
        stop_icon = QIcon(os.path.join(self.base_path, 'images/stop.svg'))
        write_icon = QIcon(os.path.join(self.base_path, 'images/draw.svg'))
        clear_icon = QIcon(os.path.join(self.base_path, 'images/clear.svg'))

        self.open_action.setIcon(open_icon)
        self.save_action.setIcon(save_icon)

        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)

        # write toolbar
        write_toolbar = QToolBar('Writer')
        write_action = QAction('Write', self)
        write_action.triggered.connect(self.canvas.write_back)
        write_action.triggered.connect(self.start_camera)
        write_action.setShortcut("Shift+D")
        write_action.setIcon(write_icon)
        write_toolbar.addAction(write_action)

        stop_write = QAction('Stop', self)
        stop_write.triggered.connect(self.canvas.write_stop)
        stop_write.triggered.connect(self.stop_camera)
        stop_write.setShortcut("Shift+S")
        stop_write.setIcon(stop_icon)
        write_toolbar.addAction(stop_write)

        # Pen Action
        pen_action = QAction('Pen', self)
        pen_action.triggered.connect(self.canvas.set_pen)
        pen_action.setShortcut("Shift+P")
        pen_action.setIcon(pen_icon)
        write_toolbar.addAction(pen_action)

        # Erase Action
        erase_action = QAction('Eraser', self)
        erase_action.triggered.connect(self.canvas.set_erase)
        erase_action.setShortcut("Shift+E")
        erase_action.setIcon(erase_icon)
        write_toolbar.addAction(erase_action)

        # Clear Action
        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.window_clear)
        clear_action.setShortcut("Shift+A")
        clear_action.setIcon(clear_icon)
        write_toolbar.addAction(clear_action)

        self.addToolBar(Qt.LeftToolBarArea, write_toolbar)

    def open_website(self):
        webbrowser.open("https://skovira.ece.cornell.edu/ece5725/")

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select a image file to open…", QDir.homePath(),
                                                  'Image Files (*.png, *.jpg, *.jpeg) ;;All Files (*)',
                                                  'Image Files (*png, *jpg, *jpeg)',
                                                  QFileDialog.DontResolveSymlinks)
        if filename:
            try:
                self.canvas.open_image(filename)
            except Exception as e:
                QMessageBox.critical(f"Could not load file: {e}")

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Select the file to save to…", QDir.homePath(),
                                                  'Image Files (*png, *jpg, *jpeg) ;;All Files (*)')
        if filename:
            try:
                self.canvas.save_image(filename)
            except Exception as e:
                QMessageBox.critical(f"Could not save file: {e}")

    def main_layout(self):

        # Camera
        self.camera_feed = QLabel()
        self.camera_feed.setObjectName("Video Stream")

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color :rgb(92,184,92);")
        self.start_button.clicked.connect(self.start_camera)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color : rgb(217, 83, 79)")
        self.stop_button.clicked.connect(self.stop_camera)

        # Different Modes
        self.print_mode = QPushButton("Print")
        self.print_mode.setStyleSheet("background-color :rgb(100, 149, 237);")
        self.print_mode.clicked.connect(lambda: self.change_status('Printing...'))
        self.print_mode.clicked.connect(self.print_image)

        self.math_mode = QPushButton("Math Mode")
        self.math_mode.setStyleSheet("background-color :rgb(234,182,118);")
        self.math_mode.clicked.connect(lambda: self.change_status('Math Mode'))

        self.text_mode = QPushButton("Text Mode")
        self.text_mode.clicked.connect(lambda: self.change_status('Text Mode'))
        self.text_mode.setStyleSheet("background-color : rgb(236, 233, 224)")

        # Canvas
        self.canvas = Canvas()
        self.result_button = QPushButton("Get Result")
        self.result_button.setStyleSheet("background-color :rgb(91, 192, 222);")
        self.result_button.clicked.connect(self.get_result)

        # Output
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        font = QFont()
        font.setPointSize(20)
        self.textEdit.setFont(font)

        # Creating layouts
        # Camera Layout
        camera_layout = QVBoxLayout()
        camera_layout.setAlignment(Qt.AlignTop)
        camera_layout.addWidget(self.camera_feed)
        camera_layout.addWidget(self.start_button)
        camera_layout.addWidget(self.stop_button)
        camera_layout.insertSpacing(10, 150)
        camera_layout.addWidget(self.print_mode)
        camera_layout.insertSpacing(10, 40)
        camera_layout.addWidget(self.math_mode)
        camera_layout.insertSpacing(10, 20)
        camera_layout.addWidget(self.text_mode)

        camera_frame = QFrame()
        camera_frame.setMinimumWidth(200)
        camera_frame.setLayout(camera_layout)

        # Canvas layout
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addWidget(self.result_button)
        canvas_frame = QFrame()
        canvas_frame.setMinimumWidth(500)
        canvas_frame.setLayout(canvas_layout)

        # Text Output
        text_layout = QVBoxLayout()
        text_layout.addWidget(self.textEdit)
        text_frame = QFrame()
        text_frame.setMinimumWidth(400)
        text_frame.setLayout(text_layout)

        # Combine
        main_layout = QHBoxLayout()
        main_layout.addWidget(camera_frame, 1)
        main_layout.addWidget(canvas_frame)
        main_layout.addWidget(text_frame)

        # making it central widget of main window
        container = QWidget(self)
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        container.layout().activate()

    def about_dialog(self):
        QMessageBox.about(self, "About", "This is a Personal Note Writer created at Cornell University")

    def contrib_dialog(self):
        QMessageBox.about(self, "Contribute", "Please check the GitHub repository")

    def change_status(self, text):
        self.statusBar().showMessage(text)

    def print_image(self):
        # uncomment if using raspberry pi
        # image = self.canvas.get_array()
        # cv2.imwrite(os.path.join(os.getcwd(), 'images'), image)
        # lines = linedraw.sketch(r"/home/pi/Project/Personal-Writer/printer/img.jpg")
        # linedraw.print_drawing(lines)
        pass

    def start_camera(self):
        self.thread = True
        self.start_button.setEnabled(False)
        self.start_button.repaint()
        self.camera = Worker()
        self.camera.frameData.connect(self.update_camera)
        self.camera.noFinger.connect(self.move_cursor)
        self.camera.clearGesture.connect(self.canvas.clear)
        self.canvas.write_back()
        self.camera.start()

    def stop_camera(self):
        if self.thread:
            self.thread = False
            self.camera.stop()
            self.start_button.setEnabled(True)
            self.canvas.write_stop()

    def window_clear(self):
        self.canvas.clear()
        self.textEdit.setText('')

    def update_camera(self, image):
        # update the camera
        height, width, channels = image.shape
        image_to_qt = QImage(image, width, height, width * channels, QImage.Format_RGB888)
        imageqt = QPixmap.fromImage(image_to_qt)
        imageqt = imageqt.scaled(self.camera_feed.width(), self.camera_feed.height(), Qt.KeepAspectRatioByExpanding)
        self.camera_feed.setPixmap(imageqt)

    def get_result(self):
        # Get the result
        image = self.canvas.get_array()
        reader = Reader(['en'])
        results = reader.readtext(image)
        output = []
        try:
            for res in results:
                rect, out, conf = res
                out = out.replace(' ', '')
                TopLeft, TopRight, BotLeft, _ = rect
                width = TopRight[0] - TopLeft[0]
                height = BotLeft[1] - TopLeft[1]
                self.canvas.draw_bounding_box(TopLeft[0], TopLeft[1], width, height, conf)
                output.append(out)
        except Exception:
            self.valueChanged.emit('Please draw something \U0001F440\n!')
        else:
            if self.math_state in self.machine.configuration():
                ans = []
                for expr in output:
                    expr = expr.lower()
                    math_expr = expr.replace(' ', '')
                    math_expr = math_expr.replace('x', '*')
                    math_expr = math_expr.replace('X', '*')
                    try:
                        ans.append(expr + ' = ' + str(eval(math_expr)) + '! \U0001f947')
                    except Exception:
                        ans.append('Unable to evaluate the expression: ' + expr + ' \U0001F440\nPlease try again!')
                self.valueChanged.emit(ans)
            else:
                self.valueChanged.emit(output)

    def move_cursor(self, trigger):
        if trigger and self.canvas.drawing:
            self.canvas.drawing = False
            self.start_state = False
        elif not self.start_state and not trigger:
            self.canvas.write_back()

    def on_value_changed(self, output):
        if isinstance(output, list):
            value = '\n\n'.join([out for out in output])
            self.textEdit.setText(value)

    # method for alerts
    def alert(self, msg):

        # error message
        error = QErrorMessage(self)

        # setting text to the error message
        error.showMessage(msg)


def main():
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(os.path.join(os.getcwd(), 'images/icon.png')))

    # create the instance of our Window
    window = MainWindow()

    # start the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
