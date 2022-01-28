import os
import sys
from scapy.all import rdpcap

protocols = {
       "#Ethertypes": {},
       "#LSAPs": {},
       "#IP Protocol": {},
       "#TCP ports": {},
       "#UDP ports": {}
    }

icmp_types_dict = {}
icmp_codes_dict = {
    "03": {},
    "05": {},
    "0A": {},
    "0B": {}
}


class ARPFrame(object):
    frame_num = None
    bytes_captured = None
    bytes_on_wire = None
    f_type = None
    MAC_S = None
    MAC_D = None
    ether_type = None
    source_ip = None
    dest_ip = None
    ARP_operation = None
    port_nazov = None

    def vypis(self):
        print("rámec {0}".format(self.frame_num))
        print("dĺžka rámca poskytnutá pcap API: {} B".format(self.bytes_captured))
        print("dĺžka rámca prenášaného po médiu: {} B".format(self.bytes_on_wire))
        print(self.f_type)
        print("Zdrojová MAC adresa:{0}\nCieľová MAC adresa:{1}".format(self.MAC_S, self.MAC_D))
        print(self.ether_type)

        if self.ARP_operation == 1:
            print("Request")
        elif self.ARP_operation == 2:
            print("Reply")

    def vypis_subor(self):
        print("rámec {0}".format(self.frame_num),file=output_file)
        print("dĺžka rámca poskytnutá pcap API: {} B".format(self.bytes_captured),file=output_file)
        print("dĺžka rámca prenášaného po médiu: {} B".format(self.bytes_on_wire),file=output_file)
        print(self.f_type,file=output_file)
        print("Zdrojová MAC adresa:{0}\nCieľová MAC adresa:{1}".format(self.MAC_S, self.MAC_D),file=output_file)
        print(self.ether_type,file=output_file)

        if self.ARP_operation == 1:
            print("Request",file=output_file)
        elif self.ARP_operation == 2:
            print("Reply",file=output_file)


class Frame(ARPFrame):                                        # trieda predstavujuca jeden ramec
    source_port = None
    dest_port = None
    ipv4_prtkl = None
    port_nazov = None
    type = None
    code = None
    flags = None

    def vypis(self):
        print("rámec {0}".format(self.frame_num))
        print("dĺžka rámca poskytnutá pcap API: {} B".format(self.bytes_captured))
        print("dĺžka rámca prenášaného po médiu: {} B".format(self.bytes_on_wire))
        print(self.f_type)
        print("Zdrojová MAC adresa:{0}\nCieľová MAC adresa:{1}".format(self.MAC_S, self.MAC_D))

        if self.ether_type is not None:
            print(self.ether_type)
        if self.ipv4_prtkl is not None:
            print("zdrojová IP adresa:" + self.source_ip)
            print("cieľová IP adresa:" + self.dest_ip)
            print(self.ipv4_prtkl)
        if self.port_nazov is not None:
            print(self.port_nazov)
            print("zdrojový port: {}".format(self.source_port))
            print("cieľový port: {}".format(self.dest_port))
        if self.ARP_operation is not None:
            if self.ARP_operation == 1:
                print("Request")
            elif self.ARP_operation == 2:
                print("Reply")
        if self.type is not None:
            for type_dict in icmp_types_dict.keys():
                if type_dict == self.type:
                    print(icmp_types_dict.get(self.type))
                    if (self.type == "03") | (self.type == "05") | (self.type == "0A") | (self.type == "0B"):
                        print(icmp_codes_dict[self.type].get(self.code))

    def vypis_subor(self):
        print("rámec {0}".format(self.frame_num),file=output_file)
        print("dĺžka rámca poskytnutá pcap API: {} B".format(self.bytes_captured),file=output_file)
        print("dĺžka rámca prenášaného po médiu: {} B".format(self.bytes_on_wire),file=output_file)
        print(self.f_type,file=output_file)
        print("Zdrojová MAC adresa:{0}\nCieľová MAC adresa:{1}".format(self.MAC_S, self.MAC_D),file=output_file)

        if self.ether_type is not None:
            print(self.ether_type,file=output_file)
        if self.ipv4_prtkl is not None:
            print("zdrojová IP adresa:" + self.source_ip,file=output_file)
            print("cieľová IP adresa:" + self.dest_ip,file=output_file)
            print(self.ipv4_prtkl,file=output_file)
        if self.port_nazov is not None:
            print(self.port_nazov,file=output_file)
            print("zdrojový port: {}".format(self.source_port),file=output_file)
            print("cieľový port: {}".format(self.dest_port),file=output_file)
        if self.ARP_operation is not None:
            if self.ARP_operation == 1:
                print("Request",file=output_file)
            elif self.ARP_operation == 2:
                print("Reply",file=output_file)
        if self.type is not None:
            for type_dict in icmp_types_dict.keys():
                if type_dict == self.type:
                    print(icmp_types_dict.get(self.type),file=output_file)
                    if (self.type == "03") | (self.type == "05") | (self.type == "0A") | (self.type == "0B"):
                        print(icmp_codes_dict[self.type].get(self.code),file=output_file)


