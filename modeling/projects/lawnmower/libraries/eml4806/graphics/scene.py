from __future__ import annotations
from typing import Any, Optional, Dict, Set
import uuid

from eml4806.graphics.actor import Actor
from eml4806.graphics.renderer.matplotlib import Matplotlib
from eml4806.geometry.vector import Vector

from eml4806.geometry.vector import Vector, Vectors, as_vector, as_vectors
from eml4806.graphics.shape import Geometry, Points, Polyline, Polygon, Rectangle, Circle, Triangle, Arrow, Axes
from eml4806.graphics.style import Style
from eml4806.geometry.transform import Transform

class Scene:
    
    __slots__ = ('renderer', 'actors', 'pending_updates', 'pending_removals')

    def __init__(self, origin: Vector, size: Vector, renderer = Matplotlib()):
        self.renderer = renderer
        self.actors: Dict[uuid.UUID, Actor] = {}
        self.pending_updates: Set[uuid.UUID] = set()
        self.pending_removals: Set[uuid.UUID] = set()
        # Decorate
        self.renderer.set_viewport(origin[0], origin[1], size[0], size[1])

    def flag(self, uid: uuid.UUID):
        self.pending_updates.add(uid)

    def clear(self) -> None:
        '''Clear the scene'''
        self.pending_removals.update(self.actors.keys())
        self.pending_updates.clear()

    def update(self) -> None:
        '''Update the scene'''
        self._sync()
        self.renderer.render()

    # BACKEND SYNCHRONIZATION
    # =============================================================================

    def _add(self, geometry: Any, style: Any = None, transform: Any = None) -> Actor:
        uid = uuid.uuid4()
        actor = Actor(self, uid, geometry, style, transform)
        self.actors[uid] = actor
        self.pending_updates.add(uid)
        return actor
    
    def _remove(self, uid: uuid.UUID) -> None:
        if uid in self.actors:
            self.pending_removals.add(uid)
            self.pending_updates.discard(uid)

    def _sync(self) -> None:
        """Synchronizes scene state with the Renderer backend."""
        # Removals
        for uid in self.pending_removals:
            self.renderer.remove(uid)
            self.actors.pop(uid, None)
        self.pending_removals.clear()
        # Updates
        for uid in list(self.pending_updates):
            actor = self.actors.get(uid)
            if not actor:
                continue
            if uid in self.renderer:
                self.renderer.update(uid, *actor.poll_updates())
                actor.update_flags.clear()
            else:
                self.renderer.create(uid, actor.geometry, actor.style, actor.transform)
        self.pending_updates.clear()

    # GRAPHICS ENGINE
    # =============================================================================

    def group(self, shapes):
        pass
        
    def rectangle(self, center: Vector, size: Vector, **kwargs):
        shape = Rectangle(center=as_vector(center), size=as_vector(size))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def circle(self, center: Vector, radius: float, **kwargs):
        shape = Circle(center=as_vector(center), radius=float(radius))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def polygon(self, points: Vectors, **kwargs):
        shape = Polygon(points=as_vectors(points))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor
    
    def polyline(self, points: Vectors, **kwargs):
        shape = Polyline(points=as_vectors(points))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def line(self, start: Vector, end: Vector, infinite=True, **kwargs):
        shape = Polyline(points=as_vectors([start, end]))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def points(self, points: Vectors, **kwargs):
        shape = Points(points=as_vectors(points))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def ray(self, origin: Vector, direction: Vector, **kwargs):
        pass
    
    def arrow(self, origin: Vector, direction: Vector, **kwargs):
        shape = Arrow(origin=as_vector(origin), direction=as_vector(direction))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor
    
    def axes(self, origin: Vector, scale: float, **kwargs):
        shape = Axes(origin=as_vector(origin), scale=float(scale))
        actor = self._add(shape)
        actor.set(**kwargs)
        return actor

    def map(self, position=None, size=None, image=None, *, pixels=500):
        pass
 
