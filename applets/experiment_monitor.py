import numpy as np
import PyQt5
import pyqtgraph as pg
from PyQt5.QtGui import QColor

from artiq.applets.simple import TitleApplet, SimpleApplet

class ExperimentMonitor(pg.PlotWidget):

    def __init__(self, args):
        pg.PlotWidget.__init__(self)
        self.args = args

        self.y_dataset_name = self.args.y
        self.has_x_dataset = self.args.x is not None
        if self.has_x_dataset:
            self.x_dataset_name = self.args.x
        else:
            self.x_dataset_name = "No X Dataset"

        if self.args.xmax is not None and not self.has_x_dataset:
            raise RuntimeError("xmax given, but no x dataset given.")

        # This assume the default value of xmin and xmax is 0
        if self.args.xmin != 0 and self.args.xmax is None:
            raise RuntimeError("xmin given but no xmax given.")
        if self.args.ymin != 0 and self.args.ymax is None:
            raise RuntimeError("ymin given but no ymax given.")

        if self.args.xmax is not None:
            self.setXRange(self.args.xmin, self.args.xmax)
        if self.args.ymax is not None:
            self.setYRange(self.args.ymin, self.args.ymax)
        
        if not self.args.pen:
             self.pen = None
        else:
             self.pen = 1

        title = "Experiment Monitor"
        if self.args.exp_label is not None:
             title += f"<br>({self.args.exp_label})"

        self.setLabel("bottom", self.x_dataset_name)
        self.setLabel("left", self.y_dataset_name)
        self.setTitle(title)
        self.setBackground(QColor(240, 240, 240))
        
        self.waiting_for_size_update = False

    def data_changed(self, data, mods, title=None):
        if self.y_dataset_name not in data:
            raise RuntimeError(f"Y Dataset name '{self.y_dataset_name}' "
                                "not in data.")

        if self.has_x_dataset and self.x_dataset_name not in data:
            raise RuntimeError(f"X Dataset name '{self.x_dataset_name}' "
                                "not in data.")

        y_data = data[self.y_dataset_name][1]
        if self.has_x_dataset:
            x_data = data[self.x_dataset_name][1]
        else:
            x_data = np.arange(len(y_data))
        
        # If x_data and y_data have different lengths, wait one update cycle
        # to see if the other has updated to the right length. Else raise an error.
        if x_data.size != y_data.size:
        	if not self.waiting_for_size_update:
        		self.waiting_for_size_update = True
        		return
        	else:
        		raise RuntimeError(
        			f"Size mismatch between x_data ({x_data.size}) "
        			f"and y_data ({y_data.size})."
        		)
        
        # If we waited for a size update and sizes matched, unset this flag
        elif self.waiting_for_size_update:
        	self.waiting_for_size_update = False

        self.clear()
        self.plot(x_data, y_data, pen=self.pen, symbol="o").setSymbolSize(5)



def main():
    applet = SimpleApplet(ExperimentMonitor)
    #applet = TitleApplet(ExperimentMonitor)
    applet.add_dataset("y", "Y values")
    applet.add_dataset("x", "X values", required=False)
    applet.argparser.add_argument("--xmin", type=float, default=0,
                                  help="Min value of the x axis")
    applet.argparser.add_argument("--xmax", type=float, default=None,
                                  help="Max value of the x axis")
    applet.argparser.add_argument("--ymin", type=float, default=0,
                                  help="Min value of the y axis")
    applet.argparser.add_argument("--ymax", type=float, default=None,
                                  help="Max value of the y axis")
    applet.argparser.add_argument("--pen", type=bool, default=False,
                                  help="Set to true to draw lines between points.")
    applet.argparser.add_argument("--exp-label", type=str, default=None)
    applet.run()


if __name__ == "__main__":
    main()
