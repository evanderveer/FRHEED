# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QSplashScreen, QWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap

from frheed.widgets.rheed_widgets import RHEEDWidget
from frheed.widgets.plot_widgets import PlotGridWidget
#from frheed.widgets.splash_screen import SplashScreenWidget
from frheed import utils
# from frheed import settings
from functools import partial


logger = utils.get_logger()

# Fix IPython and PyQt
utils.fix_ipython()
utils.fix_pyqt()


class FRHEED(QMainWindow):
    def __init__(self):
        
        # Get application BEFORE initializing
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Initialize window
        super().__init__(parent=None)
         
        
        # Show a splash screen while the app is loading
        self.splash_screen_widget = QSplashScreen(QPixmap("resources/icons/frheed.png"))
        self.splash_screen_widget.show()
        self.splash_screen_widget.raise_()
        
        # Create the main widget
        self.rheed_widget = RHEEDWidget()
        #self.plot_widget = PlotGridWidget()
        
        self.setCentralWidget(self.rheed_widget)
        
        # Close the splash screen once the rheed_widget is ready
        self.splash_screen_widget.close()
        
        # Connect signals
        self.app.lastWindowClosed.connect(self.quit_app)
        
        # Set window properties
        self.setWindowTitle("FRHEED")
        self.setWindowIcon(utils.get_icon("FRHEED"))
        
        # Show the window and center in the screen
        self.show()
        utils.fit_screen(self)
        
        # Start blocking event loop that ends when app is closed
        sys.exit(self.app.exec())
        
    @pyqtSlot()
    def quit_app(self):
        self.app.quit()

def show() -> FRHEED:
    logger.info("Opening FRHEED...")
    
    # This should prevent the window being garbage collected
    main_window = FRHEED()
    return(main_window)


if __name__ == "__main__":
    gui = show()
    