def print_hexdump(array):           # funkcia na vypis ramca v hexadecimalnom tvare

    array = bytes(array)
    array = bytearray(array)
    array = array.hex().upper()

    for i in range(1, len(array)+1):
        print(array[i-1], end='')
        if i % 32 == 0:
            print(end='\n')
            continue
        if i % 16 == 0:
            print('  ', end='')
            continue
        if i % 2 == 0:
            print(' ', end='')
    print("\n", end="\n")


def print_hexdump_file(array):           # funkcia na vypis ramca v hexadecimalnom tvare

    array = bytes(array)
    array = bytearray(array)
    array = array.hex().upper()

    for i in range(1, len(array)+1):
        print(array[i-1], end='',file=output_file)
        if i % 32 == 0:
            print(end='\n',file=output_file)
            continue
        if i % 16 == 0:
            print('  ', end='',file=output_file)
            continue
        if i % 2 == 0:
            print(' ', end='',file=output_file)
    print("\n", end="\n",file=output_file)


def arp_comm_analysis(list_of_frames):                  #analýza a výpis arp komunikácii
    index = 0
    reply_without_request = []

    if len(list_of_frames) == 0:
        print("ARP komunikácia nenájdená")

    for reply in list_of_frames[1]:                                 # prejdenie vsetkych reply
        index += 1
        request_to_remove = []

        for request in list_of_frames[0]:                                       # prejdenie vstekych request
            if(request.dest_ip == reply.source_ip) & (request.source_ip == reply.dest_ip) & (reply.frame_num > request.frame_num):                              # najdenie dvojice
                request_to_remove.append(request)

        if len(request_to_remove) > 0:                                          # nájdená dvojica

            print("*******************\n* Komunikácia č.{} *\n*******************\n".format(index))
            print("ARP-request, IP adresa: {0}, MAC adresa: ???".format(request_to_remove[0].source_ip))
            print("Zdrojová IP: {0}, Cieľová IP: {1}".format(request_to_remove[0].source_ip, request_to_remove[0].dest_ip))

            for request in request_to_remove:                               #výpis všetkých request ramcov pre daný reply
                request.vypis()
                print_hexdump(file_reader[request.frame_num - 1])
                list_of_frames[0].remove(request)

            print("ARP-reply, IP adresa: {0}, MAC adresa: {1}".format(reply.source_ip, reply.MAC_S))
            print("Zdrojová IP: {0}, Cieľová IP: {1}".format(reply.source_ip, reply.dest_ip))
            reply.vypis()
            print_hexdump(file_reader[reply.frame_num - 1])

        else:
            reply_without_request.append(reply)                                 # nájdenie reply bez request

    if len(reply_without_request) > 0:                                      # výpis všetkých reply bez request
        print("\nARP-reply bez ARP-request: ")
        for reply in reply_without_request:
            reply.vypis()
            print_hexdump(file_reader[reply.frame_num - 1])

    if len(list_of_frames[0]) > 0:                                       # výpis všetkých request bez príslušného reply
        print("\nARP-request bez ARP-reply: ")
    for request in list_of_frames[0]:
        print("ARP-request, IP adresa: {0}, MAC adresa: ???".format(request.source_ip))
        print("Zdrojová IP: {0}, Cieľová IP: {1}".format(request.source_ip, request.dest_ip))
        request.vypis()
        print_hexdump(file_reader[request.frame_num - 1])


