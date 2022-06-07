;Autor: Tom?? Socha
;Predmet: SPAASM
;Zadanie1:  15. Vyp?sa? v?etky riadky ktor? obsahuj? n?zov vstupn?ho s?boru (bez pr?pony) v ktorom sa nach?dzaj?.
;Spravene bonusove ulohy:   Plus 1 bod: Po zadan? prep?na?a '-p' bude v?stup str?nkovan?, teda po zaplnen? obrazovky sa po?k? na stla?enie kl?vesu.
                            ;Plus 1 bod: Pri str?nkovan? sa v?dy zobraz? aj absol?tna cesta zobrazovan?ho (spracov?van?ho) vstupn?ho s?boru. Ak je dlh?ia ne? riadok, bude v prostriedku vhodne skr?ten?.
                            ;Plus 1 bod: Ak bud? korektne spracovan? vstupn? s?bory s ve?kos?ou nad 64 kB.
                            ;Plus 2 body: Ak bude mo?n? zada? viacero vstupn?ch s?borov.
                            ;Plus 1 bod je mo?n? z?ska? za (dobr?) koment?re, resp. dokument?ciu, v anglickom jazyku.

include makro.txt           ;includnute funkcie print a fileopen        (?nclude functions print and fileopen)

BUFFSIZE EQU 84
jumps                   ; povolenie skokov na vecsie vzdialenosti      (enable jumps for longer distances)                  
 .model small           ; deklaracia maleho modulu                      (declaration of small type of model)

 .stack 20h             ; deklaracia zasobnikoveho segmentu velkosti 32B    (stack declaration of size 32B)

 .data 
 file_handle DW   ?      

BUFF DB 85 DUP ('$'),'$'
riadok DW ?                         ;pointer na zaciatok riadka v bufferi       (pointer pointing to beginning of line in buffer )
prvy_r DB 1                         ;indikator vypisu prveho riadka             (boolean value represents if first line is going to be printed )
nr    db 0dh, 0ah,'$'               ;nastavi vypis na novy riadok               (set pointer for output to the next line)
eror  DB 'Subor sa nepodarilo otvorit$'        ;vypis pre neuspesne otvorenie suboru    (Answer print to output after reaching carry flag to value 1 while trying to open file)
nazov DB 12 DUP ('$')               ;nazov citaneho suboru bez pripony          (file name of reading file without suffix)
posun DW 0                          ; posun vramci riadka                       (offset in a current line)
velkost DW 0                        ;velkost nacitanych znakov v bufferi        (amount of loaded characters in buffer)
subor DB '\'
subory  DB 20 DUP('$')              ; ulozeny citany subor                      (stored file name of currently reading file)

prepinac DB 0                       ; ulozenie prepinaca nacitaneho z argumentu (stored parameter for program loaded as an argument)
zac_argument DW 0,0                 ; zaciatocna adresa akt.argumentu           (starting adress of current argument)
kon_argument  DW 0,0                ; koncova adresa akt.argumentu              (ending adress of current argument)
bool_next_argument  DB 1            ;indikator dalsieho argumentu- ci je este nejaky za nim  (boolean value represents if there is another filename to be read)
stranky DB 1                        ; pocitadlo na riadky pri strankovani           (line counter for paging)
strankovanie DB 0                   ; boolova hodnota reprezentujuca ci je vystup strankovany   (boolean value represents if output is being paged)
dir    DB 'C:\'
dir_name DB 80 DUP('$')             ;absolutna cesta nacitaneho suboru              (absolute route of loaded file)
autor DB 'Autor: Tomas Socha',10,13,'Predmet: SPAASM',10,13,10,'ZAdanie 1:',10,13
help DB 'Program sluzi na vypisanie vsetkych riadkov ktore obsahuju nazov vstupneho suboru v ktorom sa nachadzaju.',10,13,10,'Prepinac: -p  sluzi na strankovanie vypisu',10,13,'Pri strankovani sa taktiez vzdy zobrazi aj absolutna cesta spracovavaneho suboru', 10,13,'Program je mozne spustit zadanim viacerych vstupnych suborov do argumentu.',10,13,'Do argumentu sa vzdy vklada iba nazov suboru,ktory musi byt v rovnakom priecinku ako program',10,13,'Vstupne subory su korektne spracovane aj pri velkosti nad 64KB.',10,13,'$'

 .code                      ; zaciatok segmentu instrukcii                      (start of instruction segment)
