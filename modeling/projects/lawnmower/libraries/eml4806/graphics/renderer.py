import numpy as np

from abc import ABC, abstractmethod

from eml4806.geometry.vector import vector, vectors, split

Vector = np.ndarray

###############################################################

class AbstractRenderer(ABC):
    
    '''Render a shape'''
    
    @abstractmethod
    def make(self, shape):
        pass

    @abstractmethod
    def update_geometry(self, shape, vertices):
        pass

    @abstractmethod
    def update_style(self, shape):
        pass

###############################################################

class PlotRenderer(AbstractRenderer):
        
    def make(self, shape):
        shape._artist = shape._ax.plot([], [])[0]

    def update_geometry(self, shape, vertices):
        vertices = vectors(vertices)
        if vertices.size == 0: 
            shape._artist.set_data([], [])
        else:
            x, y, _ = split(vertices) 
            shape._artist.set_data(x, y)

    def update_style(self, shape):
        s = shape._style
        if s.has_stroke():
            shape._artist.set_color(s.stroke.color)
            shape._artist.set_linewidth(s.stroke.width)
        if shape._marker is not None:
            shape._artist.set_marker(shape._marker)
            shape._artist.set_markerfacecolor(s.stroke.color)
            shape._artist.set_markeredgecolor(s.stroke.color)
        shape._artist.set_alpha(s.opacity)

###############################################################

class FillRenderer(AbstractRenderer):

    def make(self, shape):
        shape._artist = shape._ax.fill([], [])[0]

    def update_geometry(self, shape, vertices):
        vertices = vectors(vertices)
        if vertices.size == 0: 
            shape._artist.set_xy([])
        else: 
            shape._artist.set_xy(vertices[:, :2])

    def update_style(self, shape):
        s = shape._style
        if s.has_fill():
            shape._artist.set_facecolor(s.fill.color)
        if s.has_stroke():
            shape._artist.set_edgecolor(s.stroke.color)
            shape._artist.set_linewidth(s.stroke.width)
        shape._artist.set_alpha(s.opacity)

###############################################################

class ArrowRenderer(AbstractRenderer):

    def make(self, shape):
        shape._artist = shape._ax.quiver(0, 0, 0, 0,
            angles='xy', scale_units='xy', scale=1,
            units='dots',
            width=3,       # Width of the shaft
            headwidth=4,   # x the width
            headlength=6,   # x the width
            headaxislength=6,  # Matches length to make the back flat
            )

    def update_geometry(self, shape, points):
        x, y, _ = points[0]
        u, v, _ = points[1] - points[0]
        shape._artist.set_offsets((x, y))
        shape._artist.set_UVC(u, v)

    def update_style(self, shape):
        s = shape._style
        if s.has_fill():
            shape._artist.set_color(s.fill.color)
        if s.has_stroke():
            shape._artist.set_edgecolor(s.stroke.color)
        shape._artist.set_alpha(s.opacity)
