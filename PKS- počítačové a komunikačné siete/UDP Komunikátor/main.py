import os
import random
import socket
from struct import pack, unpack
from time import sleep
import threading
import binascii

FORMAT = "utf-8"

keep_alive_thread = None
keep_alive_status = False

server_pocuvanie_bg_status = False
server_bg_thread = None


class Communicator:
    socket = None           # koncovy bod
    dest_addr = None        # adresa ktorej posiela a od ktorej prijima spravy (ip,port)


# sekcia klient


def client_start(ip_adress, port):
    client = Communicator
    client.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.dest_addr = (ip_adress, int(port))  # port cez ktorý sa pripoji do serveru

    # client.socket.settimeout(60)
    kom_nadviazana = 0

    while True:                                     # nadviazanie spojenia
        client.socket.sendto(b"S", client.dest_addr)
        try:
            client.socket.settimeout(60)
            data, client.dest_addr = client.socket.recvfrom(1500)
            client.socket.settimeout(None)
            data = data.decode(FORMAT)
            if data == "A":
                print(f"\nKlient prihlaseny na server {client.dest_addr}")
                client_main(client)
            break
        except ConnectionResetError:                    # prijímač bol vypnutý
            if kom_nadviazana == 0:
                print("čakanie na spustenie prijímača....")
                kom_nadviazana = 1
            sleep(3)
        except TimeoutError:
            print("Prijímač nebol spustený, vypínanie!!")
            os._exit(0)


def client_main(client):
    global keep_alive_thread
    global keep_alive_status

    while True:
        fragment_size = -1
        if keep_alive_status is False:          # zapnutie keep-alive
            keep_alive_thread = threading.Thread(target=keep_alive, args=(client,),daemon=True)
            keep_alive_status = True
            keep_alive_thread.start()

        print("\nPonuka:\n----------------")                    # výpis ponuky
        print("Prenos dát  - p\nVýmena rolí - v\nUkončenie   - q\n----------------")
        volba = input("Vyber 1 možnosť: ")

        if keep_alive_thread is not None:
            keep_alive_status = False
            keep_alive_thread.join()

        if volba == 'p':
            # if keep_alive_thread is not None:
            #     keep_alive_status = False
            #     keep_alive_thread.join()

            client_prenos_dat(client)

        # if keep_alive_thread is not None:
        #     keep_alive_status = False
        #     keep_alive_thread.join()

        if volba == 'v':
            vymena_roli(client,"Server")
        elif volba == 'q':
            ukoncenie_programu(client)
        elif volba == 'c':
            client.socket.sendto(b'A', client.dest_addr)
            print("Roly uspešne vymenené")
            server_main(client)
            break
        elif volba == 'n':
            print("Odmietnute!!")
            client.socket.sendto(b'N', client.dest_addr)


