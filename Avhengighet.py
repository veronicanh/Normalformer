from Main import *
from MengdeAttributter import *

class Avhengighet():
    def __init__(self, data, tag):
        self._tag = tag
        self._left = MengdeAttributter([], tag)
        self._right = MengdeAttributter([], tag)

        self._readData(data)

    def __str__(self):
        return str(self._left) + " " + SPLIT_BY + " " + str(self._right)

    def _readData(self, data):
        if (SPLIT_BY not in data):
            fatalError("FD '" + data + "' does not contain '" + SPLIT_BY + "'")

        if (self._tag == TEXT_TAG):
            bits = data.replace(" ", "").split(SPLIT_BY)
            self._left.addAll(bits[0].split(","))
            self._right.addAll(bits[1].split(","))

        elif (self._tag == CHAR_TAG):
            bits = data.replace(" ", "").split(SPLIT_BY)
            self._left.addAll([c for c in bits[0]])
            self._right.addAll([c for c in bits[1]])

    def attributes(self):
        return MengdeAttributter(self._left.list() + self._right.list(), self._tag)

    def left(self):
        return self._left

    def right(self):
        return self._right

    def kreverOmskriving(self):
        return len(self._right) >= 2

    def omskriv(self):
        nye = []
        for att in self._right:
            data = str(self._left) + SPLIT_BY + att
            nye.append(Avhengighet(data, self._tag))
        return nye