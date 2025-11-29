import numpy as np
import matplotlib.pyplot as plt

class Workspace:
    def __init__(self, xmin, xmax, ymin, ymax, menu=None):
        plt.ion()
        self.figure, self.axis = plt.subplots(figsize=(10, 10))
        self.axis.set_xlim(xmin, xmax)
        self.axis.set_ylim(ymin, ymax)
        self.axis.set_aspect("equal")
        self.axis.grid(True)
        self.figure.suptitle(self.title())
        if menu is not None:
            self.figure.supxlabel(menu)
            print(menu)
            print()
    def title(self):
        return '''Florida International University
        EML 4806 Modeling & EML 5808 Robot Control
        Miami, FL (Fall 2025)'''
    def update(self):
        self.figure.canvas.draw_idle()
        self.figure.canvas.flush_events()

    def __del__(self):
        plt.ioff()
        plt.show()