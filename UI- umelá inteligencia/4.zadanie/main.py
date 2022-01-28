
import random
import timeit
from math import sqrt
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

# vykreslenie grafov
colors = []                     # farby
list_cely_graf = []
cislo_grafu = 1                 # cislo pre ulozenie grafu

centroids_pocet = 20
pocet_bodov = 20000

# ulozenie vysledkov z testovania
list_kmeans_centroid = [0,0,0]
list_kmeans_medoid = [0,0,0]
list_divisive_clustering = [0,0,0]
list_aglomerative_clustering = [0,0,0]
zobrazenie_grafov = True


class Divisive_rozlozenie:
    list_klastrov = None
    predch_rozlozenie = None


class Klaster:
    suradnice = None
    list_bodov = None

class Centroid:
    suradnice = None
    list_bodov = None
    sum_x_suradnic = 0
    sum_y_suradnic = 0
    avg_vzdialenost = 0


def nacitanie_farieb():
    global colors
    file = open("farby.txt", 'r')
    while 1:
        farba = file.readline()
        if not farba:
            break
        colors.append(farba[:-1])

    file.close()


def graf_vsetky_body():
    global list_cely_graf

    for i in range(-7000,7000,75):
        for j in range (-5000,5000,75):
            list_cely_graf.append((i,j))


def generator_start():                      # vygenerovanie prvých 20 bodov
    list_pociatocne_body = []

    while len(list_pociatocne_body) != 20:
        suradnice_mesta = (random.randint(-5000, 5000), random.randint(-5000, 5000))

        if suradnice_mesta not in list_pociatocne_body:
            list_pociatocne_body.append(suradnice_mesta)

    return list_pociatocne_body


def generator_continue(list_pociatocne_body):                   # vygenerovanie dalších bodov
    list_vsetky_body = [x for x in list_pociatocne_body]

    while len(list_vsetky_body) != pocet_bodov:
        rand_index = random.getrandbits(15) % (len(list_vsetky_body))
        rand_bod = list_vsetky_body[rand_index]

        if (abs(rand_bod[1]) == 5000) | (abs(rand_bod[0]) == 5000):
            continue

        if (abs(rand_bod[0]) + 100) < 5000:                         # x-offset
            x_offset = random.getrandbits(8) % 201 - 100
        else:
            max_offset = 5000 - abs(rand_bod[0])
            x_offset = random.getrandbits(8) % max_offset*2+1 - max_offset

        if (abs(rand_bod[1]) + 100) < 5000:                         # y-offset
            y_offset = random.getrandbits(8) % 201 - 100
        else:
            max_offset = 5000 - abs(rand_bod[1])
            y_offset = random.getrandbits(8) % max_offset*2+1 - max_offset

        novy_bod = (rand_bod[0] + x_offset, rand_bod[1] + y_offset)
        list_vsetky_body.append(novy_bod)


    return list_vsetky_body


def najdenie_medoidu(medoid):               # najdenie nového medoidu
    min_vzdialenost = float("inf")
    suradnice = medoid.suradnice

    for bod in medoid.list_bodov:
        vzdialenost = 0
        for bod2 in medoid.list_bodov:
            vzdialenost += sqrt((bod2[0] - bod[0]) ** 2 + (bod2[1] - bod[1]) ** 2)
        vzdialenost = vzdialenost/len(medoid.list_bodov)

        if vzdialenost < min_vzdialenost:
            min_vzdialenost = vzdialenost
            suradnice = bod

    return suradnice,min_vzdialenost


