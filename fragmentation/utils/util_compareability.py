import mod

class ComparableVertex:
    def __init__(self, vertex, attrs=("id", "stringLabel")):
        if isinstance(vertex, ComparableVertex):  # unwrap if needed
            vertex = vertex.vertex
        self.vertex = vertex
        self.attrs = (attrs,) if isinstance(attrs, str) else tuple(attrs)

    def __eq__(self, other):
        if isinstance(other, ComparableVertex):
            other_vertex = other.vertex
        elif isinstance(other, mod.Graph.Vertex):
            other_vertex = other
        else:
            return NotImplemented
        return all(getattr(self.vertex, attr) == getattr(other_vertex, attr) for attr in self.attrs)

    def __hash__(self):
        return hash(tuple(getattr(self.vertex, attr) for attr in self.attrs))

    def __repr__(self):
        return f"ComparableVertex({', '.join(f'{a}={getattr(self.vertex, a)}' for a in self.attrs)})"


class ComparableVertexList:
    def __init__(self, vertices, attrs=("id", "stringLabel")):
        self.attrs = (attrs,) if isinstance(attrs, str) else tuple(attrs)
        self._wrapped = [
            ComparableVertex(v.vertex if isinstance(v, ComparableVertex) else v, self.attrs)
            for v in vertices
        ]

    def __contains__(self, vertex):
        return ComparableVertex(vertex, self.attrs) in self._wrapped

    def add(self, vertex):
        wrapped = ComparableVertex(vertex, self.attrs)
        if wrapped not in self._wrapped:
            self._wrapped.append(wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __iter__(self):
        return (cv.vertex for cv in self._wrapped)

    def __getitem__(self, index):
        return self._wrapped[index].vertex

    def __repr__(self):
        return f"ComparableVertexList([\n  " + ",\n  ".join(repr(cv) for cv in self._wrapped) + "\n])"

    def to_raw_list(self):
        return [cv.vertex for cv in self._wrapped]

    def to_wrapped(self):
        return self._wrapped.copy()

    def __eq__(self, other):
        if isinstance(other, ComparableVertexList):
            return self.attrs == other.attrs and set(self._wrapped) == set(other._wrapped)
        elif isinstance(other, ComparableVertex):
            return other in self._wrapped
        elif isinstance(other, mod.Graph.Vertex):
            return ComparableVertex(other, self.attrs) in self._wrapped
        return NotImplemented
