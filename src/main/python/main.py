import logging
import os
import subprocess
import sys
from os.path import expanduser

from PyQt5 import QtWidgets
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QApplication
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.platform import is_windows, is_mac

from gui.open_playlist import Ui_MainWindow
from set_default_arrangement import set_default_arrangements

DETACHED_PROCESS = 8

home = expanduser('~')
if is_windows():
    log_filepath = os.path.join(home, 'AppData\\Local\\open-pro6plx')
else:
    log_filepath = os.path.join(home, 'Library/Logs/open-pro6plx')
os.makedirs(log_filepath, exist_ok=True)
log_filename = os.path.join(log_filepath, 'debug.log')
logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO)

logger = logging.getLogger()


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
    logger.info('open_playlist...')

    try:
        set_default_arrangements(path_to_playlist)
    except Exception as e:
        logger.error("open_playlist - Cannot set default arrangements: %s" % str(e))

    try:
        if is_windows():
            path_to_propresenter = "C:\\Program Files (x86)\\Renewed Vision\\ProPresenter 6\\ProPresenter.exe"
            subprocess.Popen([path_to_propresenter, path_to_playlist], creationflags=DETACHED_PROCESS)
        elif is_mac():
            path_to_propresenter = "/Applications/ProPresenter 6.app"
            subprocess.Popen([path_to_propresenter, path_to_playlist])
    except Exception as e:
        logger.error('open_playlist - Cannot open playlist: %s' % str(e))


def quickstart(path=None):
    logger.info('quickstart...')
    path_to_playlist = path or (sys.argv[1] if len(sys.argv) > 1 else None)
    logger.info('quickstart - path_to_playlist is %s' % path_to_playlist)
    if path_to_playlist and os.path.exists(path_to_playlist):
        open_playlist(path_to_playlist)
        window.close()
    else:
        logger.error('quickstart - No path or path not valid.')


def enable_file_drag(line_edit: QLineEdit) -> None:
    logger.info('enable_file_drag...')

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


def enable_open_with():
    logger.info('enable_open_with...')

    def event(e: QEvent) -> bool:
        if e.type() == QEvent.FileOpen:
            quickstart(e.file())
        return QApplication.event(appctxt.app, e)

    appctxt.app.event = event


if __name__ == '__main__':
    logger.info('open-pro6plx started.')
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext

    if is_mac():
        enable_open_with()

    window = MainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    enable_file_drag(ui.lineEdit)
    window.show()

    if is_windows():
        quickstart()

    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    logger.info('open-pro6plx closed with exit code %s' % exit_code)
    sys.exit(exit_code)