def icmp_comm_analysis(list_of_frames):         # analýza a výpis icmp komunikácii
    list_of_communication = []
    cislo_komunikacie = 0

    if len(list_of_frames) == 0:
        print("ICMP komunikácia nenájdená")

    while len(list_of_frames):                      #cyklus na prejdenie všetkých rámcov v liste
        frame_first = list_of_frames[0]
        ip = []
        ip.append(frame_first.dest_ip)
        ip.append(frame_first.source_ip)

        for frame in list_of_frames:                            # nájdenie rámcov patriacich do jednej komunikácie
            if (frame.dest_ip in ip) & (frame.source_ip in ip):
                list_of_communication.append(frame)

        cislo_komunikacie += 1
        print("*******************\n* Komunikácia č.{} *\n*******************\n".format(cislo_komunikacie), end='')
        print_comm(list_of_communication)

        for frame in list_of_communication:                     # vymazanie už vypísaných prvkov z listu
            list_of_frames.remove(frame)

        list_of_communication = []


def tftp_comm_analysis(list_of_frames):                 # výpis TFTP komunikácii

    for i in range(len(list_of_frames)):
        print("*******************\n* Komunikácia č.{} *\n*******************\n".format(i+1), end='')
        print_comm(list_of_frames[i])

    if len(list_of_frames) == 0:
        print("TFTP komunikácia nenájdená")


def tcp_type_of_comm(list_of_communication):                # rozhodne ci ide o kompletnu alebo nekompletnu komunikaciu

    if len(list_of_communication) > 3:
        four_last = int(list_of_communication[-4].flags, 16)            # ulozenie hodnot flagov poslednych 4 ramcov komunikacie do int, kvoli dalsiemu porovnavaniu
        three_last = int(list_of_communication[-3].flags, 16)
        two_last = int(list_of_communication[-2].flags, 16)
        one_last = int(list_of_communication[-1].flags, 16)

        if (one_last & 4 == 4) | (two_last & 4 == 4):                       # ukoncenie resetom
            return 1
        elif (three_last & 1 == 1) & (two_last & 1 == 1) & (one_last & 16 == 16):       # ukoncenie pomocou >fin <fin,ack >ack
            return 1
        elif (three_last & 16 == 16) & (one_last & 16 == 16):
            if ((four_last & 1 == 1) & (two_last & 1 == 1)) | ((four_last & 17 == 17) & (two_last & 17 == 17)):             # ukoncenie >fin,(ack) <ack <fin,(ack) >ack
                return 1
            else:
                return 0
        else:
            return 0

    elif not list_of_communication:
        return -1
    else:
        return -2


def tcp_comm_analysis(list_of_frames):                      # najdenie a vypis prvej kompletnej a nekompletnej komunikacie

    list_of_communication = tcp_start_comm_analysis(list_of_frames)            # list jednej komunikacie
    counter = 0

    complete_com = tcp_type_of_comm(list_of_communication)
    if(complete_com == -1):                                             # nenajdena ziadna komunikacia
        print("Nenajdená komunikácia")

    elif complete_com == 0:                                             # nájdena nekompletná komunikácia
        print("*************************\n*Nekompletná komunikácia*\n*************************")
        print_comm(list_of_communication)

        while (complete_com != 1) & (complete_com != -1):               # hladanie kompletnej komunikacie
            list_of_communication = tcp_start_comm_analysis(list_of_frames[list_of_communication[0].frame_num:])
            complete_com = tcp_type_of_comm(list_of_communication)
        if complete_com == 1:
            print("***********************\n*Kompletná komunikácia*\n***********************")
            print_comm(list_of_communication)
            print("Bola najdená aj kompletná aj nekompletná komunikácia")
        else:
            print("Kompletná komunikácia nenájdená")

    elif complete_com == 1:                                                 # najdenie kompletnej komunikacie
        print("***********************\n*Kompletná komunikácia*\n***********************")
        print_comm(list_of_communication)

        while (complete_com != 0) & (complete_com != -1):                   # hladanie nekompletnej komunikacie
            list_of_communication = tcp_start_comm_analysis(list_of_frames[list_of_communication[0].frame_num:])
            complete_com = tcp_type_of_comm(list_of_communication)
        if complete_com == 0:
            print("*************************\n*Nekompletná komunikácia*\n*************************")
            print_comm(list_of_communication)
            print("\nBola najdená aj kompletná aj nekompletná komunikácia")
        else:
            print("\nNekompletná komunikácia nenájdená")