START: 
    mov bl,byte ptr ES:[80h]        ;nastavenie 0 na koniec argumentov          (set 0 at the end of arguments in psp)
    mov byte ptr [bx+81h],0
    
    
    MOV AX, @data       
    MOV DS, AX                      ;nastavenie adresy datoveho segmentu        (setting an address of data segment)
    
        
    mov si,[81h]                    ; nastavenie si pre citanie argumentov      (si register set for reading arguments)
    mov kon_argument, si
    
                                    ;cyklus pre citanie viacerych suborov       (cycle for reading more files)
dalsi_subor:     
        mov di, DS:[offset subory-1]    ;zapisovanie do premennej subory        (storing data to variable subory )
        mov si,kon_argument             ;nastavenie si a di                     (set si and di)
        mov zac_argument,si
        

for:                                ;prechadzanie argumentov                    (going throught arguments)
        inc di
        inc si
        mov al,ES:[si]
        cmp al,'-'                  ;najdeny prepinac                           (parameter has been found)
        je prep
        mov [di],al
        cmp al, ' '                 ;viacej vstupnych suborov                   (psp contains more than one file to handle)
        je inc_n_arg
        cmp al,0D                   ;koniec argumentov                          (reached end of aguments)
        jne for
        mov bool_next_argument, 0   
        jmp otvor_subor
    
prep:                               ;identifikovany prepinac                    (parameter has been identified)
    inc si
    dec di
    mov al,ES:[si]
    mov prepinac,al
    cmp al,'p'                      ;identifikovany prepinac na strankovanie    (found parameter which turns paging functionality on)
    jne iny_prepinac
    mov strankovanie, 1             ; nastavenie strankovania                   (paging functionality on)
iny_prepinac:
    inc si
    mov zac_argument,si             ;ulozenie ineho prepinaca                   (unrecognized parameter has been stored)
    cmp al,'h'
    jne for
    print autor
    jmp for
inc_n_arg:                          ; viacej suborov na otvorenie              (multiple files to be open)
    mov bool_next_argument ,1
    mov kon_argument,si
    

otvor_subor:
    mov [di],0                      ;nastavenie 0 na konci nazvu suboru        (set 0 value at the end of file name string)
    
    
    FILEOPEN subory
    MOV file_handle, ax             ;ulozenie file_handle                      (storing file handle)
    JNC main                        ;kontrola spravneho otvorenia suboru        (checking if file was opened correctly)
