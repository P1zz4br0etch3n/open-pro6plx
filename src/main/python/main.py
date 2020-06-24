import os
import subprocess
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QMainWindow, QLineEdit
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.platform import is_windows, is_mac

from gui.open_playlist import Ui_MainWindow
from set_default_arrangement import set_default_arrangements

DETACHED_PROCESS = 8


class MainWindow(QMainWindow):

    @staticmethod
    def browse_slot():
        file_name, _ = QtWidgets.QFileDialog().getOpenFileName(filter='*.pro6plx')
        if file_name:
            ui.lineEdit.setText(file_name)

    def open_slot(self):
        path_to_playlist = ui.lineEdit.text()
        if os.path.exists(path_to_playlist):
            open_playlist(path_to_playlist)
            self.close()


def open_playlist(path_to_playlist):
    set_default_arrangements(path_to_playlist)
    if is_windows():
        path_to_propresenter = "C:\\Program Files (x86)\\Renewed Vision\\ProPresenter 6\\ProPresenter.exe"
        subprocess.Popen([path_to_propresenter, path_to_playlist], creationflags=DETACHED_PROCESS)
    elif is_mac():
        path_to_propresenter = "/Applications/ProPresenter 6.app/Contents/MacOS/ProPresenter 6"
        subprocess.Popen([path_to_propresenter, path_to_playlist])


def quickstart():
    path_to_playlist = sys.argv[1] if len(sys.argv) > 1 else None
    if path_to_playlist and os.path.exists(path_to_playlist):
        open_playlist(path_to_playlist)
        window.close()


def enable_file_drag(line_edit: QLineEdit) -> None:
    line_edit.setDragEnabled(True)

    def drag_enter_event(event: QDragEnterEvent) -> None:
        data = event.mimeData()
        url = data.urls()[0]
        if url and url.isLocalFile() and url.fileName().endswith('.pro6plx'):
            event.acceptProposedAction()

    def drop_event(event: QDropEvent) -> None:
        data = event.mimeData()
        url = data.urls()[0]
        if url and url.isLocalFile() and url.fileName().endswith('.pro6plx'):
            line_edit.setText(url.toLocalFile())

    line_edit.dragEnterEvent = drag_enter_event
    line_edit.dropEvent = drop_event


if __name__ == '__main__':

    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    window = MainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    enable_file_drag(ui.lineEdit)
    window.show()

    quickstart()

    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