def print_comm(list_of_communication):              #  vypis komunikácie
    if len(list_of_communication) <= 20:
        for frame in list_of_communication:
            frame.vypis()
            print_hexdump(file_reader[frame.frame_num - 1])
    else:                                               # ak obsahuje viac ako 20 ramcov, vypise prvych a poslednych 10
        for frame in list_of_communication[:10]:
            frame.vypis()
            print_hexdump(file_reader[frame.frame_num - 1])
        print("\n\n.\n.\n.")
        for frame in list_of_communication[-10:]:
            frame.vypis()
            print_hexdump(file_reader[frame.frame_num - 1])


def tcp_start_comm_analysis(list_of_frames):
    switch = 0
    list_of_flags = [2, 18, 16]                         #int cisla ale reprezentujuce hex hodnotu
    list_of_communication = []
    ports = []
    IP = []
    for frame in list_of_frames:

        if (int(frame.flags, 16) & list_of_flags[0] == list_of_flags[0]) & (len(list_of_communication) == 0):       # porovnanie hodnot flagov cez bitove operacie
            switch += 1                                             # najdenie ramca so SYN flagom
            list_of_communication.append(frame)
            ports.append(frame.source_port)
            ports.append(frame.dest_port)
            IP.append(frame.source_ip)
            IP.append(frame.dest_ip)
            continue

        if (switch > 0) & (switch < 3):                             # najdenie dalsich ramcov s flagmi potrebnymi na otvorenie komunikacie
            if (int(frame.flags, 16) & list_of_flags[switch] == list_of_flags[switch]) & (len(list_of_communication) != 0) & ((frame.dest_port in ports) & (frame.source_port in ports)) & (frame.dest_ip in IP) & (frame.source_ip in IP):
                switch += 1
                list_of_communication.append(frame)

                continue

        if switch == 3:                                             # pridavanie dalsich ramcov do komunikacie
            if (switch == 3) & (frame.dest_port in ports) & (frame.source_port in ports) & (frame.dest_ip in IP) & (frame.source_ip in IP):
                if int(frame.flags, 16) & list_of_flags[0] == list_of_flags[0]:
                    return list_of_communication
                list_of_communication.append(frame)

    return list_of_communication