def k_means_centroid(list_vsetky_body):
    list_of_centroids = []
    list_suradnic = []
    max_posun_velkost = 5000

    start = timeit.default_timer()

    while len(list_of_centroids) < centroids_pocet:                             # generovanie nahodnych centroidov
        # centroid_suradnice = [random.randint(-5000, 5000), random.randint(-5000, 5000)]
        index_1 = random.randint(0,len(list_vsetky_body)-1)
        index_2 = random.randint(0,len(list_vsetky_body)-1)
        x_stred = int((list_vsetky_body[index_1][0] + list_vsetky_body[index_2][0])/2)
        y_stred = int((list_vsetky_body[index_1][1] + list_vsetky_body[index_2][1])/2)
        centroid_suradnice = [random.randint(-500, 500) + x_stred, random.randint(-500, 500)+y_stred]

        if centroid_suradnice not in list_suradnic:                 # vygenerovany nový centroid
            centroid = Centroid()
            centroid.suradnice= centroid_suradnice
            centroid.list_bodov = []
            list_of_centroids.append(centroid)
            list_suradnic.append(centroid_suradnice)

    if (centroids_pocet != 2) & zobrazenie_grafov:
        vykreslenie_grafu(list_vsetky_body, list_suradnic)

    while max_posun_velkost > 25:
        max_posun_velkost = 0
        for centroid in list_of_centroids:                      # vynulovanie hodnot
            centroid.list_bodov = []
            centroid.sum_y_suradnic = 0
            centroid.sum_x_suradnic = 0
            centroid.avg_vzdialenost = 0

        for bod in list_vsetky_body:                            # vzdialenosti od centroidu
            min_vzdialenost = 15000
            min_centroid = None

            for centroid in list_of_centroids:
                vzdialenost = sqrt((centroid.suradnice[0] - bod[0]) ** 2 + (centroid.suradnice[1] - bod[1]) ** 2)

                if vzdialenost < min_vzdialenost:
                    min_vzdialenost = vzdialenost
                    min_centroid = centroid

            min_centroid.list_bodov.append(bod)
            min_centroid.sum_x_suradnic += bod[0]
            min_centroid.sum_y_suradnic += bod[1]
            min_centroid.avg_vzdialenost += min_vzdialenost

        if (centroids_pocet != 2) & zobrazenie_grafov:
            vykreslenie_grafu_centroid(list_of_centroids,"K-means centroid")

        list_suradnic.clear()
        najhorsi_priemer = 0
        priemer_priemerov = 0
                                                                # nove_suradnice centroidov
        for centroid in list_of_centroids:
            stare_suradnice = centroid.suradnice
            if len(centroid.list_bodov) != 0:
                centroid.suradnice = [int(centroid.sum_x_suradnic/len(centroid.list_bodov)), int(centroid.sum_y_suradnic/len(centroid.list_bodov))]
                centroid.avg_vzdialenost = centroid.avg_vzdialenost/len(centroid.list_bodov)
            else:
                continue

            list_suradnic.append(centroid.suradnice)
            posun_velkost = sqrt((stare_suradnice[0] - centroid.suradnice[0])**2 + (stare_suradnice[1] - centroid.suradnice[1])**2)
            priemer_priemerov += centroid.avg_vzdialenost

            if posun_velkost > max_posun_velkost:
                max_posun_velkost = posun_velkost
            if najhorsi_priemer < centroid.avg_vzdialenost:
                najhorsi_priemer = centroid.avg_vzdialenost

    end = timeit.default_timer()
    if centroids_pocet != 2:
        vykreslenie_grafu_centroid(list_of_centroids, "K-means centroid")
        end = timeit.default_timer()

        global list_kmeans_centroid
        list_kmeans_centroid[0] += round(end - start, 4)    # cas
        list_kmeans_centroid[1] += round(priemer_priemerov/centroids_pocet,2)    # avg
        list_kmeans_centroid[2] += round(najhorsi_priemer,2)    #worst
        print("K-means centroid\n------------")
        print("Priemer priemerných vzdialeností bodov od stredov klastrov: ",round(priemer_priemerov/centroids_pocet,2))
        print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ", round(najhorsi_priemer,2))

        print(round(end - start, 4), "sekund\n")
    return list_of_centroids