def client_prenos_dat(client):
    global keep_alive_thread
    global keep_alive_status
    fragment_size = -1

    while True:
        print("\nZvoľ čo chceš prenášať:\n-------------\nSúbor  - f\nSprávu - m\n-------------")
        volba = input("zadaj: ")
                # vyber typu prenášaných dát
        if volba == 'f':
            print("Zvolený súbor")

            while True:             # korektné zadaná cesta k suboru
                absolutna_cesta = input("Zadaj názov súboru aj s jeho absolútnou cestou:")
                try:  # zle zadana cesta suboru
                    if absolutna_cesta == 'q':
                        exit(0)
                    data = nacitanie_suboru(absolutna_cesta)
                    break
                except FileNotFoundError:
                    print("Súbor nenájdený!!")

            file_name = absolutna_cesta[absolutna_cesta.rfind('\\') + 1:].encode()
            crc_value = binascii.crc_hqx(file_name, 0)
            flag = b'D'

        elif volba == 'm':
            print("zvolená správa")
            data = input("Napíš správu ktorú chceš odoslať:\n").encode()
            flag = b'M'

        else:
            print("Nesprávne zvolená možnosť!!!")
            continue

            # zadanie velkosti fragmentu
        while (fragment_size <= 0) | (fragment_size > 1466):
            try:
                fragment_size = int(input("Zadaj max. veľkosť fragmentu:"))
            except ValueError:
                print("Zadaj hodnotu z intervalu (0,1464>")
            if (fragment_size <= 0) | (fragment_size > 1466):
                print("Nesprávne zadaná veľkosť, prosím zadaj hodnotu z intervalu (0,1466>")

        simulacia_chyby = input("Chceš zapnúť simuláciu chyby? a/n:")
        simulacia_chyby = True if simulacia_chyby == 'a' else False

        # vytvorenie inf packetu
        num_of_fragments = int(len(data) / fragment_size) + 1
        num_of_fragments_bytes = num_of_fragments.to_bytes(3, "big")

        if volba == 'f':
            inf_packet = pack(f"c{3}sH{len(file_name)}s", flag, num_of_fragments_bytes, crc_value, file_name)
        else:
            inf_packet = pack(f"c{3}s", flag, num_of_fragments_bytes)

            # poslanie informacnej spravy o planovanom prenose
        while True:
            client.socket.sendto(inf_packet, client.dest_addr)
            try:
                client.socket.settimeout(25)
                response, source_addr = client.socket.recvfrom(1500)
                client.socket.settimeout(None)
                response = response.decode()
            except socket.timeout:
                print("Server nepočúva")
                # keep_alive_thread = threading.Thread(target=keep_alive, args=(client,))
                # keep_alive_status = True
                # keep_alive_thread.start()
                return

            if response == 'A':
                print("\n------------------------")
                if volba == 'f':
                    print("Prenášaný súbor: ",file_name.decode())
                    print("Absolútna cesta: ", absolutna_cesta)
                else:
                    print("Prenášanie správy")
                print("Počet fragmentov: ", num_of_fragments)
                print("Max. veľkosť fragmentu: ",fragment_size)
                print("------------------------")
                selective_arq_prenos(client, fragment_size, data, volba,simulacia_chyby)
                return
            elif response == 'N':
                print("Server zamietol prenos")
                return
            elif (response == 'M') | (response == 'D'):
                continue

        break


def selective_arq_prenos(client, fragment_size, data, volba, simulacia_chyby):
    list_of_fragments = [b'']
    sliding_window = []
    num_of_fragments = int(len(data) / fragment_size) + 1
    sliding_window_len = int(num_of_fragments / 4) if (num_of_fragments > 4) else 1
    bytearray = b''
    chybne_fragmenty_list = [b'']
    index_chybnych_fragmentov = 1

    for i in range(1, num_of_fragments + 1):  # rozdelenie dat do fragmentov
        if i == num_of_fragments:
            data_in_fragment = data[(num_of_fragments - 1) * fragment_size:]
        else:
            data_in_fragment = data[(i - 1) * fragment_size:i * fragment_size]

        fragment_num_bytes = i.to_bytes(3, "big")
        crc_value = binascii.crc_hqx(data_in_fragment, 0)
        fragment = pack(f"c{3}sH{len(data_in_fragment)}s", b'D', fragment_num_bytes, crc_value, data_in_fragment)
        list_of_fragments.append(fragment)

        if simulacia_chyby & (i < 20):        # simulacia chyby - vytvorenie chybnych fragmentov
            if i % 2 == 1:
                data_in_fragment = data_in_fragment[0:-1]
                fragment = pack(f"c{3}sH{len(data_in_fragment)}s", b'D', fragment_num_bytes, crc_value, data_in_fragment)
            chybne_fragmenty_list.append(fragment)

        if sliding_window_len >= i:  # naplnenie sliding window
            sliding_window.append(i)

    index_to_insert = len(sliding_window) + 1
    nack_list = []
    thread_pocuvanie_ack = threading.Thread(target=pocuvanie_ack_packetov, args=(client, sliding_window, nack_list),daemon=True)
    thread_pocuvanie_ack.start()

    for i in range(1, sliding_window_len + 1):
        if simulacia_chyby & (i < len(chybne_fragmenty_list)):          # simulacia chyby, poslanie zlych fragmentov
            if i != 2:
                client.socket.sendto(chybne_fragmenty_list[i], client.dest_addr)
            index_chybnych_fragmentov = i+1                             # ktory fragment ma byt dalsi poslany
        else:
            client.socket.sendto(list_of_fragments[i], client.dest_addr)


            # doplnanie sliding window
    while (len(sliding_window) != 0) | (index_to_insert != len(list_of_fragments)) | (len(nack_list) != 0):

        # if len(sliding_window) < sliding_window_len:                # nemusi byt

        while len(sliding_window) != sliding_window_len:
                                                            # znovuposlanie nack fragmentov
            if len(nack_list) != 0:
                akt_index = nack_list.pop(0)
                sliding_window.append(akt_index)
                client.socket.sendto(list_of_fragments[akt_index], client.dest_addr)

            elif index_to_insert != len(list_of_fragments):     # vlozenie dalsieho fragment do sliding window

                sliding_window.append(index_to_insert)

                if simulacia_chyby & (index_chybnych_fragmentov < len(chybne_fragmenty_list)):  # simulacia chyby
                    client.socket.sendto(chybne_fragmenty_list[index_chybnych_fragmentov], client.dest_addr)
                    index_chybnych_fragmentov += 1
                else:
                    client.socket.sendto(list_of_fragments[index_to_insert], client.dest_addr)
                index_to_insert += 1

            else:
                if (len(sliding_window) == 0) & (len(nack_list) == 0):  # znovu posielanie nack fragmentov
                    break

    client.socket.sendto(b'A', client.dest_addr)
    if volba == 'f':
        print("------------------------")
        print("Čakanie na server kým uloží prijatý súbor....")
        print("------------------------")
    thread_pocuvanie_ack.join(60)


