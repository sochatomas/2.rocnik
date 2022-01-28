import random
import timeit

pocet_riadkov = 5
pocet_stlpcov = 5
max_velkost_spracovane = 17*pocet_riadkov**(pocet_stlpcov-1)*100
max_velkost_vygenerovane = 15*pocet_riadkov**pocet_stlpcov*100


class Uzol:
    stav = None
    predchodca = None
    hodnota = None

    def __init__(self, stav, predchodca):
        self.stav = stav
        self.predchodca = predchodca


def list_na_string(stav):                    # prevedie list na string
    string = ""
    for riadok in stav:
        string += ' '.join(riadok)
        string += ' '
    return string


def riesitelnost_hlavolamu(vstupna_pozicia, cielova_pozicia):
    pocet_inverzii_vstup = 0
    pocet_inverzii_ciel = 0
    pozicia_m_vstup = 0
    pozicia_m_ciel = 0

    for i in range(0,pocet_riadkov):                #cyklus v cykle na prejdenie vsetkych prvkov (na porovnavanie)
        for j in range(0,pocet_stlpcov):

            if vstupna_pozicia[i][j] == 'm':        # najdenie prázdneho policka
                pozicia_m_vstup = i+1
            if cielova_pozicia[i][j] == 'm':
                pozicia_m_ciel = i+1

            for poradie in range((i*pocet_stlpcov)+j, pocet_riadkov*pocet_stlpcov):     # cyklus na prejdenie vsetkych prvkov nasledujucich po prvku [i][j]
                if (vstupna_pozicia[i][j] != 'm') & (vstupna_pozicia[int(poradie/pocet_stlpcov)][poradie%pocet_stlpcov] != 'm'):        # najdenie cisla mensieho ako porovnavane
                    if int(vstupna_pozicia[i][j]) > int(vstupna_pozicia[int(poradie/pocet_stlpcov)][poradie%pocet_stlpcov]):
                        pocet_inverzii_vstup += 1

                if (cielova_pozicia[i][j] != 'm') & (cielova_pozicia[int(poradie/pocet_stlpcov)][poradie%pocet_stlpcov] != 'm'):
                    if int(cielova_pozicia[i][j]) > int(cielova_pozicia[int(poradie/pocet_stlpcov)][poradie%pocet_stlpcov]):
                        pocet_inverzii_ciel += 1

    # print(pocet_inverzii_vstup)
    # print(pocet_inverzii_ciel)

    if(pocet_stlpcov %2 != 0) & (pocet_inverzii_vstup%2 == pocet_inverzii_ciel%2):            # pocet stlpcov je neparny
        return 1
    elif (pocet_stlpcov %2 ==0) & ((pocet_inverzii_vstup+pozicia_m_vstup)%2 == (pocet_inverzii_ciel+pozicia_m_ciel)%2):     # pocet stlpcov je neparny
        return 1
    else:
        return -1


def pohyb(stary_uzol, final_stav, cislo_heuristiky, spracovane_uzly, vygenerovane_uzly, pozicia_medzery, smer_pohybu):

    riadok = pozicia_medzery[0] - 1
    stlpec = pozicia_medzery[1] - 1

    if stary_uzol.stav[riadok][stlpec] == 'm':
        novy_stav = list(map(list, stary_uzol.stav))              # pre kazdy list v liste stav zavolá konstruktor na vytvorenie noveho listu

        if smer_pohybu == "vpravo":                                 # vyber smeru pohybu
            novy_stav[riadok][stlpec] = novy_stav[riadok][stlpec-1]
            novy_stav[riadok][stlpec - 1] = 'm'

        elif smer_pohybu == "vlavo":
            novy_stav[riadok][stlpec] = novy_stav[riadok][stlpec + 1]
            novy_stav[riadok][stlpec + 1] = 'm'

        elif smer_pohybu == "hore":
            novy_stav[riadok][stlpec] = novy_stav[riadok + 1][stlpec]
            novy_stav[riadok + 1][stlpec] = 'm'

        elif smer_pohybu == "dole":
            novy_stav[riadok][stlpec] = novy_stav[riadok - 1][stlpec]
            novy_stav[riadok - 1][stlpec] = 'm'

        stav_str = list_na_string(novy_stav)

        if spracovane_uzly.get(stav_str, None) is None:                 # vytvorenie noveho uzla
            novy_uzol = Uzol(novy_stav, stary_uzol)
            novy_uzol.hodnota = vyber_heuristiky(novy_uzol, final_stav, cislo_heuristiky)
            vlozenie_do_listu(vygenerovane_uzly, novy_uzol)             # vlozenie do listu


def heuristika_1(akt_uzol,ciel_stav):
    pocet = 0

    for riadok in range(len(ciel_stav)):                # prejdenie vsetkych policok
        for stlpec in range(len(ciel_stav[riadok])):

            if (akt_uzol.stav[riadok][stlpec] != 'm') & (ciel_stav[riadok][stlpec] != akt_uzol.stav[riadok][stlpec]):
                pocet += 1                                              # policko nieje na svojej cielovej pozicii

    return pocet