def k_means_medoid(list_vsetky_body):
    list_of_medoids = []
    list_suradnic = []
    max_posun_velkost = centroids_pocet
    pocet_iteracii = 0

    start = timeit.default_timer()

    while len(list_of_medoids) < centroids_pocet:                             # zvolenie nahodnych medoidov
        medoid_suradnice = list_vsetky_body[random.randint(0,len(list_vsetky_body) -1)]

        if medoid_suradnice not in list_suradnic:                           # kontrola duplikatov
            medoid = Klaster()
            medoid.suradnice = [medoid_suradnice[0], medoid_suradnice[1]]
            medoid.list_bodov = []
            list_of_medoids.append(medoid)
            list_suradnic.append(medoid_suradnice)

    if zobrazenie_grafov:
        vykreslenie_grafu(list_vsetky_body,list_suradnic)

    while (max_posun_velkost > 3) & (pocet_iteracii < 15):
        max_posun_velkost = 0
        pocet_iteracii += 1


        for medoid in list_of_medoids:          # vynulovanie bodov patriacich medoidu
            medoid.list_bodov = []

        for bod in list_vsetky_body:                            # zaradenie vsetkych bodov
            min_vzdialenost = 15000
            min_medoid = None

            for medoid in list_of_medoids:                  # najdenie najbližsieho medoidu
                vzdialenost = sqrt((medoid.suradnice[0] - bod[0]) ** 2 + (medoid.suradnice[1] - bod[1]) ** 2)

                if (vzdialenost < min_vzdialenost):    # hladanie minima
                    min_vzdialenost = vzdialenost
                    min_medoid = medoid

            min_medoid.list_bodov.append(bod)

        list_suradnic.clear()
        najhorsi_priemer = 0
        priemer_priemerov = 0

        if zobrazenie_grafov:
            vykreslenie_grafu_centroid(list_of_medoids, "K-means medoid")

        for medoid in list_of_medoids:                  # prejdenie vsetkych medoidov

            if len(medoid.list_bodov) > 0:
                nove_suradnice, avg_vzdialenost = najdenie_medoidu(medoid)
                stare_suradnice = medoid.suradnice
                medoid.suradnice = [nove_suradnice[0],nove_suradnice[1]]
                priemer_priemerov += avg_vzdialenost

                if avg_vzdialenost > najhorsi_priemer:
                    najhorsi_priemer = avg_vzdialenost

            list_suradnic.append(medoid.suradnice)  # list novych suradnic medoidov
            if sqrt((stare_suradnice[0] - medoid.suradnice[0]) ** 2 + (stare_suradnice[1] - medoid.suradnice[1]) ** 2) > 25:
                max_posun_velkost += 1

    vykreslenie_grafu_centroid(list_of_medoids, "K-means medoid")
    end = timeit.default_timer()
    print("K-means medoid\n------------")
    print("Priemer priemerných vzdialeností bodov od stredov klastrov: ",round(priemer_priemerov/centroids_pocet,2))
    print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ",round(najhorsi_priemer,2))
    print(round(end - start, 4), "sekund\n")

    global list_kmeans_medoid
    list_kmeans_medoid[0] += round(end - start, 4)  # cas
    list_kmeans_medoid[1] += round(priemer_priemerov / centroids_pocet, 2)  # avg
    list_kmeans_medoid[2] += round(najhorsi_priemer, 2)  # worst


