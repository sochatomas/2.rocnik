from math import sqrt,exp
import random
import timeit
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt

pocet_miest = 20
pocet_iteracii = 1000
velkost_okolia = pocet_miest-1

tabu_list_velkost = 10

teplota = 50
faktor_ochladzovania = 0.9951


class Vektor:
    stav = None
    vzdialenost = None
    iteracia = None


def generator():  # generovanie vstupov
    stav = []

    while len(stav) != pocet_miest:
        suradnice_mesta = [random.randint(0, 200), random.randint(0, 200)]

        try:
            stav.index(suradnice_mesta)
        except ValueError:
            stav.append(suradnice_mesta)

    vektor = Vektor()
    vektor.stav = stav
    vektor.vzdialenost = vypocet_vzdialenosti(stav)

    return vektor


def vypocet_vzdialenosti(stav):
    vzdialenost = 0
    for i in range(0,pocet_miest-1):            # pomocou pytagorovej vety vzdialenosť každej dvojice susedných miest
        vzdialenost += sqrt((stav[i][0] - stav[i+1][0])**2 + (stav[i][1] - stav[i+1][1])**2)
    vzdialenost += sqrt((stav[0][0] - stav[-1][0]) ** 2 + (stav[0][1] - stav[-1][1]) ** 2)
    return round(vzdialenost, 2)


def novy_stav_gen(vektor):          # generovanie nového stavu

    novy_stav = list(map(list,vektor.stav))
    index_1 = random.getrandbits(7)%(pocet_miest)     #vygenerovanie nahodneho čisla
    index_2 = random.getrandbits(7)%(pocet_miest)
    while index_1 == index_2:
        index_2 = random.getrandbits(7)%(pocet_miest-1)

    pomocna_premenna = novy_stav[index_1]               # výmena miest
    novy_stav[index_1] = novy_stav[index_2]
    novy_stav[index_2] = pomocna_premenna

    return novy_stav


def search_algorithm(typ_algoritmu,akt_vektor):
    # pre tester na 20 miest
    # akt_vektor.stav = [[166, 76], [60, 30], [176, 50], [85, 0], [73, 72], [200, 20], [92, 85], [106, 75], [53, 109], [145, 5], [173, 107], [166, 44], [120, 152], [9, 192], [110, 198], [3, 82], [167, 143], [62, 72], [73, 169], [101, 17]]
    # pre tester na 30 miest
    # akt_vektor.stav = [[24, 88], [110, 43], [104, 49], [52, 48], [52, 74], [119, 192], [139, 33], [45, 112], [134, 56], [29, 28], [108, 73], [129, 86], [18, 16], [86, 45], [133, 98], [120, 138], [99, 32], [48, 114], [165, 82], [117, 161], [99, 144], [90, 200], [177, 13], [195, 62], [122, 152], [182, 14], [19, 106], [60, 96], [29, 66], [132, 5]]
    # akt_vektor.vzdialenost = vypocet_vzdialenosti(akt_vektor.stav)

    y = []              #list vzdialeností
    x = []              # list iteracii
    
    tabu_list = [akt_vektor.stav]
    global_best = Vektor()
    global_best.vzdialenost = akt_vektor.vzdialenost
    print(typ_algoritmu, "algoritmus\n-------------------------------")
    print("Zaciatocna cesta: {0}\nvzdialenost: {1}".format(akt_vektor.stav,akt_vektor.vzdialenost))

    start = timeit.default_timer()
    for akt_iteracia in range(pocet_iteracii):          # prejdenie vsetkých iteracii

        okolie_best = Vektor()
        okolie_best.vzdialenost = 100000
        x.append(akt_iteracia+1)

        # výber algoritmu
        if typ_algoritmu == "Hill-climbing":
            akt_vektor = hill_climbing(okolie_best, akt_vektor)
            global_best.stav = akt_vektor.stav
            global_best.vzdialenost = akt_vektor.vzdialenost

        elif typ_algoritmu == "TS":
            tabu_list, global_best, akt_vektor = tabu_search(tabu_list, okolie_best, global_best, akt_vektor)

        elif typ_algoritmu == "SA":
            akt_vektor = simulated_annealing(akt_vektor)

            if global_best.stav != akt_vektor.stav:
                global_best.iteracia = akt_iteracia + 1

            global_best.stav = akt_vektor.stav
            global_best.vzdialenost = akt_vektor.vzdialenost

        y.append(akt_vektor.vzdialenost)

    end = timeit.default_timer()
    print("Koncova cesta: {0}\nvzdialenost: {1}".format(global_best.stav, global_best.vzdialenost))
    print(round(end - start, 4), "sekund\n")

    # zakomentovať vykreslenie grafov pri vykonavaní testov
    vykreslenie_grafu(x,y,typ_algoritmu)
    a = [i[0] for i in global_best.stav]        # x-ove suradnice miest hladanej cesty
    b = [i[1] for i in global_best.stav]        # y- ove suradnice miest hladanej cesty
    a.append(global_best.stav[0][0])            # pridanie prvých miest z dovodu vykreslenia uzavretej cesty
    b.append(global_best.stav[0][1])

    vykreslenie_cesty(a,b,typ_algoritmu)
    return global_best.vzdialenost,round(end - start, 4),global_best.iteracia


