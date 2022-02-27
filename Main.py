from Relasjon import *

TEXT_TAG = "TEXT"
CHAR_TAG = "CHAR"

SPLIT_BY = "→"  # '->' eller '→'


def main():
    #########################
    ##
    ##    INPUT
    ##
    ##  Relasjon: 'Navn(att1, att2, att3,att4,att5)'
    ##
    ##  FDer: Kan være på flere former, gitt av tag over (TEXT eller CHAR),
    ##        alltid max 1 FD per hver linje. Eks:
    ##          - CHAR: "AB → C" eller "A B → C"
    ##          - TEXT: "att1, att2 → att3"
    ##        Husk også å velge SPLIT_BY over!
    ##
    tag = CHAR_TAG  # 'CHAR_TAG' eller 'TEXT_TAG'
    relasjonRaw = "R(A, B, C, D, E, F)"
    FDerRaw = """
        AB → C
        B → E
        D → E
        D → F
        """
    ##
    ##
    #########################


    fd = FunksjonelleAvhengigheter(FDerRaw, tag)
    r = Relasjon(relasjonRaw, fd)
    print("\n\n\n")


    #########################
    ##
    ##    FUNKSJONALITET
    ##      Kommenter ut de som ikke trengs
    ##
    print(r.finnKandidatnøkler(), "\n\n\n")
    print(r.bestemNormalform(), "\n\n\n")
    print(r.tapsfriDekomponering())
    ##
    #########################


def fatalError(msg):
    print("********************************************")
    print("*** FATAL ERROR: " + msg + " ***")
    print("********************************************")
    exit(1)


if __name__ == "__main__":
    main()




# EKSEMPEL 1
# relasjon = "R(A,B,C,D,E,F)"
# FDer = "AB → CD \n CD → AB \n A → E \n C → F"
# tag = CHAR_TAG

# EKSEMPEL 2
# rel = "R(Brnavn, Navn, Adresse, Kurskode, Tittel, Beskrivelse, AntSP, Karakter, Bestått)"
#
# FDer = """
# Brnavn → Navn, Adresse
# Kurskode → Tittel, Beskrivelse, AntSP
# Tittel → Kurskode, Beskrivelse, AntSP
# Brnavn, Kurskode → Karakter
# Karakter → Bestått
# Tittel → Kurskode, Beskrivelse, AntSP
# """
#
# tag = TEXT_TAG