def pcap_analysis(file_reader, filter):

    frame_num = 0                                   # cislo ramca
    list_of_frames = []                            # list ulozenych ramcov

    if filter is None:
        ip_adresses_dict = {}                           #dict na ulozenie jedinecnych ip adries
        max_ip_adress = []                              # list na ulozenie ip adries s najvecsim poctom odoslanych paketov
        max_value = 0

    if filter == "TFTP":
        destination_port = None
    list_tftp_comm = []
    source_port = 0

    if filter == "ARP":
        list_of_frames.append([])
        list_of_frames.append([])

    for row in file_reader:                         # cyklus na prejdenie vsetkych ramcov z nacitaneho pcap suboru
        frame_num += 1
        array = bytes(row)                          # prevod bytoveho pola na string
        array = bytearray(array)
        array = array.hex().upper()

        if filter == "ARP":
            frame = ARPFrame()
        else:
            frame = Frame()                             # vytvorenie objektu triedy

        frame.frame_num = frame_num
        frame_analysis(array, frame)                # analyza ramca

        if filter is not None:                      # v pripade nastavenia filtra(vykonania 4. ulohy sa potrebne ramce ulozia do listu)

            if (frame.port_nazov == filter) & (filter != "TFTP"):
                list_of_frames.append(frame)
            elif frame.ether_type == filter:
                list_of_frames[frame.ARP_operation-1].append(frame)

            elif (filter == "TFTP") & ((frame.port_nazov == filter) | (source_port in [frame.source_port, frame.dest_port])):

                if frame.port_nazov == filter:                                          # prvy ramec komunikacie

                    if source_port != 0:
                        list_of_frames.append(list_tftp_comm)                  # pridanie predch. komunikacie do
                        list_tftp_comm = []

                    list_tftp_comm.append(frame)
                    source_port = frame.source_port                            # nastavenie novej dvojice portov pre danu komunikaciu(dest. este nevieme urcit)
                    destination_port = None

                elif (source_port in [frame.source_port, frame.dest_port]):               # pokracujuci ramec komunikacie
                    if (list_tftp_comm[0].source_ip in [frame.source_ip, frame.dest_ip]) & (list_tftp_comm[0].dest_ip in [frame.source_ip, frame.dest_ip]):
                        list_tftp_comm.append(frame)
                        frame.port_nazov = "TFTP"

                    if destination_port is None:
                        destination_port = frame.source_port

            elif (filter == "ICMP") & (frame.ipv4_prtkl == filter):
                list_of_frames.append(frame)

        else:
            frame.vypis()
            print_hexdump(file_reader[frame.frame_num - 1])     # vypis hexadecim. hodnot
            frame.vypis_subor()
            print_hexdump_file(file_reader[frame.frame_num - 1])
            if frame.ether_type == "IPv4":                      # zistovanie a ukladnie jedinecnych IP adries
                if ip_adresses_dict.get(frame.source_ip) is not None:
                    ip_adresses_dict[frame.source_ip] += 1
                else:
                    ip_adresses_dict[frame.source_ip] = 1

    if filter is None:                                              # sumarny vypis jedinecnyh IP adres, a najvecsi pocet odoslanych paketov
        print("\n\nIP adresy vysielajúcich uzlov:\n---------------------")
        print("\n\nIP adresy vysielajúcich uzlov:\n---------------------", file=output_file)
        for key in ip_adresses_dict.keys():                             # cyklus na vypis ip adries
            print(key)
            print(key, file=output_file)

        for key, value in ip_adresses_dict.items():                     # najdenie IP adresy ktora odoslala najviac paketov
            if int(value) >= max_value:
                max_value = int(value)
                max_ip_adress.append(key)                               # pridavanie do listu v pripade ze z viac IP adries sa odoslal max. pocet paketov

        print("\nNajviac odoslaných paketov:\n------------------ ")
        print("\nNajviac odoslaných paketov:\n------------------ ", file=output_file)

        for adress in max_ip_adress:
            print(adress)
            print(adress, file=output_file)
        print("Počet : {}".format(max_value))
        print("Počet : {}".format(max_value), file=output_file)

    if list_tftp_comm:                                          # pridanie poslednej komunikacie do listu
        list_of_frames.append(list_tftp_comm)

    return list_of_frames


