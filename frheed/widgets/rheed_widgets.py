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
    
    )
from PyQt5.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
    
    )
# from PyQt5.QtGui import (
    
#     )

from frheed.widgets.camera_widget import VideoWidget
from frheed.widgets.plot_widgets import PlotGridWidget
from frheed.widgets.canvas_widget import CanvasShape, CanvasLine
from frheed.widgets.selection_widgets import select_camera
from frheed.widgets.common_widgets import HSpacer, VSpacer
from frheed.utils import snip_lists



class RHEEDWidget(QWidget):
    _initialized = False
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Settings
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)
        
        # Create the layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)
        
        
        
        # Make all the widgets invisible until camera selected
        self.setVisible(False)
        
        # Make the camera widget
        #camera = self.cam_selection._cam
        self.camera_widget = VideoWidget(parent=self)
        self.camera_widget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.MinimumExpanding)
                                         
        # Create the plot widgets
        # self.region_plot = PlotWidget(parent=self, popup=True, name="Regions (Live)")
        # self.profile_plot = PlotWidget(parent=self, popup=True, name="Line Profiles (Live)")
        self.plot_grid = PlotGridWidget(parent=self, title="Live Plots", popup=True)
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
        self.cam_selected_signal = select_camera(self.camera_widget)
        self.cam_selected_signal.is_camera_selected.connect(self._finish_ui_init)
        
        # Create the menu bar
        self.menubar = QMenuBar(self)
        
        # "File" menu
        # Note: &File underlines the "F" to indicate the keyboard shortcut,
        # but will not be visible unless enabled manually in Windows.
        # To enable it, go to Control Panel -> Ease of Access -> Keyboard 
        #                   -> Underline keyboard shortcuts and access keys
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction("&Change camera", partial(select_camera, self.camera_widget))
        
        # "View" menu
        self.view_menu = self.menubar.addMenu("&View")
        self.show_live_plots_item = self.view_menu.addAction("&Live plots")
        self.show_live_plots_item.setCheckable(True)
        self.show_live_plots_item.setChecked(True)
        self.show_live_plots_item.toggled.connect(self.show_live_plots)
        
        # "Tools" menu
        self.tools_menu = self.menubar.addMenu("&Tools")
        self.preferences_item = self.tools_menu.addAction("&Preferences")
        
        # Add menubar
        self.layout.addWidget(self.menubar, 0, 0, 1, 1)
        
        
    @pyqtSlot()
    def _finish_ui_init(self):
        """ Finish UI setup after selecting a camera. """
        # Show the widget
        self.setVisible(True)
        
        # Reconnect camera_selected signal
        self.cam_selected_signal.disconnect()
        
        # Mark as initialized
        self._initialized = True
        
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        
    def closeEvent(self, event) -> None:
        if self._initialized:
            [wid.setParent(None) for wid in 
                [self.region_plot, self.profile_plot, self, self.plot_grid]]
            self.camera_widget.closeEvent(event)
        self.cam_selection.close()
        
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
        

if __name__ == "__main__":
    def test():
        from frheed.utils import test_widget
        
        return test_widget(RHEEDWidget, block=True)
        
    widget, app = test()