def pocuvanie_ack_packetov(client, sliding_window, nack_list):
    client.socket.settimeout(2)
    while True:
        try:
            response, dest_addr = client.socket.recvfrom(1500)
            flag = chr(response[0])
            fragment_num = int.from_bytes(response[1:4], 'big')
            print("f_num: ", fragment_num)
            if fragment_num == 0:  # vyskoci z while cyklu,ukonci thread
                print("Dáta boli úspešne doručené.\n")
                return

            if flag == 'A':                             # dorucene ACK
                for i in range(len(sliding_window)):
                    if sliding_window[i] == fragment_num:
                        sliding_window.pop(i)
                        if i > 0:
                            nepotvrdeny = sliding_window[0]
                            nack_list.append(nepotvrdeny)
                            sliding_window.pop(0)
                        break
                print("ACK")

            elif flag == 'N':                           # dorucene NACK
                for i in range(len(sliding_window)):
                    if sliding_window[i] == fragment_num:
                        # nepotvrdeny = sliding_window.pop(i)
                        nack_list.append(sliding_window.pop(i))
                        break
                print("NACK")
        except socket.timeout:                          # vyprsanie timeoutu
            for i in range(len(sliding_window)):
                nack_list.append(sliding_window.pop(i))
        except ConnectionResetError:
            print("prenos neúspešný, prijímajúca strana prerušila spojenie.")
            print("Vypínam...")
            sleep(2)



def keep_alive(client):
    global keep_alive_status
    pocitadlo = 0
    while keep_alive_status:

        sleep(3)
        client.socket.sendto(b'K', client.dest_addr)
        # print("keep-alive poslany")
        try:
            client.socket.settimeout(3)
            data, dest_addr = client.socket.recvfrom(1500)
            data = data.decode(FORMAT)
            pocitadlo = 0
            # print(data)
            # print("keep-alive doruceny")
            if data == 'F':                         # FIN
                print("\nServer ukončil spojenie")
                print("Vypínanie...")
                sleep(2)
                os._exit(0)
            if data == 'C':
                print("Ziadost o vymenu roli - c!!!")
                print("c/n:")
                keep_alive_status = False
                client.socket.settimeout(None)
        except:
            print("server neodpovedá na keep-alive, posielam znovu.")
            pocitadlo += 1
            if pocitadlo == 3:
                print("Server nereaguje, vypínam...")
                os._exit(0)



    client.socket.settimeout(None)


def nacitanie_suboru(absolute_route):
    file = open(absolute_route, 'rb')
    data = file.read(1500 * 1024 * 1024)
    file.close()
    return data


# sekcia spolocne

def vymena_roli(iniciator,meno):

    print("Výmena rolí")
    iniciator.socket.sendto(b'C', iniciator.dest_addr)
    iniciator.socket.settimeout(30)
    try:
        data, dest_addr = iniciator.socket.recvfrom(1500)
        iniciator.socket.settimeout(None)
    except:
        print("Ziadna odpoved z druhej strany")
        return

    if data == b'A':
        print("roly uspesne vymenené")
        if meno == "Klient":
            client_main(iniciator)
        else:
            server_main(iniciator)
    elif data == b'N':
        print(meno, " zamietol vymenu roli.")
        return


def ukoncenie_programu(komunikator):
    komunikator.socket.sendto(b'F', komunikator.dest_addr)
    print("Vypínanie...")
    sleep(2)
    exit(0)

# sekcia server


def ulozenie_suboru(absolute_route, file_name, data):
    file = open(absolute_route + file_name.decode(FORMAT), 'wb')
    file.write(data)
    file.close()