def aglomerative_clustering(list_vsetky_body):

    list_klastrov = []
    matica_vzdialenosti = []

    # premenne pre vypis
    priem_vzdialenost = 0
    najhorsi_priemer = 0
    priemer_priemerov = 0

    start = timeit.default_timer()

    for bod in list_vsetky_body:        # vytvorenie nových klastrov pre každý bod
        novy_klaster = Klaster()
        novy_klaster.suradnice = bod
        novy_klaster.list_bodov = [bod]
        list_klastrov.append(novy_klaster)

        # 2D matica vzdialenosti - vytvorenie
    for i in range(len(list_vsetky_body)):
        n_riadok = []
        for j in range(0,i):
                                    # výpočet vzdialeností medzi jednotlivými bodmi
            vzdialenost = round(sqrt((list_vsetky_body[i][0] - list_vsetky_body[j][0]) ** 2 + (list_vsetky_body[i][1] - list_vsetky_body[j][1]) ** 2),3)
            n_riadok.append(vzdialenost)

        matica_vzdialenosti.append(n_riadok)

    vykreslenie_dendogramu(list_klastrov)

    while len(list_klastrov) != 1:

        min_vzdialenost_best = float("inf")
        index_stlpec = -1
        index_riadok = -1

            # najdenie min.vzdialenosti
        for i in range(len(matica_vzdialenosti)):
            if not matica_vzdialenosti[i]:                              # dany riadok je prazdny
                continue

            min_vzdialenost_n = min(matica_vzdialenosti[i])
            if min_vzdialenost_n < min_vzdialenost_best:
                min_vzdialenost_best = min_vzdialenost_n
                index_riadok = i

        index_stlpec = matica_vzdialenosti[index_riadok].index(min_vzdialenost_best)

        # if len(list_klastrov) == 200:           # vykreslenie dendogramu
        #     vykreslenie_dendogramu(list_klastrov)
        #     if len(list_klastrov) == 21:
        #         print(min_vzdialenost_best)

            # vypocet noveho centroidu zluceneho klastra
        klaster_1 = list_klastrov[index_riadok]
        klaster_2 = list_klastrov[index_stlpec]
        len_1 = len(klaster_1.list_bodov)
        len_2 = len(klaster_2.list_bodov)
        suradnica_x = int((klaster_1.suradnice[0]*len_1 + klaster_2.suradnice[0]*len_2)/(len_2+len_1))
        suradnica_y = int((klaster_1.suradnice[1]*len_1 + klaster_2.suradnice[1]*len_2)/(len_2+len_1))
        suradnice_novy_klaster = [suradnica_x,suradnica_y]


            # zlucenie klastrov
        klaster_1.suradnice = suradnice_novy_klaster
        klaster_1.list_bodov += klaster_2.list_bodov

            # odstranenie zlucneho klastra
        matica_vzdialenosti.pop(index_stlpec)               # vymazanie riadku
        for i in range(index_stlpec,len(matica_vzdialenosti)):      # vymazanie stlpca
            matica_vzdialenosti[i].pop(index_stlpec)
        list_klastrov.pop(index_stlpec)                     # vybratie z listu klastrov

        # aktualizacia matice vzdialenosti - riadok
        for i in range(index_riadok-1):
            vzdialenost = round(sqrt((list_klastrov[i].suradnice[0] - klaster_1.suradnice[0]) ** 2 + (list_klastrov[i].suradnice[1] - klaster_1.suradnice[1]) ** 2),3)
            matica_vzdialenosti[index_riadok-1][i] = vzdialenost

        # aktualizacia matice vzdialenosti stlpec
        for i in range(index_riadok ,len(matica_vzdialenosti)):
            vzdialenost = round(sqrt((list_klastrov[i].suradnice[0] - klaster_1.suradnice[0]) ** 2 + (list_klastrov[i].suradnice[1] - klaster_1.suradnice[1]) ** 2),3)
            matica_vzdialenosti[i][index_riadok - 1] = vzdialenost

        # print("\nopakovanie: ",pocet_bodov-(len(list_klastrov)))
        # print(len(matica_vzdialenosti))

        if len(list_klastrov) == centroids_pocet:
            # return list_klastrov
            if zobrazenie_grafov:
                vykreslenie_dendogramu(list_klastrov)
            vykreslenie_grafu_centroid(list_klastrov,"Aglomeratívne zhlukovanie")

        if len(list_klastrov) == centroids_pocet:               # vypocet priemernej a najhorsej vzdialenosti pre dany pocet klastrov
            vykreslenie_dendogramu(list_klastrov)

            for klaster in list_klastrov:
                for bod in klaster.list_bodov:
                    priem_vzdialenost += sqrt((bod[0] - klaster.suradnice[0])**2 + (bod[1] - klaster.suradnice[1])**2)
                priem_vzdialenost = priem_vzdialenost/len(klaster.list_bodov)
                priemer_priemerov += priem_vzdialenost
                if priem_vzdialenost > najhorsi_priemer:
                    najhorsi_priemer = priem_vzdialenost

    end = timeit.default_timer()
    print("Aglomerativne zhlukovanie\n------------")
    print("Priemer priemerných vzdialeností bodov od stredov klastrov: ", round(priemer_priemerov / centroids_pocet, 2))
    print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ", round(najhorsi_priemer, 2))
    print(round(end - start, 4), "sekund\n")

    global list_aglomerative_clustering
    list_aglomerative_clustering[0] += round(end - start, 4)  # cas
    list_aglomerative_clustering[1] += round(priemer_priemerov / centroids_pocet, 2)  # avg
    list_aglomerative_clustering[2] += round(najhorsi_priemer, 2)  # worst