def tabu_search(tabu_list, okolie_best, global_best, akt_vektor):
    okolie = {}

    while len(okolie) < velkost_okolia:             # naplnenie okolia jedinecnými potomkami
        novy_stav = novy_stav_gen(akt_vektor)

        try:
            tabu_list.index(novy_stav)
            continue
        except ValueError:
            okolie[vypocet_vzdialenosti(novy_stav)] = novy_stav

    okolie_keys = sorted(okolie.keys())             # zoradenie klucov vzostupne a vybratie najlepsieho z okolia
    okolie_best.stav = okolie[okolie_keys[0]]
    okolie_best.vzdialenost = vypocet_vzdialenosti(okolie_best.stav)

    if okolie_best.vzdialenost < global_best.vzdialenost:   # najdenie global_best
        global_best = okolie_best

    if len(tabu_list) == tabu_list_velkost:                # odobratie z tabu listu
        tabu_list.pop(0)
    # if okolie_best.vzdialenost < akt_vektor.vzdialenost:
    tabu_list.append(okolie_best.stav)                      # pridanie do tabu listu



    return tabu_list,global_best,okolie_best


def hill_climbing(okolie_best, akt_vektor):
    okolie = {}

    while len(okolie) < velkost_okolia:                   # naplnenie okolia jedinecnými potomkami
        novy_stav = novy_stav_gen(akt_vektor)
        okolie[vypocet_vzdialenosti(novy_stav)] = novy_stav

    okolie_keys = sorted(okolie.keys())                     # vybratie najlepsieho potomka
    okolie_best.stav = okolie[okolie_keys[0]]
    okolie_best.vzdialenost = vypocet_vzdialenosti(okolie_best.stav)

    if okolie_best.vzdialenost < akt_vektor.vzdialenost:    # najdenie lepsej cesty
        akt_vektor = okolie_best

    return akt_vektor


