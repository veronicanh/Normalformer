from Main import *
from Avhengighet import *
from MengdeAttributter import *

class FunksjonelleAvhengigheter:
    def __init__(self, data, tag):
        self._avhengigheter = []
        self._tag = tag

        self._lefts = MengdeAttributter([], tag)
        self._rights = MengdeAttributter([], tag)

        self._readData(data)

    def __str__(self):
        if (len(self._avhengigheter) == 0):
            return "Ingen"

        prettyStr = ""
        for a in self._avhengigheter:
            prettyStr += str(a) + "\n"
        return prettyStr.strip()

    def __len__(self):
        return len(self._avhengigheter)

    def __getitem__(self, key):
        return self._avhengigheter[key]

    def _readData(self, data):
        for line in data.split("\n"):
            line = line.strip()
            if (line == ""):
                continue

            a = Avhengighet(line, self._tag)
            self._avhengigheter.append(a)
            self._lefts.addAsSet(a.left())
            self._rights.addAsSet(a.right())

    def checkAttributes(self, attributes):
        for avgh in self._avhengigheter:
            for att in avgh.attributes():
                if att not in attributes:
                    fatalError("'" + att + "' from FD '" + str(avgh) + "' is not in attributes")

    # Fjerner alle ugylde FDer, sånn at vi kan gjøre dekomponering
    def gyldigeFDer(self, attributes):
        gyldige = []
        for avgh in self._avhengigheter:
            valid = True
            for att in avgh.attributes():
                if att not in attributes:
                    valid = False
            if valid:
                gyldige.append(avgh)

        data = ""
        for a in gyldige:
            data += str(a) + "\n"
        return FunksjonelleAvhengigheter(data, self._tag)


    # Finnes aldri på høyreside
    def alltidMed(self, alleAtt):
        res = list(alleAtt.set() - self._rights.set())
        if (self._tag == CHAR_TAG):
            res.sort()
        return MengdeAttributter(res, self._tag)

    # Finnes kun på høyreside
    def aldriMed(self):
        res = list(self._rights.set() - self._lefts.set())
        if (self._tag == CHAR_TAG):
            res.sort()
        return MengdeAttributter(res, self._tag)

    # Resterende
    def muligUtvidelse(self, alleAtt):
        res = list(alleAtt.set() - self.alltidMed(alleAtt).set() - self.aldriMed().set())
        if (self._tag == CHAR_TAG):
            res.sort()
        return MengdeAttributter(res, self._tag)

    def tillukning(self, att):
        tillukning = MengdeAttributter(att.list(), self._tag).copy()

        lenForrige = 0
        # Fortsett itereringa frem til det ikke forandres noe mer
        while lenForrige != len(tillukning):
            lenForrige = len(tillukning)

            for avhg in self._avhengigheter:
                # Dersom vi har alle attributtene som kreves for å bestemme høyresiden,
                # så legges høyresiden til i tillukningen
                if tillukning.containsAllFrom(avhg.left()):
                    tillukning.addAsSet(avhg.right())

        return tillukning

    def kreverOmskriving(self):
        for avhg in self._avhengigheter:
            if avhg.kreverOmskriving():
                return True
        return False

    def omskrivEnPåHøyre(self):
        for i in range(len(self._avhengigheter)):
            avgh = self._avhengigheter[i]
            if avgh.kreverOmskriving():
                self._avhengigheter.pop(i)
                for ny in reversed(avgh.omskriv()):
                    self._avhengigheter.insert(i, ny)

    def bestemNormalform(self, kandidatnøkler):
        s = ""
        s += "Går igjennom hver FD og sjekker om de bryter med BCNF/3NF/2NF:\n"

        normalform = "BCNF"
        for a in self._avhengigheter:
            ss, nf = self._sjekkNormalform1FD(a, kandidatnøkler)
            s += ss

            # Oppdaterer normalform til hele relasjonen
            if (nf == "3NF" and normalform == "BCNF"):
                normalform = "3NF"
            elif (nf == "2NF" and (normalform == "3NF" or normalform == "BCNF")):
                normalform = "2NF"
            elif (nf == "1NF"):
                return s, nf

        s += "Relasjonen er på den laveste normalformen av alle FDene, så relasjonen er på " + normalform + "."
        return s, normalform

    # For å finne en FD som bryter med BCNF under dekomponering
    def fdIkkeBCNF(self, kandidatnøkler):
        s = ""
        for a in self._avhengigheter:
            _, nf = self._sjekkNormalform1FD(a, kandidatnøkler)

            if (nf == "BCNF"):
                s += " - " + str(a) + ": Bryter ikke med BCNF siden {" + str(a.left()) + "} er en supernøkkel.\n"
            else:
                s += " - " + str(a) + ": Bryter med BCNF siden {" + str(a.left()) + "} ikke er en supernøkkel.\n"
                return s, a
        return s, None

    def _sjekkNormalform1FD(self, FD, kandidatnøkler):
        s = ""
        s += str(FD) + "\n"
        # Sjekker om BCNF
        if (FD.left().erSupernøkkel(kandidatnøkler)):
            s += " - Bryter ikke med BCNF siden {" + str(FD.left()) + "} er en supernøkkel.\n\n"
            return s, "BCNF"

        # Sjekker om 3NF
        s += " - Brudd på BCNF siden {" + str(FD.left()) + "} ikke er en supernøkkel, går til neste punkt.\n"
        if (FD.right().erNøkkelAtt(kandidatnøkler)):
            s += " - Bryter ikke med 3NF siden " + str(FD.right()) + " er et nøkkelattributt.\n\n"
            return s, "3NF"

        # Sjekker om 2NF
        s += " - Brudd på 3NF siden " + str(FD.right()) + " ikke er et nøkkelattributt, går til neste punkt.\n"
        if not (FD.left().partOfKandidatnøkkel(kandidatnøkler)):
            s += " - Bryter ikke med 2NF siden {" + str(FD.left()) + "} ikke er en del av en kandidatnøkkel."
            if (FD != self._avhengigheter[-1]):
                s += " Sjekker neste FD."
            s += "\n\n"
            return s, "2NF"

        # Er på 1NF
        s += " - Brudd på 2NF siden {" + str(FD.left()) + "} er en del av en kandidatnøkkel.\n\n"
        s += "Relasjonen er på den laveste normalformen av alle FDene, så relasjonen er på 1NF."
        if (FD != self._avhengigheter[-1]):
            s += "\nSiden dette er den laveste normalformen en relasjon kan ha, trenger jeg ikke å fortsette å sjekke FDene."
        return s, "1NF"