def divisive_clustering(list_vsetky_body):
    global centroids_pocet
    pocet_iteracii = centroids_pocet
    centroids_pocet = 2
    priemer_priemerov =0

    sorted_list_of_centroids = []
    list_of_clusters = []

    # ulozenie vsetkych stavov, cize 2-20 klastrov
    akt_rozlozenie = None
    predch_rozlozenie = None

    aktualny_subset = list_vsetky_body
    print("Divizne zhlukovanie\n------------")
    start = timeit.default_timer()

    for i in range(1,pocet_iteracii):                                   # vytvorenie klastrov
        list_of_centroids = None

        while list_of_centroids is None:                    # zabezpečenie správneho zvolenia centroidov, aby rozdelili
            list_of_centroids = k_means_centroid(aktualny_subset)

        sorted_list_of_centroids.append(list_of_centroids[0])
        sorted_list_of_centroids.append(list_of_centroids[1])
        list_of_clusters.append(list_of_centroids[0])
        list_of_clusters.append(list_of_centroids[1])

        sorted_list_of_centroids.sort(key=lambda centroid: centroid.avg_vzdialenost)
        aktualny_subset = []
        aktualny_centroid = None

        while len(aktualny_subset) == 0:    # vybratie centroidu s najvecsou priemernou vzdialenostou
            aktualny_centroid = sorted_list_of_centroids.pop()
            aktualny_subset = aktualny_centroid.list_bodov
            if len(sorted_list_of_centroids) == 0:          # cely list vybrany
                break

        # pridanie akt. stavu do spajan.listu
        akt_rozlozenie = Divisive_rozlozenie()
        akt_rozlozenie.list_klastrov = []
        for x in list_of_clusters:
            akt_rozlozenie.list_klastrov.append(x)
        akt_rozlozenie.predch_rozlozenie = predch_rozlozenie
        predch_rozlozenie = akt_rozlozenie

        # print("najhorsie priemerna vzdialenost od centroidu pre ", round(len(list_of_clusters),2) ," klastrov: ",aktualny_centroid.avg_vzdialenost)
        # print("priemerna priemerna vzdialenost: ",)
        if i == (pocet_iteracii - 1) :
            vykreslenie_grafu_centroid(list_of_clusters, "Divízne zhlukovanie ")
        elif zobrazenie_grafov:
            vykreslenie_grafu_centroid(list_of_clusters, "Divízne zhlukovanie ")

        list_of_clusters.remove(aktualny_centroid)

    end = timeit.default_timer()
    akt_rozlozenie.list_klastrov.sort(key=lambda centroid: centroid.avg_vzdialenost)
    for i in akt_rozlozenie.list_klastrov:
        priemer_priemerov += i.avg_vzdialenost

    print("Priemer priemerných vzdialeností bodov od stredov klastrov: ",
              round(priemer_priemerov / (len(list_of_clusters) + 1), 2))
    print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ",round(akt_rozlozenie.list_klastrov[-1].avg_vzdialenost,2))
    print(round(end - start, 4), "sekund\n")

    global list_divisive_clustering
    list_divisive_clustering[0] += round(end - start, 4)  # cas
    list_divisive_clustering[1] += round(priemer_priemerov/(len(list_of_clusters)+1),2)  # avg
    list_divisive_clustering[2] += round(akt_rozlozenie.list_klastrov[-1].avg_vzdialenost,2)  # worst

    centroids_pocet = pocet_iteracii        # vrátenie glob prem. do povodneho stavu


def vykreslenie_grafu(list_vsetky_body,list_suradnic):


    plot.scatter([x[0] for x in list_vsetky_body], [x[1] for x in list_vsetky_body], marker='o',label="body")
    plot.scatter([x[0] for x in list_suradnic], [x[1] for x in list_suradnic], marker='o',color="black",
                 label="centroidy",
                 s=50)
    plot.xlabel('x-ova suradnica')
    plot.ylabel('y-ova suradnica')
    plot.title("body")
    plot.show()


def vykreslenie_grafu_centroid(list_of_centroids,typ_algoritmu):

    global cislo_grafu
    list_suradnic_centroidov = []
    list_centroidov_pozadie = []

    for centroid in list_of_centroids:              # list suradnic centroidov
        list_suradnic_centroidov.append(centroid.suradnice)
        centroid_pozadie = Klaster()
        centroid_pozadie.suradnice = centroid.suradnice
        centroid_pozadie.list_bodov = []
        list_centroidov_pozadie.append(centroid_pozadie)


    for bod in list_cely_graf:                      # rozdelenie  vsetkych bodov(zafarbenie pozadia)
        min_vzdialenost = 15000
        min_centroid = None

        for centroid in list_centroidov_pozadie:    # rozdelenie bodov
            vzdialenost = sqrt((centroid.suradnice[0] - bod[0]) ** 2 + (centroid.suradnice[1] - bod[1]) ** 2)
            vzdialenost = round(vzdialenost, 4)

            if (vzdialenost < min_vzdialenost) & (vzdialenost != 0):
                min_vzdialenost = vzdialenost
                min_centroid = centroid

        min_centroid.list_bodov.append(bod)

    plot.scatter([-5000,5000],[-5000,5000], color="white")

    for i in range(len(list_of_centroids)):                          # vykreslenie pozadia rozdeleneho
        list = list_centroidov_pozadie[i].list_bodov
        plot.scatter([x[0] for x in list], [x[1] for x in list], color=colors[i], marker='o',label="body",)

    for i in range(len(list_of_centroids)):                         # vykreslenie bodov

        # if typ_algoritmu == "K-means medoid":
        #     list = list_of_centroids[i].dict_bodov.keys()
        # else:
        list = list_of_centroids[i].list_bodov
        plot.scatter([x[0] for x in list], [x[1] for x in list], color=colors[i], marker='o',label="body",edgecolors="black")

    plot.scatter([x[0] for x in list_suradnic_centroidov], [x[1] for x in list_suradnic_centroidov],
                 c=colors[:len(list_suradnic_centroidov)], marker='o', label="centroidy",
                 s=140,edgecolors="black",linewidths=2,alpha=0.8)

    plot.xlabel('x-ova suradnica')
    plot.ylabel('y-ova suradnica')
    plot.title(typ_algoritmu)
    plot.xlim([-5000, 5000])
    plot.ylim([-5000, 5000])
    # plot.savefig("D:/stuff/plots/testplot_" + str(cislo_grafu) +".png")
    cislo_grafu += 1
    plot.show()