def frame_analysis(array, frame):                           #analyza jedneho ramca(linkova a sietova vrstva)

    length = array[24:28]                                       # dlzka nasledujuceho protokolu/ethertype
    l_total = int(length, 16)
    t_1 = array[28:30]                                          # dlzka vnoreneho ethernet protokolu

    frame.bytes_captured = int(len(array) / 2)                   # vypocet zachytench bajtov, po sieti
    frame.bytes_on_wire = 64 if frame.bytes_captured <= 60 else frame.bytes_captured + 4

    frame.MAC_D = ' '.join(array[i:i + 2] for i in range(0, 12, 2))
    frame.MAC_S = ' '.join(array[i:i + 2] for i in range(12, 24, 2))
    frame.ether_type = "nezistený"

    if len(protocols["#Ethertypes"]) == 0:                          # nacitanie protokolov, ak este niesu
        load_protocols()

    if l_total >= 1536:                                             # ide o ethernet
        frame.f_type = "Ethernet II"

        for key in protocols["#Ethertypes"].keys():                     # cyklus na najdenie spravneho ethertype
            if int(key, 16) == l_total:
                frame.ether_type = protocols["#Ethertypes"].get(key)
                break

    elif l_total <= 1500:                                           # ide o 802.3
        if t_1 == "AA":
            frame.f_type = "IEEE 802.3 LLC + SNAP"
            type_eth = array[40:44]

            for key in protocols["#Ethertypes"].keys():         # cyklus na najdenie spravneho ethertype
                if int(key, 16) == int(type_eth, 16):
                    frame.ether_type = protocols["#Ethertypes"].get(key)
                    break

        elif t_1 == "FF":
            frame.f_type = "Novell 802.3 RAW"
            frame.ether_type = "IPX"
        else:
            frame.f_type = "IEEE 802.3 LLC"
            for key in protocols["#LSAPs"].keys():          # cyklus na najdenie spravneho SAPu
                if int(key, 16) == int(t_1, 16):
                    frame.ether_type = protocols["#LSAPs"].get(key)

        return

    else:
        frame.f_type = "nezistený"
        frame.ether_type = "nezistený"

    if frame.ether_type == "IPv4":                          # dalsia analýza na vnorených vrstvách
        ipv4_analysis(array, frame)

    elif frame.ether_type == "ARP":                         # zistenie ARP operacie
        frame.ARP_operation = int(array[43])
        frame.source_ip = '.'.join(str(int(array[i:i + 2], 16)) for i in range(56, 64, 2))
        frame.dest_ip = '.'.join(str(int(array[i:i + 2], 16)) for i in range(76, 84, 2))


def ipv4_analysis(array, frame):                    # analyza ipv4 protokolu

    frame.source_ip = '.'.join(str(int(array[i:i + 2], 16)) for i in range(52, 60, 2))
    frame.dest_ip = '.'.join(str(int(array[i:i + 2], 16)) for i in range(60, 68, 2))


    vnoreny_protokol = array[46:48]
    for key in protocols["#IP Protocol"].keys():                # cyklus na najdenie spraveho vnoreneho protokolu od ipv4 zo zoznamu

        if key[2:] == vnoreny_protokol:
            offset = int(array[29]) * 4 * 2                     # posun za hlavicku daneho protokolu

            frame.ipv4_prtkl = protocols["#IP Protocol"].get(key)

            if (frame.ipv4_prtkl == "TCP") | (frame.ipv4_prtkl == "UDP"):
                frame.dest_port = int(array[32 + offset:36 + offset], 16)       # dest a src porty
                frame.source_port = int(array[28 + offset:32 + offset], 16)
                frame.port_nazov = "port nezistený"

                if frame.ipv4_prtkl == "TCP":
                    frame.flags = array[94:96]

                for port in protocols["#" + frame.ipv4_prtkl + " ports"].keys():    # cyklus na najdenie spravneho vnoreneho protokolu od TCP/UDP(transportnej vrstvy)
                    if int(port, 16) == (frame.dest_port if frame.dest_port < frame.source_port else frame.source_port):
                        frame.port_nazov = protocols["#" + frame.ipv4_prtkl + " ports"].get(port)
                        break

            elif frame.ipv4_prtkl == "ICMP":
                frame.type = array[28 + offset:30 + offset]     # typ a kod ICMP protokolu
                frame.code = array[30 + offset:32 + offset]


def choose_subprogram(file_reader):                     # vyber podprogramu
    program_choice = ''
    while (program_choice != '1') & (program_choice != '2') & (program_choice != 'q') & (program_choice != 'c'):      # cyklus, ktory zabezpeci spravne vybratie moznosti z ponuky
        print("\nVyber jednu z nasledujúcich možností:\n-------------------------------------")
        print("zobrazenie základného výpisu        -        stlač 1\nanalýza komunikácie pre konkrétny protokol - stlač 2")
        print("ukoncenie programu                  -        stlač q")

        program_choice = input("Stlač klavesu:")

        # file_path = 'randomfile.txt'
        # sys.stdout = open(file_path, "w")

    if program_choice == '1':
        pcap_analysis(file_reader, None)
    elif program_choice == '2':
        choose_subprogram_2(file_reader)
    elif program_choice == 'q':
        output_file.close()
        sys.exit()
    else:
        os.system("cls")