def heuristika_2(akt_uzol, ciel_stav):
    hodnota = 0

    for riadok in range(pocet_riadkov):                     # prejdenie vsetkych policok
        for stlpec in range(pocet_stlpcov):
                                                            # policko nieje na svojom mieste
            if (akt_uzol.stav[riadok][stlpec] != ciel_stav[riadok][stlpec]) & (akt_uzol.stav[riadok][stlpec] != 'm'):

                for riadok_2 in range(pocet_riadkov):       #prejdenie vsetkych policok
                    for stlpec_2 in range(pocet_stlpcov):

                        if akt_uzol.stav[riadok][stlpec] == ciel_stav[riadok_2][stlpec_2]:  # najdenie cielovej pozicie daneho policka
                            hodnota += abs(riadok_2-riadok) + abs(stlpec_2 - stlpec)        # vzdialenost od cielovej pozicie
                            break

    return hodnota


def heuristika_3(akt_uzol, ciel_stav):                  # heuristika 2 + polovica z prvej
    hodnota = 0

    for riadok in range(pocet_riadkov):
        for stlpec in range(pocet_stlpcov):

            if (akt_uzol.stav[riadok][stlpec] != ciel_stav[riadok][stlpec]) & (akt_uzol.stav[riadok][stlpec] != 'm'):
                hodnota += 0.5

                for riadok_2 in range(pocet_riadkov):
                    for stlpec_2 in range(pocet_stlpcov):

                        if akt_uzol.stav[riadok][stlpec] == ciel_stav[riadok_2][stlpec_2]:
                            hodnota += (abs(riadok_2 - riadok) + abs(stlpec_2 - stlpec))
                            break

    return hodnota


def vyber_heuristiky(akt_uzol, ciel_stav, cislo_heuristiky):

    if cislo_heuristiky == 2:
        return heuristika_2(akt_uzol, ciel_stav)

    elif cislo_heuristiky == 1:
        return heuristika_1(akt_uzol, ciel_stav)

    else:
        return heuristika_3(akt_uzol, ciel_stav)


def vlozenie_do_listu(vygenerovane_uzly,potencialny_uzol):
    index = 0

    for prvok in vygenerovane_uzly:
        if prvok.hodnota >= potencialny_uzol.hodnota:

            if prvok.stav == potencialny_uzol.stav:                # najdenie uz rovnakeho stavu v liste vygenerovanych
                return

            if (prvok.hodnota == potencialny_uzol.hodnota) & (index == 0):      # zistenie pozicie prveho s rovnakou hodnotou
                index = vygenerovane_uzly.index(prvok)

            # if (prvok.hodnota == potencialny_uzol.hodnota) & (random.randint(0,1) == 1):      #vkladanie na nahodnu poziciu vramci moznosti
            #     index = vygenerovane_uzly.index(prvok)

            if prvok.hodnota > potencialny_uzol.hodnota:                    # vlozenie do listu
                vygenerovane_uzly.insert(index, potencialny_uzol)
                return