def vykreslenie_dendogramu(data):

    # vykreslenie_grafu_centroid(data,"aa")
    list = []
    for i in data:
        list.append(i.suradnice)

    plt.title('Aglomeratívne zhlukovanie')
    Z = linkage(list)
    plt.xlabel('index v poli')
    plt.ylabel('vzdialenosť')
    dendrogram(Z, leaf_rotation=90)
    plt.show()


def tester():
    pocet_opakovani = 5
    list_poctu_klastrov = [5,10,15,20]
    global centroids_pocet
    global zobrazenie_grafov
    zobrazenie_grafov = False

    global list_kmeans_centroid
    global list_kmeans_medoid
    global list_divisive_clustering
    global list_aglomerative_clustering

    for j in range(4):
        centroids_pocet = list_poctu_klastrov[j]

        for i in range(pocet_opakovani):
            k_means_centroid(list_vsetky_body)
            k_means_medoid(list_vsetky_body)
            divisive_clustering(list_vsetky_body)
            aglomerative_clustering(list_vsetky_body)

        print("Sumár po opakovaných meraniach pre ", list_poctu_klastrov[j] ," klastrov\n--------------\n")
        print("K-means centroid\n------------")
        print("Priemer priemerných vzdialeností bodov od stredov klastrov: ", round(list_kmeans_centroid[1]/pocet_opakovani, 2))
        print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ", round(list_kmeans_centroid[2]/pocet_opakovani, 2))
        print(round(list_kmeans_centroid[0]/pocet_opakovani, 4), "sekund\n")

        print("K-means medoid\n------------")
        print("Priemer priemerných vzdialeností bodov od stredov klastrov: ",round(list_kmeans_medoid[1]/pocet_opakovani,2))
        print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ",round(list_kmeans_medoid[2]/pocet_opakovani,2))
        print(round(list_kmeans_medoid[0]/pocet_opakovani, 4), "sekund\n")

        print("Aglomerativne zhlukovanie\n------------")
        print("Priemer priemerných vzdialeností bodov od stredov klastrov: ", round(list_aglomerative_clustering[1]/pocet_opakovani, 2))
        print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ", round(list_aglomerative_clustering[2]/pocet_opakovani, 2))
        print(round(list_aglomerative_clustering[0]/pocet_opakovani, 4), "sekund\n")

        print("Divizne zhlukovanie\n------------")
        print("Priemer priemerných vzdialeností bodov od stredov klastrov: ", round(list_divisive_clustering[1]/pocet_opakovani, 2))
        print("Najhoršia priemerná vzdialenosť bodov od stredov klastrov: ",
              round(list_divisive_clustering[2]/pocet_opakovani, 2))
        print(round(list_divisive_clustering[0]/pocet_opakovani, 4), "sekund\n")

        list_kmeans_centroid = [0, 0, 0]
        list_kmeans_medoid = [0, 0, 0]
        list_divisive_clustering = [0, 0, 0]
        list_aglomerative_clustering = [0, 0, 0]

    zobrazenie_grafov = True


if __name__ == '__main__':
    if not colors:
        nacitanie_farieb()
    list_vsetky_body = generator_continue(generator_start())
    graf_vsetky_body()

    k_means_centroid(list_vsetky_body)
    k_means_medoid(list_vsetky_body)
    divisive_clustering(list_vsetky_body)

    aglomerative_clustering(list_vsetky_body)
    # tester()



