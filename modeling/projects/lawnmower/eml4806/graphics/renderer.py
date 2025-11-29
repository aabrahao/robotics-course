from abc import ABC, abstractmethod

from matplotlib.patches import FancyArrowPatch as ArrowPatch

import eml4806.geometry.vector as vector

###############################################################

class AbstractRenderer(ABC):
    
    '''Render a shape'''
    
    @abstractmethod
    def make(self, shape):
        pass

    @abstractmethod
    def updateGeometry(self, shape, vertices):
        pass

    @abstractmethod
    def updateStyle(self, shape):
        pass

###############################################################

class PlotRenderer(AbstractRenderer):
        
    def make(self, shape):
        shape._artist = shape._ax.plot([], [])[0]

    def updateGeometry(self, shape, vertices):
        vertices = vector.ensureMany(vertices)
        if vector.isEmpty(vertices): 
            shape._artist.set_data([], [])
        else: 
            shape._artist.set_data(vertices[:, 0], vertices[:, 1])

    def updateStyle(self, shape):
        s = shape._style
        if s.hasStroke():
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

    def updateGeometry(self, shape, vertices):
        vertices = vector.ensureMany(vertices)
        if vector.isEmpty(vertices): 
            shape._artist.set_xy([])
        else: 
            shape._artist.set_xy(vertices)

    def updateStyle(self, shape):
        s = shape._style
        if s.hasFill():
            shape._artist.set_facecolor(s.fill.color)
        if s.hasStroke():
            shape._artist.set_edgecolor(s.stroke.color)
            shape._artist.set_linewidth(s.stroke.width)
        shape._artist.set_alpha(s.opacity)

###############################################################

class ArrowRenderer(AbstractRenderer):

    def make(self, shape):
        shape._artist = ArrowPatch(
            posA=(0.0, 0.0),
            posB=(0.0, 0.0),
            arrowstyle="->",
            mutation_scale=shape._magnification,
        )
        shape._ax.add_patch(shape._artist)

    def updateGeometry(self, shape, o):
        shape._artist.set_positions((o[0, 0], o[0, 1]), (o[1, 0], o[1, 1]))

    def updateStyle(self, shape):
        s = shape._style
        if s.hasFill():
            shape._artist.set_facecolor(s.fill.color)
        if s.hasStroke():
            shape._artist.set_edgecolor(s.stroke.color)
            shape._artist.set_linewidth(s.stroke.width)
        shape._artist.set_alpha(s.opacity)
