# -*- coding: utf-8 -*-
"""
Widgets for RHEED analysis.
"""

from typing import Union
from functools import partial

from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QSizePolicy,
    QPushButton,
    QSplitter,
    QSpacerItem,
    QMenuBar,
    QMenu,
    QFileDialog
    
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
    
    )

from frheed.widgets.camera_widget import VideoWidget
from frheed.widgets.plot_widgets import PlotGridWidget
from frheed.widgets.canvas_widget import CanvasShape, CanvasLine
from frheed.widgets.selection_widgets import CameraSelection
from frheed.widgets.common_widgets import HSpacer, VSpacer
from frheed.utils import snip_lists
from os.path  import exists
from json import dumps
from pprint import pprint
from time import sleep



class RHEEDWidget(QWidget):
    _initialized = False
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        
        # Settings
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)
        
        #By default, we do not save the data
        self.write_to_file = False
        
        # Create the layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)
        
        # Make the camera widget
        #camera = self.cam_selection._cam
        self.camera_widget = VideoWidget(parent=self)
        self.camera_widget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.MinimumExpanding)
                                         
        # Create the plot widgets
        self.plot_grid = PlotGridWidget(parent=self, title="Live Plots")
        self.region_plot = self.plot_grid.region_plot
        self.profile_plot = self.plot_grid.profile_plot
        self.line_scan_plot = self.plot_grid.line_scan_plot
        
        # Add widgets to layout
        self.layout.addWidget(self.camera_widget, 1, 0, 1, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setColumnStretch(0, 1)
        
        # Connect signals
        self.camera_widget.analysis_worker.data_ready.connect(self.plot_data)
        self.camera_widget.display.canvas.shape_deleted.connect(self.remove_line)
        self.plot_grid.closed.connect(self.live_plots_closed)
        self.camera_widget.display.canvas.shape_deleted.connect(self.plot_grid.remove_curves)
        
        
        # Create the camera selection window
        self.camera_selected = CameraSelection()
        self.camera_selected.is_camera_selected.connect(self._finish_ui_init)
        
        
        # Create the menu bar
        self.menubar = QMenuBar(self)
        
        # "File" menu
        # Note: &File underlines the "F" to indicate the keyboard shortcut,
        # but will not be visible unless enabled manually in Windows.
        # To enable it, go to Control Panel -> Ease of Access -> Keyboard 
        #                   -> Underline keyboard shortcuts and access keys
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction("&Save to file", self.get_file_name)
        self.file_menu.addAction("&Change camera", self.change_camera)
        
        # "View" menu
        self.view_menu = self.menubar.addMenu("&View")
        self.show_live_plots_item = self.view_menu.addAction("&Live plots")
        self.show_live_plots_item.setCheckable(True)
        self.show_live_plots_item.setChecked(True)
        self.show_live_plots_item.toggled.connect(self.show_live_plots)
        
        # "Tools" menu
        #self.tools_menu = self.menubar.addMenu("&Tools")
        #self.preferences_item = self.tools_menu.addAction("&Preferences")
        
        # Add menubar
        self.layout.addWidget(self.menubar, 0, 0, 1, 1)
        
    @pyqtSlot()
    def _finish_ui_init(self):
        """ Finish UI setup after selecting a camera. """
        # Show the widgets
        self.plot_grid.show()
        self.parent().show()
        
        # Make sure a proper camera is actually selected
        if not hasattr(self.camera_selected, 'the_camera'):
            self.parent().quit_app()
        
        # Put the camera object into the VideoWidget
        self.camera_widget.set_camera(self.camera_selected.the_camera)
        
        # Disconnect camera_selected signal to reuse camera selection logic
        self.camera_selected.is_camera_selected.disconnect()
        
        # Mark as initialized
        self._initialized = True
        
    def closeEvent(self, event) -> None:
        if hasattr(self, 'file_save_worker'):
            self.file_save_worker.close()
        if self._initialized:
            [wid.setParent(None) for wid in 
                [self.region_plot, self.profile_plot, self, self.plot_grid]]
            self.camera_widget.closeEvent(event)
        self.camera_selected.close()
        super().closeEvent(event)
        
    @pyqtSlot(dict)
    def plot_data(self, data: dict) -> None:
        """ Plot data from the camera """
        # Get data for each color in the data dictionary
        for color, color_data in data.items():
            # Add region data to the region plot
            if color_data["kind"] in ["rectangle", "ellipse"]:
                curve = self.region_plot.get_or_add_curve(color)
                # Catch RuntimeError if widget has been closed
                try:
                    curve.setData(*snip_lists(color_data["time"], color_data["average"]))
                except RuntimeError:
                    pass
                
            # Add line profile data to the profile plot and update line scan
            elif color_data["kind"] == "line":
                curve = self.profile_plot.get_or_add_curve(color)
                try:
                    curve.setData(color_data["y"][-1])
                except RuntimeError:
                    pass
                
                # Update 2D line scan image
                self.line_scan_plot.set_image(color_data["image"])
                
            # Update region window
            if self.region_plot.auto_fft_max:
                self.region_plot.set_fft_max(color_data["time"][-1])
        
        #Send the data over to the FileSaveWorker object for saving to file
        if self.write_to_file and data != {}:
            self.file_save_worker.save_to_file(data)
            
    @pyqtSlot(object)
    def remove_line(self, shape: Union["CanvasShape", "CanvasLine"]) -> None:
        """ Remove a line from the plot it is part of """
        # Get the plot widget
        plot = self.profile_plot if shape.kind == "line" else self.region_plot
        
        # Remove the line
        plot.plot_widget.removeItem(plot.plot_items.pop(shape.color_name))
        self.camera_widget.analysis_worker.data.pop(shape.color_name)   
        
    @pyqtSlot()
    def live_plots_closed(self) -> None:
        self.show_live_plots_item.setChecked(False)
        
    @pyqtSlot(bool)
    def show_live_plots(self, visible: bool) -> None:
        self.plot_grid.setVisible(visible)
    
    @pyqtSlot()
    def change_camera(self):
        """Closes the current camera, then selects a new one."""
        self.camera_widget.camera_worker.stop()
        sleep(0.1) #Finish IO operations
    
        self.camera_selected = CameraSelection()
    
        def _finish_changing_camera(self):
            # If no new camera is selected, the current camera will be maintained
            print(hasattr(self.camera_selected, 'the_camera'))
            if not hasattr(self.camera_selected, 'the_camera'):
                self.camera_widget.camera_worker.start()
                return
                
            self.camera_widget.set_camera(self.camera_selected.the_camera)
        
        self.camera_selected.is_camera_selected.connect(partial(_finish_changing_camera, self))
            
            
    def get_file_name(self):
        file_name = QFileDialog.getSaveFileName(parent=None, caption='Open file', 
        directory='c:\\', filter="Text file (*.txt)")
        
        self.write_to_file = True
        
        # Instantiate a FileSaveWorker which will handle file saving
        # or change the file name if one already exists
        if not hasattr(self, 'file_save_worker'):
            self.file_save_worker = FileSaveWorker(file_name=file_name[0][:-4])
        else:
            self.file_save_worker.change_file_name(file_name=file_name[0][:-4])


class FileSaveWorker():
    """
    Handles all file saving operations
    """

    def __init__(self, file_name: str) -> None:
        self.change_file_name(file_name)
        
        #Write the header
        self.file.write('Shape ID,Time,Average,Shape type\n')
        
    def __bool__(self) -> bool:
        return(True)
        
    def close(self) -> None:
        self.file.close()
    
    def start_new_file(self) -> None:
        self.change_file_name(self.file_name)
    
    def save_to_file(self, data: dict) -> None:
        write_string = []
        for shape_id, shape_data in data.items():
            curr_time = str(shape_data['time'][-1])
            curr_ave = str(shape_data['average'][-1])
            curr_kind = str(shape_data['kind'][-1]) 
            write_string.append(','.join((shape_id, curr_time, curr_ave, curr_kind)))
        self.file.write(','.join(write_string) + '\n')
        
    def change_file_name(self, file_name: str) -> None:
        if hasattr(self, 'file'):
            self.file.close()
            
        self.file_name = file_name
        self.file_num = 0
        
        #Make sure a unique file is saved
        while(exists(f'{self.file_name}_{self.file_num}.txt')):
            self.file_num += 1
        self.file = open(f'{self.file_name}_{self.file_num}.txt', 'w')
    
        
        
if __name__ == "__main__":
    pass