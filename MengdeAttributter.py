from Main import *

class MengdeAttributter:
    def __init__(self, attr, tag):
        self._attributter = attr
        self._tag = tag

    def __str__(self):
        if (len(self._attributter) == 0):
            return "Ingen"

        str = ""
        for i in range(len(self._attributter)):
            str += self._attributter[i]
            if (i != len(self._attributter) - 1):
                if (self._tag == TEXT_TAG):
                    str += ","
                str += " "
        return str

    def strCommaSeparated(self):
        orgTag = self._tag
        self._tag = TEXT_TAG
        s = str(self)
        self._tag = orgTag
        return s

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if (self._counter >= len(self._attributter)):
            raise StopIteration

        elm = self._attributter[self._counter]
        self._counter += 1
        return elm

    def __len__(self):
        return len(self._attributter)

    def __getitem__(self, key):
        return self._attributter[key]

    def copy(self):
        c = MengdeAttributter([], self._tag)
        for elm in self._attributter:
            c.add(elm)
        return c

    def changeTag(self, tag):
        self._tag = tag

    def add(self, elm):
        self._attributter.append(elm)

    def addAll(self, lst, place=None):
        if (place == "front"):
            for elm in lst:
                self._attributter.insert(0, elm)
        else:
            for elm in lst:
                self._attributter.append(elm)

    def addAsSet(self, lst):
        for elm in lst:
            if elm not in self._attributter:
                self._attributter.append(elm)

    def list(self):
        return self._attributter

    def set(self):
        return set(self._attributter)

    def containsAllFrom(self, other):
        return len(other.set() - self.set()) == 0

    def commonElements(self, other):
        m = MengdeAttributter([], self._tag)
        for elm in other:
            if elm in self._attributter:
                m.add(elm)
        return m

    def removeDuplicatesFrom(self, other):
        for elm in other:
            if elm in self._attributter:
                self._attributter.remove(elm)

    def remove(self, elm):
        self._attributter.remove(elm)

    def sort(self):
        if (self._tag == TEXT_TAG):
            return self
        self._attributter.sort()
        return self

    def sorted(self):
        if (self._tag == TEXT_TAG):
            return self
        return MengdeAttributter(sorted(self._attributter), self._tag)

    def erSupernøkkel(self, kandidat):
        for nøkkel in kandidat:
            if nøkkel.set().issubset(self.set()):
                return True
        return False

    def erNøkkelAtt(self, kandidat):
        if (len(self) > 1):
            fatalError("Det skal være max 1 element på høyresiden under bestemming av normalform!")

        att = self._attributter[0]
        for nøkkel in kandidat:
            for a in nøkkel:
                if a == att:
                    return True
        return False

    def partOfKandidatnøkkel(self, kandidat):
        for nøkkel in kandidat:
            if self.set().issubset(nøkkel.set()):
                return True
        return False