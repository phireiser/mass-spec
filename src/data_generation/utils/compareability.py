"""
Helpers to make mod.* objects from different derivation graphs comparable.
"""

import mod
from typing import Iterable, Tuple

class ComparableVertex:
    """
    Lightweight wrapper around mod.Graph.Vertex to provide stable equality and hashing
    across different derivation graphs (by selected attributes).
    """
    __slots__ = ("vertex", "attrs", "_key")

    def __init__(self, vertex, attrs=("id", "stringLabel")):
        if isinstance(vertex, ComparableVertex):  # unwrap if needed
            vertex = vertex.vertex
        self.vertex = vertex
        self.attrs = (attrs,) if isinstance(attrs, str) else tuple(attrs)
        # Read the comparison attributes off the mod vertex exactly once and cache
        # the resulting key tuple. Each `getattr` on a mod object goes through mod's
        # (slow) Python `__getattribute__` wrapper, and these wrappers are hashed
        # and compared tens of millions of times per molecule (84M `__hash__` calls
        # on toluene). Precomputing moves that cost from every hash/eq to a single
        # read at construction; the hash value is identical to before.
        self._key = tuple(getattr(vertex, attr) for attr in self.attrs)

    def __eq__(self, other):
        if isinstance(other, ComparableVertex):
            if other.attrs == self.attrs:
                return self._key == other._key  # fast path: compare cached keys
            other_vertex = other.vertex
        elif isinstance(other, mod.Graph.Vertex):
            other_vertex = other
        else:
            return NotImplemented
        return all(getattr(self.vertex, attr) == getattr(other_vertex, attr) for attr in self.attrs)

    def __hash__(self):
        return hash(self._key)

    def __repr__(self):
        attrs_str = ", ".join(f"{a}={getattr(self.vertex, a)}" for a in self.attrs)
        return f"ComparableVertex({attrs_str})"



class ComparableVertexList:
    """
    Container that wraps an iterable of vertices with ComparableVertex for
    consistent equality and hashing. Provides fast membership checks while
    preserving insertion order for iteration.
    """
    __slots__ = ("attrs", "_wrapped_list", "_wrapped_set")

    def __init__(
            self, vertices: Iterable[mod.Graph.Vertex] | Iterable[ComparableVertex],
            attrs=("id", "stringLabel")
            ) -> None:
        self.attrs: Tuple[str, ...] = (attrs,) if isinstance(attrs, str) else tuple(attrs)
        wrapped = [ComparableVertex(v.vertex if isinstance(v, ComparableVertex) else v, self.attrs) for v in vertices]
        # Keep both list (to preserve order) and set (for O(1) membership)
        self._wrapped_list = wrapped
        self._wrapped_set = set(wrapped)

    def __contains__(self, vertex):
        return ComparableVertex(vertex, self.attrs) in self._wrapped_set

    def add(self, vertex):
        """
        Add an element to the container (if not already present).
        """
        wrapped = ComparableVertex(vertex, self.attrs)
        if wrapped not in self._wrapped_set:
            self._wrapped_list.append(wrapped)
            self._wrapped_set.add(wrapped)

    def __len__(self):
        return len(self._wrapped_list)

    def __iter__(self):
        return (cv.vertex for cv in self._wrapped_list)

    def __getitem__(self, index):
        return self._wrapped_list[index].vertex

    def __repr__(self):
        return "ComparableVertexList([\n  " + \
            ",\n  ".join(repr(cv) for cv in self._wrapped_list) + \
            "\n])"

    def __eq__(self, other):
        if isinstance(other, ComparableVertexList):
            return self.attrs == other.attrs and set(self._wrapped_list) == set(other._wrapped_list)
        elif isinstance(other, ComparableVertex):
            return other in self._wrapped_set
        elif isinstance(other, mod.Graph.Vertex):
            return ComparableVertex(other, self.attrs) in self._wrapped_set
        return NotImplemented


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "ComparableVertex",
    "ComparableVertexList",
]