def simulated_annealing(akt_vektor):
    okolie =[]
    global teplota
    teplota = teplota * faktor_ochladzovania            # znižovanie teploty
    novy_vektor = Vektor
    novy_vektor.vzdialenost = akt_vektor.vzdialenost
    novy_vektor.stav = akt_vektor.stav

    while len(okolie) < velkost_okolia:                # generovanie jedinecných potomkov
        novy_stav = novy_stav_gen(akt_vektor)
        #okolie.append(novy_stav_gen(akt_vektor))

        try:
            okolie.index(novy_stav)
            continue
        except ValueError:
            okolie.append(novy_stav)

    while True:                                         # hladanie akceptovaneho potomka
        index = int(random.random()*(len(okolie)-1))
        potomok_vzdialenost = vypocet_vzdialenosti(okolie[index])

        if potomok_vzdialenost < akt_vektor.vzdialenost:    # 100% akceptovanie
            novy_vektor.vzdialenost = potomok_vzdialenost
            novy_vektor.stav = okolie[index]
            return novy_vektor

        elif potomok_vzdialenost > akt_vektor.vzdialenost:  # akceptovanie na základe pravdepodobnosti
            rozdiel_vzdialenosti = abs(potomok_vzdialenost-akt_vektor.vzdialenost)
            pravdepodobnost = exp(-(rozdiel_vzdialenosti / teplota))

            if random.random() <= pravdepodobnost:
                novy_vektor.vzdialenost = potomok_vzdialenost
                novy_vektor.stav = okolie[index]
                return novy_vektor
            else:
                okolie.pop(index)
                if len(okolie) == 0:
                    return novy_vektor
        else:
            okolie.pop(index)
            if len(okolie) == 0:
                return  novy_vektor


def vykreslenie_grafu(x,y,typ_algoritmu):
    plot.plot(x, y)
    plot.xlabel('počet iteracii')
    plot.ylabel('vzdialenosť')
    plot.title(typ_algoritmu + " vývoj hľadania optimalneho riešenia")
    plot.show()


def vykreslenie_cesty(x,y,typ_algoritmu):
    plot.plot(x, y, marker='o', markerfacecolor='black')
    # plot.xlabel('x-ova suradnica')
    # plot.ylabel('y-ova suradnica')
    plot.xlabel('x-ova suradnica')
    plot.ylabel('y-ova suradnica')
    plot.title(typ_algoritmu + " cesta")
    plot.show()


def test_tabu_list():                       # testovanie roznych velkosti tabu listu
    priemerne_vzdialenosti = []
    priemerne_casy = []
    testovacie_velkosti = [5,10,20,30,50]
    pocet_opakovani = 10
    akt_vektor = generator()

    for i in testovacie_velkosti:
        global tabu_list_velkost
        tabu_list_velkost = i

        cas = 0
        vzdialenost = 0
        for j in range(pocet_opakovani):

            vzdialenost_1,cas_1,iteracia = search_algorithm("TS", akt_vektor)
            cas += cas_1
            vzdialenost += vzdialenost_1

        priemerne_casy.append(cas/pocet_opakovani)
        priemerne_vzdialenosti.append(vzdialenost/pocet_opakovani)

    vykreslenie_cesty(testovacie_velkosti,priemerne_casy,"TS")
    vykreslenie_cesty(testovacie_velkosti,priemerne_vzdialenosti,"TS")


def test_simulovane_zihanie():          # testovanie roznych parametrov pri simulovanom zihani
    priemerne_vzdialenosti = []
    najlepsie_vzdialenosti = []
    konecna_teplota = []
    global_best_iteracia_list = []

    testovacie_velkosti = [[50, 0.9951],[50, 0.95],[50, 0.999], [5000, 0.981]]
    testovania = [1,2,3,4]
    akt_vektor = generator()

    for i in testovacie_velkosti:
        global teplota
        global faktor_ochladzovania
        teplota = i[0]
        faktor_ochladzovania = i[1]

        vzdialenost = 0
        min_vzdialenost = 100000
        global_best_iteracia = 0

        for j in range(5):
            vzdialenost_1, cas_1, iteracia = search_algorithm("SA",akt_vektor)

            vzdialenost += vzdialenost_1
            if min_vzdialenost > vzdialenost_1:
                min_vzdialenost = vzdialenost_1
                global_best_iteracia = iteracia
            teplota = i[0]

        priemerne_vzdialenosti.append(vzdialenost / 5)
        najlepsie_vzdialenosti.append(min_vzdialenost)
        konecna_teplota.append(teplota)
        global_best_iteracia_list.append(global_best_iteracia)

    vykreslenie_cesty(testovania, najlepsie_vzdialenosti, "SA najlepsia vzdialenost")
    vykreslenie_cesty(testovania, priemerne_vzdialenosti, "SA priemerna vzdialenost")
    vykreslenie_cesty(testovania, konecna_teplota, "SA konecna teplota")
    vykreslenie_cesty(testovania, global_best_iteracia_list, "SA gb iteracia")


