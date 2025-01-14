import ntpath
import posixpath


class Path:
    def __init__(self, sep, getcwd=None, realpath=None):
        def _getcwd():
            return ""

        self.getcwd = getcwd or _getcwd
        self.realpath = realpath or self.abspath

        if sep == posixpath.sep:
            self.flavour = posixpath
        elif sep == ntpath.sep:
            self.flavour = ntpath
        else:
            raise ValueError(f"unsupported separator '{sep}'")

    def chdir(self, path):
        def _getcwd():
            return path

        self.getcwd = _getcwd

    def join(self, *parts):
        return self.flavour.join(*parts)

    def split(self, path):
        return self.flavour.split(path)

    def normpath(self, path):
        return self.flavour.normpath(path)

    def isabs(self, path):
        return self.flavour.isabs(path)

    def abspath(self, path):
        if not self.isabs(path):
            path = self.join(self.getcwd(), path)
        return self.normpath(path)

    def commonprefix(self, path):
        return self.flavour.commonprefix(path)

    def parts(self, path):
        drive, path = self.flavour.splitdrive(path.rstrip(self.flavour.sep))

        ret = []
        while True:
            path, part = self.flavour.split(path)

            if part:
                ret.append(part)
                continue

            if path:
                ret.append(path)

            break

        ret.reverse()

        if drive:
            ret = [drive] + ret

        return tuple(ret)

    def parent(self, path):
        return self.flavour.dirname(path)

    def dirname(self, path):
        return self.parent(path)

    def parents(self, path):
        parts = self.parts(path)
        return tuple(
            self.join(*parts[:length])
            for length in range(len(parts) - 1, 0, -1)
        )

    def name(self, path):
        return self.parts(path)[-1]

    def suffix(self, path):
        name = self.name(path)
        _, dot, suffix = name.partition(".")
        return dot + suffix

    def with_name(self, path, name):
        parts = list(self.parts(path))
        parts[-1] = name
        return self.join(*parts)

    def with_suffix(self, path, suffix):
        parts = list(self.parts(path))
        real_path, _, _ = parts[-1].partition(".")
        parts[-1] = real_path + suffix
        return self.join(*parts)

    def isin(self, left, right):
        left_parts = self.parts(left)
        right_parts = self.parts(right)
        left_len = len(left_parts)
        right_len = len(right_parts)
        return left_len > right_len and left_parts[:right_len] == right_parts

    def isin_or_eq(self, left, right):
        return left == right or self.isin(left, right)

    def overlaps(self, left, right):
        # pylint: disable=arguments-out-of-order
        return self.isin_or_eq(left, right) or self.isin(right, left)

    def relpath(self, path, start=None):
        if start is None:
            start = "."
        return self.flavour.relpath(
            self.abspath(path), start=self.abspath(start)
        )

    def relparts(self, path, start=None):
        return self.parts(self.relpath(path, start=start))

    def as_posix(self, path):
        return path.replace(self.flavour.sep, posixpath.sep)