def rozbalenie_hlavicky(data):
    unpack(f'{len(data)}s', data)

    flag = chr(data[0])
    crc = int.from_bytes(data[4:6], 'little')
    pocet_fragmentov = int.from_bytes(data[1:4], 'big')
    if len(data) > 6:
        data = data[6:]
    else:
        data = b''

    return flag, pocet_fragmentov, crc, data


def server_pocuvanie_bg(server, data_list, volba):
    global server_pocuvanie_bg_status
    server.socket.settimeout(None)

    while server_pocuvanie_bg_status:
        # print("cakam na keep alive")
        data, source_addr = server.socket.recvfrom(1500)
        flag, fragment_num, crc_value, data2 = rozbalenie_hlavicky(data)
        # print(data)

        if server_pocuvanie_bg_status is False:                 # server už je v stave počúvania
            if flag == 'C':
                data_list.append('C')
            elif data is not None:
                data_list.append(data)
            return
        if flag == 'K':                                         # keep-alive
            server.socket.sendto(b"A", server.dest_addr)
            continue
        elif flag == 'C':                                       # výmena roli
            print("\n--------------------")
            print("Žiadost o výmenu roli, chceš ich vymeniť? c/n")
            print("Vyber 1 možnosť:")
            server_pocuvanie_bg_status = False
        elif (flag == 'D') & (volba == ''):                     # prijatie suboru
            print("\n--------------------")
            print(f"Klient vám chce poslať súbor {data2.decode(FORMAT)}, chceš ho prijať? p/n ")
            print("Vyber 1 možnosť:")
            data_list.append(data)
            data_list.append('V')
            return
        elif (flag == 'M') & (volba == ''):                     # prijatie spravy
            print("\n--------------------")
            print(f"Klient vám chce poslať správu, chceš ju prijať? p/n ")
            print("Vyber 1 možnosť:")
            data_list.append(data)
            data_list.append('V')
            return
        elif flag == 'F':                                   # ukončenie spojenia
            print("Klient ukončil spojenie")
            print("Vypínanie...")
            sleep(2)
            os._exit(0)
        elif volba != '':
            server_pocuvanie_bg_status = False
            return


def server_prijimanie_fragmentov(server,num_of_fragments):

    list_of_data = [b'']

    for i in range(1, num_of_fragments + 2):            # vytvorenie prazdneho listu
        list_of_data.append(b'')

    server.socket.sendto(b'A', server.dest_addr)

    while True:                                         # prijímanie packetov
        # server.socket.settimeout(60)
        # try:
        data, source_addr = server.socket.recvfrom(1500)
        flag, fragment_num, crc_value, data = rozbalenie_hlavicky(data)
        # except:
        #     return

        if flag == 'A':                             # oznam o doruceni vsetkych fragmentov
            return list_of_data
        # elif random.random() > 5:                 # kontrola chyby
        #     crc_value += 2
        if crc_value == binascii.crc_hqx(data, 0):  # kontrola ci data prisli neposkodene
            response = b'A'
            list_of_data[fragment_num] = data
        else:
            response = b'N'
        ack = pack(f"c{3}s", response, fragment_num.to_bytes(3, 'big'))
        # print(ack)
        print("f-num: ", fragment_num)
        print(response.decode(FORMAT))
        server.socket.sendto(ack, server.dest_addr)