def test_porovnanie_algoritmov():               # porovnanie rôznych algoritmov
    global pocet_miest
    vzdialenost_ts_list = []
    vzdialenost_hc_list = []
    vzdialenost_sa_list = []

    cas_ts_list = []
    cas_hc_list = []
    cas_sa_list = []

    list_pocet_miest = [20,30,40]
    for mnozstvo_miest in list_pocet_miest:

        pocet_miest = mnozstvo_miest
        vzdialenost_ts = 0
        vzdialenost_hc = 0
        vzdialenost_sa = 0
        cas_ts = 0
        cas_hc = 0
        cas_sa = 0

        akt_vektor = generator()
        for i in range(5):

            vzdialenost_ts1, cas_ts1, iteracia = search_algorithm("TS",akt_vektor)
            vzdialenost_hc1, cas_hc1, iteracia = search_algorithm("Hill-climbing", akt_vektor)
            vzdialenost_sa1, cas_sa1, iteracia =search_algorithm("SA",akt_vektor)

            vzdialenost_ts += vzdialenost_ts1
            vzdialenost_hc += vzdialenost_hc1
            vzdialenost_sa += vzdialenost_sa1
            cas_ts += cas_ts1
            cas_hc += cas_hc1
            cas_sa += cas_sa1

        vzdialenost_ts_list.append(vzdialenost_ts/5)
        vzdialenost_sa_list.append(vzdialenost_sa/5)
        vzdialenost_hc_list.append(vzdialenost_hc/5)
        cas_ts_list.append(cas_ts/5)
        cas_hc_list.append(cas_hc/5)
        cas_sa_list.append(cas_sa/5)
    print(vzdialenost_hc_list)
    print(vzdialenost_sa_list)

    plot.plot(list_pocet_miest, vzdialenost_ts_list, marker='o', markerfacecolor='black', label="tabu search")
    plot.plot(list_pocet_miest, vzdialenost_sa_list, marker='o', markerfacecolor='black', label="simulovane zihanie")
    plot.plot(list_pocet_miest, vzdialenost_hc_list, marker='o', markerfacecolor='black', label="hill-climbing")
    plot.xlabel('pocet miest')
    plot.ylabel('vzdialenost')
    plot.title("vzdialenosti ")
    plt.legend()
    plot.show()

    plot.plot(list_pocet_miest, cas_ts_list, marker='o', markerfacecolor='black', label="tabu search")
    plot.plot(list_pocet_miest, cas_hc_list, marker='o', markerfacecolor='black', label="hill-climbing")
    plot.plot(list_pocet_miest, cas_sa_list, marker='o', markerfacecolor='black', label="simulovane zihanie")
    plot.xlabel('pocet miest')
    plot.ylabel('cas')
    plot.title("casy ")
    plt.legend()
    plot.show()

if __name__ == '__main__':
    akt_vektor = generator()

    search_algorithm("TS",akt_vektor)
    search_algorithm("Hill-climbing",akt_vektor)
    search_algorithm("SA",akt_vektor)
    # print(round(teplota, 4))

    # pri testovani treba zakomentovať vykreslovanie grafov vo funkcii search_algorithm() kvoli vyhnutiu sa velkemu poctu grafov
    # test_tabu_list()
    # test_simulovane_zihanie()
    # test_porovnanie_algoritmov()

