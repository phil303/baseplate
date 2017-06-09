import logging
import os


logger = logging.getLogger(__name__)


_NOT_LOADED = object()


class WatchedFileNotAvailableError(Exception):
    def __init__(self, path, inner):
        super(WatchedFileNotAvailableError, self).__init__()
        self.path = path
        self.inner = inner

    def __str__(self):  # pragma: nocover
        return "{}: {}".format(self.path, self.inner)


class FileWatcher(object):
    def __init__(self, path, parser):
        self._path = path
        self._parser = parser
        self._mtime = 0
        self._data = _NOT_LOADED

    def get_data(self):
        try:
            file_changed = self._mtime < os.path.getmtime(self._path)
        except OSError:
            file_changed = False

        if self._data is _NOT_LOADED or file_changed:
            logger.debug("Loading %s.", self._path)

            try:
                with open(self._path, "r") as f:
                    self._data = self._parser(f)
                    self._mtime = os.fstat(f.fileno()).st_mtime
            except IOError as exc:
                raise WatchedFileNotAvailableError(self._path, exc)

        return self._data