def server_pocuvanie_fg(server, data):

    if data == b'K':                                    # odpovedanie na keep-alive
        while data == b'K':
            server.socket.sendto(b"A", server.dest_addr)
            data, source_addr = server.socket.recvfrom(1500)
            # print(data)
    if data == b'C':                                    # vymena roli
        server.socket.sendto(b'A', server.dest_addr)
        print("Roly uspešne vymenené")
        client_main(server)
    if data == b'F':                                    # ukoncenie programu
        ukoncenie_programu(server)

    typ_suboru, num_of_fragments, crc_value, file_name = rozbalenie_hlavicky(data)
    list_of_data = server_prijimanie_fragmentov(server,num_of_fragments)

    if list_of_data is None:
        print("spojenie bolo prerušené")
        return

    # poskladanie dat
    file_data = b''
    for i in range(1, num_of_fragments + 1):
        file_data += list_of_data[i]

    if typ_suboru == 'D':                       # ukladanie suboru
        print("\n------------------------")
        print("Názov prenášaného súboru: ",file_name.decode(FORMAT))
        print("Počet fragmentov: ",num_of_fragments)
        print("Veľkosť fragmentu: ", len(list_of_data[1]))
        print("------------------------")

        while True:
            try:                                                # zadanie správnej adresy uloženia
                adresa = input("zadaj cestu kde chces ulozit preneseny subor, bez názvu súboru: ")
                ulozenie_suboru(adresa,file_name, file_data)
                print("------------------------")
                print("Ukladanie súboru ", file_name.decode(FORMAT) ," na adresu: ", adresa + file_name.decode(FORMAT))
                print("Súbor bol úspešne uložený ;)")
                print("------------------------")

                # prisiel cely subor, poslatie ack
                cislo = 0
                ack_all = pack(f"c{3}s", b'A', cislo.to_bytes(3, 'big'))
                server.socket.sendto(ack_all, server.dest_addr)
                break
            except:
                print("zadaná adresa neexistuje!!")

    elif typ_suboru == 'M':                         # vypis spravy
        server.socket.sendto(b'A', server.dest_addr)
        print("\n------------------------")
        print("Správa bola úspešne prenesená.")
        print("Počet fragmentov: ", num_of_fragments)
        print("Veľkosť fragmentu: ", len(list_of_data[1]))
        print("------------------------")
        print("Správa od klienta:")
        print(file_data.decode())


def server_start(port):
    server = Communicator
    server.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.socket.bind(("localhost", int(port)))

    print("nadviazanie spojenia...")
    server.socket.settimeout(60)
    try:
        data, server.dest_addr = server.socket.recvfrom(1500)  # adresa s ktorou komunikuje server, čiže ip a port klienta
        data = data.decode(FORMAT)
        server.socket.settimeout(None)
    except TimeoutError:
        print("spojenie sa nepodarilo nadviazat")
        exit(0)

    if data == "S":
        server.socket.sendto(b"A", server.dest_addr)
        print(f"\n[NOVÉ SPOJENIE] {server.dest_addr} úspešne pripojené.")
        # print(server.socket)

    else:
        print("spojenie sa nepodarilo nadviazat")
        exit(0)

    server_main(server)


def server_main(server):
    global server_pocuvanie_bg_status
    global server_bg_thread

    while True:
        data_list = []
        volba = ''
        # if server_pocuvanie_bg_status is True:
        server_pocuvanie_bg_status = True
        server_bg_thread = threading.Thread(target=server_pocuvanie_bg, args=(server, data_list, volba),daemon=True)
        server_bg_thread.start()

        print("\nPonuka:\n----------------")
        print("Počúvanie   - p\nVýmena rolí - v\nUkončenie   - q\n----------------")
        volba = input("Vyber 1 možnosť: ")

        server_pocuvanie_bg_status = False

                # osetrenie inej zadanej volby pri potvrdzovani prijatia prenosu dat
        if (len(data_list) == 2) & ((volba == 'v') | (volba == 'c')):
            print("Momentálne nemožno žiadať o vymenu roli")
            volba = 'n'

        if volba == 'p':
            print("server počúva...")
            server_bg_thread.join()
            data = data_list[0]
            server_pocuvanie_fg(server,data)
            server_pocuvanie_bg_status = True
        elif volba == 'q':
            ukoncenie_programu(server)
        elif volba == 'v':
            vymena_roli(server,"Klient")
        elif volba == 'c':
            server.socket.sendto(b'A', server.dest_addr)
            print("Roly uspešne vymenené")
            client_main(server)
        elif volba == 'n':
            server.socket.sendto(b'N',server.dest_addr)
            print("Odmietnute")


if __name__ == '__main__':
    print("--------------------------------------")
    print("|  UDP komunikátor                   |")
    print("|  autor: Tomáš Socha                |")
    print("--------------------------------------")

    while 1:

        # os.system("cls")
        print("\nvyber funkcionalitu programu:\n------------------")
        print("Prijímač - p \nVysielač - v")
        print("------------------")
        mode = input("zvoľ 1 možnosť: ")

        if mode == 'p':
            try:
                server_start(input("Zadaj čislo portu: "))
            except OSError:
                print("zvolený port už je používaný, zvoľ iný.")
                continue
        elif mode == 'v':
            try:
                client_start(input("Zadaj ip adresu:"), input("Zadaj čislo portu: "))
            except OSError:
                print("Zadané údaje už sú používané,zadaj iné")
                continue
        elif mode == 'q':
            break
        else:
            print("neprávne zadaná možnosť!!!")



