import abc
import io


class AbstractOpenMock:
    old_open = open

    @abc.abstractmethod
    def __init__(self, read_data=None):
        pass

    def __call__(self, name, mode="r"):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "mode", mode)
        return self

    def __getattr__(self, item):
        return getattr(self._stream, item)

    def __setattr__(self, key, value):
        try:
            object.__getattribute__(self, key)
            object.__setattr__(self, key, value)
        except AttributeError:
            setattr(self._stream, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def reset(self):
        self.seek(io.SEEK_SET)

    def dump(self):
        self.reset()
        return self.read()


class OpenStringMock(AbstractOpenMock):
    def __init__(self, read_data=None):
        object.__setattr__(self, "_stream", io.StringIO(read_data))
