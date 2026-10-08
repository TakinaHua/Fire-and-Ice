"""Opaque handles for camera resources that are not part of renderable game state.

CMU deep-hashes app attributes before/after drawing. Camera/model/thread internals
are independently mutable and must not be recursively inspected by that checker.
The handle has stable identity; ordinary gameplay fields remain fully checked.
"""


class RuntimeResource:
    __slots__ = ('_resource',)

    def __init__(self, resource):
        self._resource = resource

    def __getattr__(self, name):
        if name == '__dict__':
            raise AttributeError(name)
        return getattr(self._resource, name)