def choose_subprogram_2(file_reader):                   # vyber analyzy konkretnej komunikacie v 4.ulohe
    volba = ''
    tuple_choice = (('1', "HTTP"), ('2', "HTTPS"), ('3', "TELNET"), ('4', "SSH"), ('5', "FTP-CONTROL"), ('6', "FTP-DATA"), ('7', "TFTP"), ('8', "ICMP"), ('9', "ARP"))

    while (volba > '9') | (volba < '0'):                        # cyklus ktory zabezpeci spravne zvolenie moznosti z rozsahu

        print("\nVyber jednu z možností\n----------------------")
        print("HTTP   - '1'\nHTTPS  - '2'\nTELNET - '3'\nSSH    - '4'\nFTP riadiace -'5'\nFTP dátové -  '6'\nTFTP - '7'\nICMP - '8'\nARP  - '9'")
        print("ukončenie programu - '0'")
        volba = input("Zadaj hodnotu:")
        if volba == '0':
            output_file.close()
            sys.exit()
        if(volba <= '9') & (volba >= '1'):
            print("\n" + tuple_choice[int(volba)-1][1] + " komunikácie\n-------------------------------")
            list_of_frames = pcap_analysis(file_reader, tuple_choice[int(volba) - 1][1])    #naplnenie listu ramcov
            if volba <= '6':
                tcp_comm_analysis(list_of_frames)
            elif volba == '7':
                tftp_comm_analysis(list_of_frames)
            elif volba == '8':
                icmp_comm_analysis(list_of_frames)
            elif volba == '9':
                arp_comm_analysis(list_of_frames)
            break


def load_protocols():                                   # nacitanie protokolov z externeho .txt suboru
    protocols_path = "protokoly.txt"
    protocols_file = open(protocols_path, "r")
    name = "#Ethertypes"

    for current in protocols_file:                      # cyklus na citanie suboru po riadkoch
        if current[0] == "#":
            name = current[:len(current) - 1]           # nazov hlavičky bez znaku konca riadku
            continue

        blank_position = current.find(' ')              # hladanie medzery v riadku
        protocols[name][current[:blank_position]] = current[blank_position + 1:len(current) - 1]        # pridanie noveho prvku do dictionary, prva polka riadku(pred medzerou) bude kluc, a druha hodnota
    protocols_file.close()

    protocols_path = "ICMP.txt"
    protocols_file = open(protocols_path, "r")
    name = "ICMP types"

    for current in protocols_file:                      # cyklus na citanie suboru po riadkoch

        if current[0] == "#":
            name = current[1:len(current) - 1]           # nazov hlavičky bez znaku konca riadku
            continue

        if name == "ICMP types":
            icmp_types_dict[current[2:4]] = current[5:len(current) - 1]
        else:
            icmp_codes_dict[name][current[2:4]] = current[5:len(current) - 1]
    protocols_file.close()


def choose_file():

    file = input("Zadaj názov súboru, ktorý chceš analyzovať(napr.'trace-2.pcap'):")

    try:
        file_reader = rdpcap(file_name + file)

    except FileNotFoundError:                                   # osetrenie pripadu nenajdenia daneho suboru
        print("Subor nenajdený")
        sys.exit()                                                          # ukoncenie programu

    except PermissionError:
        print("Subor nenajdený")
        sys.exit()

    return file_reader


if __name__ == '__main__':
    file_name = "vzorky_pcap_na_analyzu/"
    output_file = open("1.uloha_vypis.txt", "w")                                    # externý subor
    print("-----------------------------------\n| Analyzátor sieťovej komunikácie |")
    print("| Autor : Tomáš Socha             |\n-----------------------------------\n")
    print("-----------------------------------\n| Analyzátor sieťovej komunikácie |", file=output_file)
    print("| Autor : Tomáš Socha             |\n-----------------------------------\n", file=output_file)
    file_reader = choose_file()                         #otvori zvoleny pcap subor
    while 1:
        choose_subprogram(file_reader)
