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
        shape._artist = shape._ax.annotate('', xy=(0, 0), xytext=(0, 0), 
            arrowprops=dict(
                facecolor=None,
                edgecolor=None,
                #width=4,       # Thickness of the tail in points
                #headwidth=12,  # Width of the head in points
                #headlength=15, # Length of the head in points
                shrink=0       # Ensures the arrow touches the exact coordinates
            ))

    def update_geometry(self, shape, points):
        x1, y1, _ = points[0]
        x2, y2, _ = points[1]
        shape._artist.xy = (x2, y2)
        shape._artist.set_position((x1, y1))

    def update_style(self, shape):
        s = shape._style
        if s.has_fill():
            shape._artist.arrow_patch.set_facecolor(s.fill.color)
            shape._artist.arrow_patch.set_edgecolor(s.fill.color)
        if s.has_stroke():
            shape._artist.arrow_patch.set_edgecolor(s.stroke.color)
            shape._artist.arrow_patch.set_linewidth(s.stroke.width)
        shape._artist.arrow_patch.set_alpha(s.opacity)
