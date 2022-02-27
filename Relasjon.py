# Relasjoner sendes inn på formen:
#   Navn(att1, att2, att3,att4,att5)

from Main import *
from MengdeAttributter import *
from FunksjonelleAvhengigheter import *

class Relasjon:
    def __init__(self, data, FDer):
        self._navn = data.split("(")[0]
        att = data.split("(")[1].replace(")", "").replace(" ", "").split(",")
        self._attributes = MengdeAttributter(att, TEXT_TAG)
        self._kandidatnøkler = []
        self._normalform = None

        self._FDer = FDer
        self._FDer.checkAttributes(self._attributes)

        self._createdMessage()

    def __str__(self):
        str = self._navn + "("
        for i in range(len(self._attributes)):
            str += self._attributes[i]
            if (i != len(self._attributes) - 1):
                str += ", "
        return str + ")"

    def strKandidatnøkler(self):
        strNøkler = ["{" + str(x) + "}" for x in self._kandidatnøkler]
        return str(MengdeAttributter(strNøkler, TEXT_TAG))

    def strFDer(self):
        return str(self._FDer).replace(" ", "").replace("\n", ", ")

    def _createdMessage(self):
        longest = 0
        for line in (str(self) + "\n" + str(self._FDer)).split("\n"):
            if (len(line) > longest):
                longest = len(line)

        print("┌" + ("─" * (longest + 2)) + "┐")
        print("│ " + str(self) + (" " * (longest - len(str(self)))) + " │")
        print("├" + ("─" * (longest + 2)) + "┤")
        for line in str(self._FDer).split("\n"):
            print("│ " + line + (" " * (longest - len(line))) + " │")
        print("└" + ("─" * (longest + 2)) + "┘")


    def finnKandidatnøkler(self):
        if (len(self._kandidatnøkler) != 0):
            return "Kandidatnøkkelene til " + self._navn + ": " + self.strKandidatnøkler()

        s =  "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
        s += " Finner alle kandidatnøklene til relasjonen " + self._navn + "\n"
        s += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"

        alltidMed = self._FDer.alltidMed(self._attributes).sort()
        aldriMed = self._FDer.aldriMed().sort()
        muligeUtv = self._FDer.muligUtvidelse(self._attributes).sort()
        s += "Attributter aldri på høyreside (må være med i alle kandidatnøkler): " + str(alltidMed) + "\n"
        s += "Attributter som kun er på høyreside (aldri med i kandidatnøkkel)  : " + str(aldriMed) + "\n"
        s += "Attributter som vi potensielt kan utvide med (er på begge sidene) : " + str(muligeUtv) + "\n"
        s += "\n"

        s += self._sjekkAlltidMed(alltidMed, muligeUtv)
        if ("^*_FERDIG_*^" in s):
            return s.replace("^*_FERDIG_*^", "")

        s += self._utvidPotensielleNøkler(alltidMed, muligeUtv)
        return s

    def _sjekkAlltidMed(self, alltidMed, muligeUtv):
        s = ""
        tillukkning = self._FDer.tillukning(alltidMed)
        s += "Sjekker først om {" + str(alltidMed) + "} er en kandidatnøkkel ved å beregne tillukningen: "
        s += "{" + str(alltidMed) + "}+ = {" + str(tillukkning) + "}\n"
        if (tillukkning.set() == self._attributes.set()):
            self._kandidatnøkler.append(alltidMed)
            muligeUtv.removeDuplicatesFrom(tillukkning)
            s += "Siden tillukningen inneholder alle attributtene til relasjonen, så er dette en kandidatnøkkel.\n"
            s += "Alle videre utvidelser vil føre til ikke-minimale supernøkler, altså er {" + str(alltidMed) + "} den eneste kandidatnøkkelen til " + self._navn + "."
            return s + "^*_FERDIG_*^"
        else:
            s += "Siden tillukningen ikke inndeholder alle attributtene til relasjonen, så er dette ikke en kandidatnøkkel, og vi må utvide med flere attributter.\n"
            alleredeFunnet = tillukkning.commonElements(muligeUtv)
            muligeUtv.removeDuplicatesFrom(alleredeFunnet)
            if (len(alleredeFunnet) == 1):
                s += "Attributtet " + str(alleredeFunnet) + " forekommer allerede i tillukningen, og derfor er det ikke vits å utvide med det videre."
            elif (len(alleredeFunnet) > 1):
                s += "Attributtene " + str(alleredeFunnet) + " forekommer allerede i tillukningen, og derfor er det ikke vits å utvide med de videre."
        s += "\n"
        return s

    def _utvidPotensielleNøkler(self, alltidMed, muligeUtv):
        s = ""
        # Finner alle kandidatnøkler med å utvide tidligere "mislykkede" med én og én attributt
        ikkeNøkkel = [alltidMed.copy()]

        # For å ikke forkaste en att før alle kombinasjoner i dette "laget" har prøvd seg med den, selv om man finner en nøkkel i én av dem
        ikkeNøkkelLayers = [0]
        forkastThisLayer = []

        while (len(ikkeNøkkel) != 0):
            utgangspunkt = ikkeNøkkel.pop(0)
            layer = ikkeNøkkelLayers.pop(0)

            # Må gjøre dobbbeltarbeid her for å unngå å skrive ut unødvendige utvidelser
            utvidMed = MengdeAttributter([x for x in muligeUtv if x not in utgangspunkt], TEXT_TAG)
            utvidMed = MengdeAttributter(self._fjernDuplikatNøkler(utgangspunkt, utvidMed), TEXT_TAG)
            utvidMed = MengdeAttributter(self._fjernAlleredeSjekket(utgangspunkt, utvidMed, ikkeNøkkel), TEXT_TAG)
            if (len(utvidMed) == 0):
                continue

            s += "Utvider {" + str(utgangspunkt) + "} med " + str(utvidMed) + "\n"
            for att in utvidMed:
                ny = utgangspunkt.copy()
                ny.add(att)
                ny.sort()
                tillukkning = self._FDer.tillukning(ny)

                s += "- {" + str(ny) + "}+ = {" + str(tillukkning) + "}. "
                if (tillukkning.set() == self._attributes.set()):
                    # Duplikater kan forekomme, Utvide {C D F} med E == Utvide {C E F} med D
                    if (self._duplikatNøkkel(self._kandidatnøkler, ny)):
                        s += "En kandidatnøkkel, men et duplikat av en tidligere.\n"
                    elif ny.erSupernøkkel(self._kandidatnøkler):
                        s += "En nøkkel, men en ikke-minimal supernøkkel.\n"
                    else:
                        s += "Altså er " + str(ny) + " en kandidatnøkkel.\n"
                        self._kandidatnøkler.append(ny)

                        if (layer in ikkeNøkkelLayers):
                            forkastThisLayer.append(att)
                        else:
                            muligeUtv.remove(att)
                            muligeUtv.removeDuplicatesFrom(forkastThisLayer)
                else:
                    # Sjekker om duplikat for å ikke legge den til i ikkeNøkkel 2 ganger
                    if (not self._duplikatNøkkel(ikkeNøkkel, ny)):
                        ikkeNøkkel.append(ny)
                        ikkeNøkkelLayers.append(layer + 1)
                    s += "Altså ikke en kandidatnøkkel, fortsetter å utvide denne (dersom den ikke blir en supernøkkel).\n"

            s += "\n"

        s += "Alle videre utvidelser vil føre til ikke-minimale supernøkler, så stopper utvidelsene.\n"
        s += "Kandidatnøkkelene til " + self._navn + " er: " + self.strKandidatnøkler()
        return s

    def _duplikatNøkkel(self, nøkler, mulig):
        duplikat = False
        for n in nøkler:
            if (n.set() == mulig.set()):
                return True
        return False

    def _fjernDuplikatNøkler(self, utgangspunkt, attributter):
        utvidMed = []
        for att in attributter:
            muligNøkkel = utgangspunkt.copy()
            muligNøkkel.add(att)
            if not (muligNøkkel.erSupernøkkel(self._kandidatnøkler)):
                utvidMed.append(att)
        return utvidMed

    def _fjernAlleredeSjekket(self, utgangspunkt, attributter, ikkeNøkkel):
        utvidMed = []
        for att in attributter:
            muligNøkkel = utgangspunkt.copy()
            muligNøkkel.add(att)
            if not (self._duplikatNøkkel(ikkeNøkkel, muligNøkkel)):
                utvidMed.append(att)
        return utvidMed



    def bestemNormalform(self):
        if (self._normalform != None):
            return "Normalformen til " + self._navn + ": " + self._normalform + "\n"

        s = ""
        s += self.finnKandidatnøkler() + "\n"
        s += "\n"

        s =  "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
        s += " Finner den høyeste normalformen som " + self._navn + " tilfredsstiller\n"
        s += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"

        s += self._skrivOmFDer()
        s += "\n"
        s += self.finnKandidatnøkler()
        s += "\n"

        s += "\n"
        ss, self._normalform = self._FDer.bestemNormalform(self._kandidatnøkler)
        return s + ss

    def _skrivOmFDer(self):
        s = ""
        s += "Skriver om FDer til å kun ha ett attributt på høyresiden:\n"

        if (self._FDer.kreverOmskriving()):
            self._FDer.omskrivEnPåHøyre()

        s += str(self._FDer) + "\n"
        return s

    def tapsfriDekomponering(self):
        s = ""
        s += self.finnKandidatnøkler() + "\n"
        s += "\n"

        s += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
        s += " Tapsfri dekomponering av relasjonen " + self._navn + " til BCNF\n"
        s += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"

        s += "Relasjonen: " + str(self) + "\n\n"

        s += self.finnKandidatnøkler() + "\n"
        s += "\n"
        s += self._skrivOmFDer()
        s += "\n"

        dekomponerte = []
        s += self._tapsfriDekompIter(dekomponerte, "S")
        s += "\n"

        s += "Resultatet av den tapsfrie dekomponeringen av "  + str(self) + ":\n"
        for rel in dekomponerte:
            s += " - " + str(rel) + "\n"
        return s

    def _tapsfriDekompIter(self, dekomponerte, navn=None):
        s = ""
        s += "-=( Relasjon: " + self._navn + " )=-\n"
        s += "Går gjennom hver FD og sjekker om noen bryter med BCNF:\n"
        ss, fd = self._FDer.fdIkkeBCNF(self._kandidatnøkler)
        s += ss

        if (fd == None):
            s += "Siden alle FDene er på BCNF så er også relasjonen " + self._navn + " på BCNF, og må ikke dekomponeres videre.\n\n"
            dekomponerte.append(self)
            return s

        s += "Relasjonen bryter med BCNF siden en av FDene gjør det, og må derfor dekomponeres.\n"
        s += "\n"

        tillukning = self._FDer.tillukning(fd.left())
        s += "Beregner tillukningen til FDen som bryter: {" + str(fd.left()) + "}+ = {" + str(tillukning) + "}\n"

        if (navn == None):
            navn = self._navn
        S1, S2 = self._splittRelasjon(fd.left(), tillukning, navn)

        fortsettMed = []  #Gjøres kun uskriftens skyld
        s += "Dekomponerer " + self._navn + " til:\n"
        for rel in [S1, S2]:
            s += " - " + str(rel) + ". FDer: " + rel.strFDer() + ". "
            rel.finnKandidatnøkler()
            if (len(rel._kandidatnøkler) > 1): s += "Kandidatnøkler: "
            else: s += "Kandidatnøkkel: "
            s += rel.strKandidatnøkler() + ".\n"

            ss, ferdig = rel._sjekkOmFerdig()
            s += "   " + ss + "\n\n"
            if ferdig:
                dekomponerte.append(rel)
            else:
                fortsettMed.append(rel)

        for rel in fortsettMed: #Ikke nødvendig, gjøres kun for uskriftens skyld
            s += "\n"
            s += rel._tapsfriDekompIter(dekomponerte)
        return s


    def _splittRelasjon(self, venstreSide, attS1, navn):
        dataS1 = navn + "1(" + attS1.sorted().strCommaSeparated() + ")"
        FDerS1 = self._FDer.gyldigeFDer(attS1)
        S1 = Relasjon(dataS1, FDerS1)

        attS2 = self._attributes.copy()
        attS2.removeDuplicatesFrom(attS1)
        attS2.addAll(venstreSide, "front")
        dataS2 = navn + "2(" + attS2.sorted().strCommaSeparated() + ")"
        FDerS2 = self._FDer.gyldigeFDer(attS2)
        S2 = Relasjon(dataS2, FDerS2)
        return S1, S2

    # Brukes for å stoppe det rekursive kallet på _tapsfriDekompIter, sånn at det blir mindre tekst
    # Ikke nødvendig for å løse oppgaven
    def _sjekkOmFerdig(self):
        s = ""
        if (len(self._FDer) == 0):
            s += "Siden relasjonen ikke har noen FDer så er den på BCNF, og må ikke dekomponeres videre."
            return s, True
        elif (len(self._FDer) == 1):
            self.bestemNormalform()
            if (self._normalform == "BCNF"):
                if (self._kandidatnøkler[0].set() == self._FDer[0].left().set()):
                    s += "Ser at denne er på BCNF fordi kun en FD holder, så venstresiden tilsvarer kandidatnøkkelen. Trenger ikke å dekomponere denne videre."
                    return s, True
                else:
                    s += "******************** WTF TRUDDE IKKE DETTAN KUNNE SKJE ***********************************"#"Ser at denne er på BCNF fordi venstresiden i FDen er en supernøkkel. Trenger ikke å dekomponere denne videre."
        else:
            self.bestemNormalform()
            if (self._normalform == "BCNF"):
                s += "Denne er på BCNF fordi venstresiden i alle FDene er supernøkler. Trenger ikke å dekomponere denne videre."
                return s, True

        s += "Fortsetter med " + self._navn + "."
        return s, False