error:                              
    print eror                      ;subor sa nepodarilo otvorit                (file wasn't able to be openes)
    MOV AH,4CH
    INT 21H
    
    
main:                               
     mov ah, 47h                    ;funkcia pre ziskanie cesty k suboru        (function that get current directory )
     mov dl, 0                      ;disk, 0 = aktualny disk.                   (drive, 0=current drive)
     mov si, offset dir_name        ;ulozenie cesty                             (storing path)
    int 21h
    print dir                       ;vypis absolutnej cesty aj s nazvom suboru  (printing absolute path with file name to output)
    print subor
    print nr
                                
    mov di,DS:[offset nazov-1]      ;nastavenie premennych na citanie nazvu suboru bez pripony      (preparation of si and di registers for reading file name without suffix)
    mov si, zac_argument    
    
    
    nacitaj_nazov:              ;nacitanie nazvu(hladaneho slova)               (loading a name of finding word)
        inc di
        inc si
        mov al,ES:[si]
        mov [di],al
        cmp al,'.'              ;slovo ukoncene bodkou                          (end of word represents by dot)
        jne nacitaj_nazov
        

        ;nastavenie premennych na prechadzanie jednotlivych riadkov (preparation of si and di registers for going through single lines)
        mov si,offset BUFF
        mov riadok, si
        mov di, offset nazov  
        
        jmp zacni_citat     ;prve citanie do buffera                        (first buffer filling )

    
nacitaj: 


    mov BX, file_handle     ; nastavenie file_pointera                      (setting file pointer)
    mov cx, -1
    mov al,1
    mov ah,42h
    int 21h

zacni_citat:
    
    MOV BX, file_handle     ; file handle suboru,z ktoreho chceme citat     (file handle of file to be read)
    MOV CX, BUFFSIZE        ; pocet bytov, kt. chceme precitat              (num. of bytes to be read)
    MOV DX, OFFSET BUFF     ; do DX ulozena relativna adresa prem. BUFF     (relative path of variable BUFF stored to DX)
    MOV AH, 3FH             ;zavolanie funkcie pre citanie zo suboru        (calling function for file reading)
    INT 21H
    
    mov velkost,ax
    cmp AX,BUFFSIZE         ;zistenie konca suboru                          ( finding end of file)
    push 1              
    jne zaciatok            ;dosiahnuty koniec suboru                       (end of file was reached)
    je zaciatok2            ;zatial nenajdeny koniec suboru                 (end of file still wasn't found)

    
   
zaciatok:
    push 0                  ;indikator konca suboru                         (boolean value represents if end of file was already found)
    mov bx, offset BUFF                  
    add bl, al                  ;vlozenie dlzky retazca                     (store length of string)
    mov byte ptr [bx], '$'      ;vlozenie '$' na koniec macitanyhc znakov zo suboru     (store $ at the end of input)
zaciatok2:

                                ;nastavenie premennych na prechadzanie nacitaneho buffera po znakoch    (preparation for going through buffer char. by char.)
      mov si,offset BUFF
      mov riadok, si
      mov di, offset nazov
      mov posun,0  
        
      
                                ;zaciatok hladania nazvu suboru v texte     (start of finding file name in text)
cyklus:

    mov al,[si]
    cmp al,'$'                  ;koniec suboru                              (end of file)
    je koniec
    cmp al,[di]
    je zhoda                    ;rovnaky znak                               (match in compared characters)
    mov di, offset nazov        ;nastavenie na zaciatok slova               (set pointer to beginning of finding word)
    inc si
    inc posun
    jmp nezhoda                 ;rozlicne znaky                             (mismatch in compared characters)
    
    zhoda:
        inc si
        inc di
        inc posun
        mov al,[di]
        cmp al,'.'             ;hladanie vsetkych moznych ukonceni slova a celej vety   (finding all kind of endings in sentence)
        jne cyklus      
        mov al,[si]
        cmp al,' '
        je match
        cmp al, '.'
        je match
        cmp al, '!'
        je match
        cmp al, '?'
        je match
        cmp al, 10              ;line feed -nastavenie na novy riadok                   (line feed)
        je match
        cmp al, 13              ; carriage return- nastavenie kurzora na zaciatok riadka    (carriage return)
        je match
        cmp al, '$'             ;koniec buffera                                             (end of buffer reached)
        je match
        jmp cyklus
    
    nezhoda:                    ;nezhoda, posun na dalsie slovo                         (mismatch, moving to nech word)
        mov al,[si]
        cmp al,' '
        je m_cyklus             ;nasla sa medzera                                   (blank space found)
        cmp al,0AH              ;najdeny koniec riadka                              (line feed cahr. found)
        je kon_riad
        cmp al,'$'              ;koniec suboru                                      (end of file found)
        je kon
        inc si
        inc posun
        jmp nezhoda
        
        m_cyklus:                   ; posun na porovnavanie dalsieho slova          (offset to compare next word)
            inc si
            inc posun
            jmp cyklus
        
    
    kon_riad:                       ;koniec riadka                          (end of line)
        inc si
        inc posun
        jmp kon
       
match:                           ;najdenie rovnakeho slova               (match in compared words)
   mov di,offset nazov
 
        cmp strankovanie,1
        jne bez_strankovania
        inc stranky                 ;strankovanie                       (paging)
bez_strankovania:
        mov si,riadok
        mov posun,0
        cmp prvy_r, 1               ;formatovanie, pred prvy riadok sa neda na novy riadok  (printed output is formatted with line feed and carriage return, not used in first line)
        je pokrac
        print nr
pokrac: mov prvy_r,0
        jmp dalsi_riadok
        
      
        dalsi_riadok:               ;cyklus na prejdenie na dalsi riadok a vypisanie celeho riadka  (cycle  used for printing whole line )
            mov dl,[si]
            mov ah,02h              ;vypis znaku                            (printing character)
            int 21h
            inc si
            inc posun
            mov ax, 50h         
            cmp posun,ax            ;porovnavynie s velkostou buffera       (comparision with size of buffer)
            jne preskoc
            mov prvy_r,1            ;formatovanie vypisu                    (formatting  printed output)
  preskoc:  mov al,[si]
            cmp al,'$'              ;koniec buff                            (end of buffer)
            je kon
            cmp al,0AH              ;koniec riadka                          (line feed)
            je kon_riad
            jmp dalsi_riadok
            
            
kon:    
        cmp stranky,25           ;strankovanie vypisu                       (paging used for output)
        jne dalej
        mov ah,01h                  ;cakanie na nejaky vstup z klavesnice   (waiting for input from keyboard)
        int 21h
        mov stranky,1
        print dir                   ;v?pis absol?tnej cesty s?boru          (printing absolute path of file)
        print subor                 ;v?pis n?zvu s?boru                     (printing name of file)
        
        
dalej:        
        xor dx,dx 
        add dx,posun            ;nastavenie dx na hodnotu, o kolko sa m?  posun?? file_pointer  (setting dx to offset value of file pointer)
        sub dx,velkost      
        pop ax
        cmp ax,0                ;koniec suboru                                      (end of file)                               
        jne nacitaj
        
        inc posun           
        mov ax,posun
        sub velkost,ax
        jnl  nacitaj            ; zistenie ci sa uz nach?dzame na konci posledn?ho riadku v subore      (find out if last line in file was already reached)
        
    
    ;zavretie suboru
    MOV AH, 3EH             ;sluzba na zavretie suboru          (function that close the file)
    MOV BX, file_handle 
    INT 21H
    
    cmp bool_next_argument,1    ;zistenie ci uz boli precitane vsetky subory vlozene do argumentov  (find out if all files from arguments have been already read)
    jne koniec
    print nr                    ;priprava na vypis dalsieho suboru              (preparation for printing next file)
    print nr
    add stranky,2
    mov prvy_r,1
    jmp dalsi_subor
    
KONIEC:                         ;ukoncenie programu                             (end of program)
    
    MOV AH,4CH
    INT 21H
    end start
   
    
;Program splna bonusove ulohy spomenute na zaciatku suboru.
; Pri zadavani viacerych suborov sa zadava vzdy len nazov suboru s priponou,takze sa musi nachadzat v aktualnom adresari. Nacitavanie jednotlivych suborov prebieha v cykle takze nieje obmedzenie len na nacitanie 2 suborov.
;pri strankovanom vypise sa vzdy na prvom riadku vypise absolutna cesta prave spracovavaneho suboru
;program bez problemov zvladne spracova? aj subory nad 64KB, otestoval som to na 200KB subore bez nejakych problemov