def najdenie_cesty(akt_uzol, ciel_stav, cislo_heuristiky):

    pocet_iteracii = 0
    pozicia_medzery = [0,0]
    spracovavany_uzol = None
    spracovane_uzly_dict = {}
    print("hodnota heuristiky: {}".format(vyber_heuristiky(akt_uzol,ciel_stav,cislo_heuristiky)))

    hlbka = 0
    kluc = 0                                    # premenna na zapametanie hodnoty kluca vyberaneho z dict
    akt_uzol.hlbka = 0
    akt_uzol.hodnota = 10000
    vygenerovane_uzly = [akt_uzol]

    start = timeit.default_timer()


    while(akt_uzol.stav != ciel_stav) & (akt_uzol is not None):

        pocet_iteracii += 1

        if pocet_iteracii > 5000000:
            print("cestu sa nepodarilo nájsť")
            break

        for riadok in range(pocet_riadkov):                         #prejdenie vsetkych policok a najdenie medzery
            for stlpec in range(pocet_stlpcov):

                if akt_uzol.stav[riadok][stlpec] == 'm':
                    pozicia_medzery[0] = riadok+1
                    pozicia_medzery[1] = stlpec+1
                    break

        if pozicia_medzery[0] != pocet_riadkov:                     # zavolanie funkcie pre vygenerovanie nového uzla
            pohyb(akt_uzol, ciel_stav, cislo_heuristiky, spracovane_uzly_dict, vygenerovane_uzly, pozicia_medzery, "hore")

        if pozicia_medzery[0] != 1:
            pohyb(akt_uzol, ciel_stav, cislo_heuristiky, spracovane_uzly_dict, vygenerovane_uzly, pozicia_medzery, "dole")

        if pozicia_medzery[1] != 1:
            pohyb(akt_uzol, ciel_stav, cislo_heuristiky, spracovane_uzly_dict, vygenerovane_uzly, pozicia_medzery, "vpravo")

        if pozicia_medzery[1] != pocet_stlpcov:
            pohyb(akt_uzol, ciel_stav, cislo_heuristiky, spracovane_uzly_dict, vygenerovane_uzly, pozicia_medzery, "vlavo")

        try:
            spracovavany_uzol = vygenerovane_uzly.pop(0)                # vyberie prvok z listu, ak nieje prazdny
        except IndexError:
            print("prazdny list, nepodarilo sa nájsť riešenie")         # skonci s neuspechom
            exit(-1)

        stav_str = list_na_string(spracovavany_uzol.stav)               # vytvorenie stringu z akt. stavu pre ulozenie do dict

        if len(spracovane_uzly_dict) < max_velkost_spracovane:          # vlozenie do dict
            spracovane_uzly_dict[stav_str] = len(spracovane_uzly_dict)+1

        elif len(spracovane_uzly_dict) == max_velkost_spracovane:        # vybratie a vlozenie noveho
            for key in spracovane_uzly_dict.keys():                      # ziskanie hodnoty kluca prveho stavu v dict
                kluc = key
                break
            spracovane_uzly_dict.pop(kluc)
            spracovane_uzly_dict[stav_str] = 0

        akt_uzol = spracovavany_uzol                                      # nastavenie aktualneho uzla na dalsi

        while len(vygenerovane_uzly) > max_velkost_vygenerovane:            # vybratie uzlov z listu vygenerovanych, s najvecsou hodnotou
            vygenerovane_uzly.pop()

    end = timeit.default_timer()

    if akt_uzol.stav == ciel_stav:                                          # uspesne najdenie cesty
        print(round(end - start,4), "sekund")
        print("pocet iteracii: {}".format(pocet_iteracii))

        if cislo_heuristiky == 2:                                       # otvorenie ext. suboru
            output_file = open("cesta_vypis.txt", "w")
            print("Cielový stav: ", file=output_file)

        while akt_uzol.predchodca is not None:                          # vypocitanie velkosti cesty

            if cislo_heuristiky == 2:                                   # vypis do ext. suboru
                vypis_stavu(akt_uzol.stav, output_file)
                print("\n", file=output_file)

            akt_uzol = akt_uzol.predchodca
            hlbka += 1

        if cislo_heuristiky == 2:                                     # zavretie ext. suboru
            print("Počiatočný stav: ", file=output_file)
            vypis_stavu(akt_uzol.stav, output_file)
            output_file.close()

        print("hlbka: {}".format(hlbka))
        print("Cesta bola nájdená!!!")

        return 1
    else:
        return -1


def generator():                            # generovanie vstupov

    mnozina_cisel_vstup = list(map(str,range(1, pocet_riadkov*pocet_stlpcov)))      #vytvorenie mnoziny cisel
    mnozina_cisel_ciel = list(map(str,range(1, pocet_riadkov * pocet_stlpcov)))
    mnozina_cisel_vstup.append('m')
    mnozina_cisel_ciel.append('m')
    vstupna_pozicia = []
    cielova_pozicia = []
    vystup = []

    while len(mnozina_cisel_vstup):                             # nahodne usporiadanie policok
        rand = random.randint(0, len(mnozina_cisel_vstup)-1)
        vstupna_pozicia.append((mnozina_cisel_vstup.pop(rand)))

        rand = random.randint(0, len(mnozina_cisel_ciel)-1)
        cielova_pozicia.append((mnozina_cisel_ciel.pop(rand)))
                                                                    # rozdelie listu na viacej malych v 1 liste podla poctu stlpcov
    vstupna_pozicia = [vstupna_pozicia[i*pocet_stlpcov:i*pocet_stlpcov+pocet_stlpcov] for i in range(0, pocet_riadkov)]
    cielova_pozicia = [cielova_pozicia[i*pocet_stlpcov:i*pocet_stlpcov+pocet_stlpcov] for i in range(0, pocet_riadkov)]

    vystup.append(vstupna_pozicia)
    vystup.append(cielova_pozicia)
    return vystup


def vypis_stavu(stav,subor):                      # vypisanie stavu na konzolu
    for riadok in stav:
        for prvok in riadok:

            if subor is not None:                                   #výpis do txt suboru
                print("{: ^4}".format(prvok), end='', file=subor)

            else:
                print("{: ^4}".format(prvok), end='')

        if subor is not None:
            print("\n", file=subor)

        else:
            print()


def tester():

    dvojica = generator()                                   # vygenerovanie dvojice stavov
    zaciatok = dvojica[0]
    ciel = dvojica[1]

    while riesitelnost_hlavolamu(zaciatok, ciel) == -1:         # najdenie riesitelnej dvojice
        dvojica = generator()
        zaciatok = dvojica[0]
        ciel = dvojica[1]

    print("Zaciatocny stav: ")
    vypis_stavu(zaciatok,None)
    print("\nCielovy stav: ")
    vypis_stavu(ciel,None)
    root = Uzol(zaciatok, None)

    print("\nheuristika 3\n-----------------------")
    najdenie_cesty(root, ciel, 3)                                   # zavolanie funkcie pre najdenie cesty
    print("\nheuristika 2\n-----------------------")
    najdenie_cesty(root, ciel, 2)
    print("\nheuristika 1\n-----------------------")
    najdenie_cesty(root, ciel, 1)


if __name__ == '__main__':

    tester()




