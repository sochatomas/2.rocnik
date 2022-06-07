/*Autor: Tomáš Socha
 * Predmet: Spaasm
 * Zadanie2: Napíšte v jazyku C jednoduchý interaktívny program, "shell", ktorý bude opakovane čakať na zadanie príkazu
 *           a potom ho spracuje. Na základe princípov klient-server architektúry tak musí s pomocou argumentov
 *           umožňovať funkciu servera aj klienta. Program musí umožňovať spúšťať zadané príkazy a bude tiež
 *           interpretovať aspoň nasledujúce špeciálne znaky: # ; < > | \ .
 *
 *  Spravené volitelne ulohy: 9. (3 body) S prepínačom "-c" v kombinácii s "-i", resp. "-u" sa bude program správať ako klient,
 *                  teda pripojí sa na daný soket a bude do neho posielať svoj štandardný vstup a zobrazovať
 *                  prichádzajúci obsah na výstup
 *                  11. (2 body) S prepínačom "-i" bude možné zadať aj IP adresu na ktorej bude program očakávať
 *                  spojenia (nielen port).
 *                  14. (3 body) Konfigurovateľný tvar promptu, interný príkaz prompt.
 *                  17. (2 body) Jeden z príkazov bude využívať funkcie implementované v samostatnej knižnici,
 *                  ktorá bude "prilinkovaná" k hlavnému programu.
 *                  28. (2 body) Funkčný Makefile.
 *                  30. (1 bod) Dobré komentáre, resp. rozšírená dokumentácia, v anglickom jazyku.
 *
 * */
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/un.h>

#include <sys/wait.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdlib.h>
#include <ctype.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <time.h>

#include <unistd.h>
#include <limits.h>
#include <pwd.h>
 #include <fcntl.h>
#include "prompt.h"

void pipe_found(char **first_comm, char **second_comm) {
    int fd[2];                                          //inicialisation of file descriptors 0-read, 1-write to pipe
    pipe(fd);                                           //pipe creation

    if (fork() != 0)
    {                                                   // parent process  - writing to pipe
        dup2(fd[1], 1); 	   // closing std_out and rewrite 1 to fd1 (for writing to pipe)
        close(fd[0]); 		                // closing fd for reading
        close(fd[1]); 		                          // closing fd for writing

        execvp(first_comm[0], first_comm);              // output will be sent to 1(stdout was rewritten to output to a pipe
        perror(first_comm[0]);
        exit(2);
    } else
    { 	                                       // child proces   - reading from pipe
        dup2(fd[0], 0); 		 // close stdin and rewrite for reading from pipe
        close(fd[0]);
        close(fd[1]); 		                // close fd for writing

        execvp(second_comm[0], second_comm);        // input reading from pipe, not from stdin
        perror(second_comm[0]);
        exit(2);
    }
}


int comm_execute(char **comm,int comm_len,int client_socket){

    pid_t pid,wpid;
    int status;
    pid = fork();                   //create child process

    if(pid == 0)                    //child proces
    {
        int i = 0;
        while (i++ < comm_len) {


            if (comm[i] != NULL && strcmp(comm[i], "|") == 0 && (strchr(comm[i], '|')-strchr(comm[i], '\\') != 1)) {        // pipe found in command
                comm[i] = NULL;	                                        // delete pipe
                pipe_found(comm, comm + i + 1);
                break;
            }
            if (comm[i] != NULL && strchr(comm[i], ';') != NULL  && (strchr(comm[i], ';')-strchr(comm[i], '\\') != 1)) {    // more commands in buffer
                comm[i] = NULL;	                                        // delete ;

                pid_t pid2,wpid2;
                int status2;
                pid2 = fork();                                          // create child process
                if(pid2 == 0)
                    execvp(comm[0],comm);                       //execute command
                else
                {
                    do
                    {
                        wpid2 = waitpid(pid2, &status2, WUNTRACED);      // parent process waiting for child process to execute
                    }while(!WIFEXITED(status2) && !WIFSIGNALED(status2));

                    execvp(comm[i+1],comm +i+1);        //execute command
                }
            }
            if (comm[i] != NULL && strchr(comm[i], '>') != NULL && (strchr(comm[i], '>')-strchr(comm[i], '\\') != 1))   //  redirection output to a file
            {   int out_file;
                out_file = open(comm[i + 1], O_WRONLY | O_CREAT, 0666);         //create/open output filw
                if(out_file < 0) perror("file create");                                    // handling error
                dup2(out_file,1);                                                       // redirect output to a opened file
                if(strlen(comm[i]) == 1) write(client_socket,"",1);             // send empty message to client for showing prompt

                comm[i] = NULL;
                execvp(comm[0],comm);                                                   // exec. command
            }
            if (comm[i] != NULL && strchr(comm[i], '<') != NULL && (strchr(comm[i], '<')-strchr(comm[i], '\\') != 1))   //  redirection output to a file
                {   int in_file;
                    in_file = open(comm[i + 1], O_RDONLY, 0666);         //open input file
                    if(in_file < 0) perror("file open");                                    // handling error
                    dup2(in_file,0);                                                       // redirect output to a opened file

                    comm[i] = NULL;
                    execvp(comm[0],comm);                                                   // exec. command
                }
            if(comm[i] != NULL && strchr(comm[i], '#') != NULL && (strchr(comm[i], '#')-strchr(comm[i], '\\') != 1))      // comment found
            {
                char *ptr = strchr(comm[i],'#');
                char * tmp = malloc(sizeof(char)* strlen(comm[i]));

                strncpy(tmp,comm[i], strlen(comm[i])- strlen(ptr));                     // split command
                strcpy(comm[i],tmp);
                execvp(comm[0],comm);                                                  //execute just executable command
            }

            if(comm[i]!= NULL && strchr(comm[i],'\\')!= NULL)                             // backslash identified
            {
                char * ptr=strchr(comm[i],'\\');
                char * tmp = malloc(sizeof(char)* strlen(comm[i]));

                int size = strlen(comm[i])- strlen(ptr);
                strncpy(tmp,comm[i],size);
                strcat(tmp,comm[i]+size+1);                                 // remove backslash from command
                strcpy(comm[i],tmp);
            }


//            if (strcmp(comm[0],"ls") == 0)
//            {  char ** comm2 = malloc(sizeof(char *)*2) ;
//                comm2[0] = "pwd";
//                comm2[1] = NULL;
//                pipe_found(comm2,comm);
//                break;
//            }
        }
        if ( (i >= comm_len) && (execvp(comm[0],comm) == -1)){ perror(comm[0]);}            // catch error
        free(comm);
        exit(EXIT_FAILURE);
    }else
    {
        do
        {
            wpid = waitpid(pid, &status, WUNTRACED);            // waiting for child process
        }while(!WIFEXITED(status) && !WIFSIGNALED(status));
    }
    return 1;
}


int terminate(int client_socket, int server_socket, char *buffer, pid_t parent_pid){
    if(strcmp(buffer,"quit\n") == 0)                        // client terminate
    {
        close(client_socket);
        exit(0);
    }
    if(strcmp(buffer,"halt\n") == 0)                        // cliens as well as server terminate
    {
        close(client_socket);
        close(server_socket);
        kill(parent_pid,SIGKILL);
        exit(0);
    }
}


void add_to_comm(char *tok,char **comm, int *index, char val){          // split 1 string to 3 parts when space between commands not occured (ls;ls)

    char *ptr = strchr(tok,val);
    comm[(*index)] = malloc(sizeof(char)* strlen(tok));
    comm[(*index)+1] = malloc(sizeof(char)* 1);
    comm[(*index)+2] = malloc(sizeof(char)* strlen(tok));
    strncpy(comm[(*index)++],tok,strlen(tok) - strlen(ptr));
    strcpy(comm[(*index)++],&val);
    strncpy(comm[(*index)++],tok + strlen(tok) - strlen(ptr)+2, strlen(ptr)-1);
}

int server_comm(int client_socket,int server_socket,pid_t parent_pid){

    int bytes_read;
    char *buffer = (char *)malloc(161*sizeof(char));

    dup2(client_socket,1);                                              // redirect output from server to client shell
    dup2(client_socket,2);                                              // redirect stderr from server to client shell

    while((bytes_read=read(client_socket,buffer,160)) > 0)              // cycle for reading prompts from client
    {
        terminate(client_socket,server_socket,buffer,parent_pid);                   //check if terminate
        if(strcmp(buffer,"help\n") == 0)
        {
            printf("Predmet: SPAASM\nZadnie 2\nAutor:Tomas Socha\n\n\nProgram sa sprava ako jednoduchy interaktivny shell.\n Je postaveny na principe klient-server architektury, takze je mozne ho spustit ako server alebo klient.\nServer je mozne spustit bez prepinaca, alebo zadanim prepinaca -s\n Klient sa spusta pomocou prepinaca -c\n\nPri spusteni je taktiez pomocou prepinacov -p a -i definovat port a ip adresu na ktorych ma cakat na spojenie\n\n Po spusteni a uspesnom nadviazani spojenia je mozne zadavat prikazy do terminalu, ktore sa nasledne poslu na server,ktory ich spracuje a vysledok odosle naspet klientovi\n\n Pre ukoncenie klienta je urceny prikaz quit.\n Pre ukoncenie aj servera je urceny prikaz halt\n\nShell taktiez ponuka moznost konfigurovat si prompt, a to zadanim prikazu prompt s argumentom, ktore je cislo od 0 po 4  0-> default\n 1-> vymeneny nazov zariadenia s userom\n 2-> cas je ako posledny\n 3-> prompt bez aktualneho casu\n");
            continue;
        }
        buffer[bytes_read] = 0;

        char **comm = (char **) malloc(sizeof(char *)*20);
        char * tok = strtok(buffer," \n\a\t\r");
        int index = 0;

        while(tok != NULL)                                  // going through tokens
        {                                               // searching for supported special characters

            if((strchr(tok,'#') !=NULL) && (strcmp(tok,"#") != 0) && ((strchr(tok,'\\') == NULL) || ((strlen(strchr(tok,'#'))- strlen((strchr(tok,'\\'))) != 1)) )) add_to_comm(tok,comm,&index,'#');
            else {
                if((strchr(tok,'|') !=NULL) && (strcmp(tok,"|") != 0) &&((strchr(tok,'\\') == NULL) || ((strlen(strchr(tok,'|'))- strlen((strchr(tok,'\\'))) != 1)) )) add_to_comm(tok,comm,&index,'|');
                else{
                    if((strchr(tok,'>') !=NULL) && (strcmp(tok,">") != 0) && ((strchr(tok,'\\') == NULL) || ((strlen(strchr(tok,'>'))- strlen((strchr(tok,'\\'))) != 1)) )) add_to_comm(tok,comm,&index,'>');
                    else{
                        if((strchr(tok,';') !=NULL) && (strcmp(tok,";") != 0) && ((strchr(tok,'\\') == NULL) || ((strlen(strchr(tok,';'))- strlen((strchr(tok,'\\'))) != 1)) )) add_to_comm(tok,comm,&index,';');
                        else
                        {
                            comm[index++] = tok;
                        }
                    }
                }
            }
            //                comm[index] = tok;
            //                 index ++;
            tok = strtok(NULL," \n\a\t\r");             // next string

        }
        comm[index] = NULL;

        if(comm[0][0] != 0) comm_execute(comm,index,client_socket);
        else write(client_socket,"",1);               // nothing to execute

        memset(buffer,0, bytes_read);
        free(comm);
    }
}


int server(char * ip,char * port) {

    int server_socket, addr_size, client_socket,pid,rodic = 1,port_no;
    pid_t parent_pid = getpid();
    port_no = atoi(port);

    struct sockaddr_in server_addr;
    struct sockaddr* server_addr_ptr;

    server_addr_ptr = (struct sockaddr*) &server_addr;
    addr_size = sizeof (server_addr);
    server_socket = socket( AF_INET, SOCK_STREAM, 0);       //create server socket

    server_addr.sin_family = AF_INET;                            //set sockaddr parameters for server
    server_addr.sin_addr.s_addr = inet_addr(ip);
    server_addr.sin_port = htons(port_no);

    bind(server_socket, server_addr_ptr, addr_size);            //bind
    listen(server_socket, 5);                                   // listen for connections
    fprintf(stderr, "[SERVER] pocuva na porte %d...\n", port_no);

    while(rodic){                                           // accepting connections

        client_socket = accept(server_socket, NULL, NULL);      //accept connection
        if(client_socket < 0) perror("ERROR on accept");
        printf("spojenie bolo nadviazane\n");

        pid = fork();                                           //create child process for established connection

        if(pid == 0)
        {
            rodic = 0;
            server_comm(client_socket,server_socket,parent_pid);        // calling function for communication
            close(client_socket);
        }
    }
    close(client_socket);
    close(server_socket);
    exit(0);
}



int client_comm(int server_socket,int *status,fd_set *fd,int *prompt_status){
    int bytes_read;
    char *buffer = (char *)malloc(161*sizeof(char));
    bzero(buffer,160);
    char *prompt_comm = (char *) malloc(7*sizeof(char));

    if (FD_ISSET(0, fd))		                            //  deskriptor 0 -> std_input
        {
        bytes_read=read(0, buffer, 160);	    // citanie z std_input
        strncpy(prompt_comm,buffer,6);

        if (strcmp(prompt_comm,"prompt")== 0)                       // handle prompt command
        {   int pom = buffer[7]-'0';
            if(pom < 4 && pom >= 0)                                 //testing parameter
            {
                *prompt_status = pom;
                printf("Prompt was successfully changed to layout %d \n",*prompt_status);
            }
            else printf("Wrong parameter!!\n");
            *status = 1;
        }else{
            if(strcmp(buffer,"\n") != 0) write(server_socket, buffer, bytes_read);	                    // sending message to server (through socket)
            else *status = 1;                                                                           //set variable for enable prompt to be written to shell
        }

        if((strcmp(buffer, "quit\n") == 0) || ( strcmp(buffer, "halt\n") == 0) )                        // handle quit command
        {
            close(server_socket);
            exit(0);
        }

        }
    if (FD_ISSET(server_socket, fd))		                            // socket of connection to a server
        {
        bytes_read=read(server_socket, buffer, 160);	    // reading from server
        write(1, buffer, bytes_read);	                        // write to deskriptor ,1 = std_output
        if((bytes_read < 160) && (bytes_read > 0)) *status = 1;
        }
    if(*status == 1)                                               //print prompt to a shell
    {
        prompt(*prompt_status);
        *status = 0;
    }

    FD_ZERO(fd);	// variable needs to be set again
    FD_SET(0, fd);
    FD_SET(server_socket, fd);
    free(buffer);
    free(prompt_comm);

}

int client(char *ip, char *port) {

    int server_socket, server_size, port_no, result,bytes_read,prompt_status = 0;
    struct sockaddr_in server_addr;
    unsigned long ip_address;

    server_size = sizeof(server_addr);
    ip_address = inet_addr(ip);
    port_no = atoi(port);                                       // port convert to number

    if(ip_address == 0) perror("ERROR host name not found");

    bzero((char *) &server_addr, server_size);                  // server_addr set to zero
    server_addr.sin_family = AF_INET;                           // set variable for server sockaddr
    server_addr.sin_addr.s_addr = ip_address;
    server_addr.sin_port = htons(port_no);

    server_socket = socket(AF_INET, SOCK_STREAM, 0);            // create socket
    if (server_socket < 0) perror("ERROR opening socket");
    do {
        result = connect(server_socket, (struct sockaddr *)&server_addr, server_size);      //connect to a server
    }
    while(result == -1);

    fd_set fd;
    char * buffer;
    int status = 0;

    buffer = (char *)malloc(161*sizeof(char));
    bzero(buffer,160);

    FD_ZERO(&fd);                                                                   //clear set
    FD_SET(0, &fd);
    FD_SET(server_socket, &fd);

    prompt(prompt_status);                                                          //print prompt
    while(select(server_socket+1, &fd, NULL, NULL, NULL) > 0)
    {
        client_comm(server_socket,&status,&fd,&prompt_status);                  //communication with server
    }
    perror("select:");
    close(server_socket);
    free(buffer);

}


int main(int argc, char *argv[]){

    int client_bool = 0,h = 0;
    char *ip = (char*)malloc(10*sizeof(char));;
    char *port = (char*)malloc(5*sizeof(char));
    char *help = "Predmet: SPAASM\nZadnie 2\nAutor:Tomas Socha\n\n\nProgram sa sprava ako jednoduchy interaktivny shell.\n Je postaveny na principe klient-server architektury, takze je mozne ho spustit ako server alebo klient.\nServer je mozne spustit bez prepinaca, alebo zadanim prepinaca -s\n Klient sa spusta pomocou prepinaca -c\n\nPri spusteni je taktiez pomocou prepinacov -p a -i definovat port a ip adresu na ktorych ma cakat na spojenie\n\n Po spusteni a uspesnom nadviazani spojenia je mozne zadavat prikazy do terminalu, ktore sa nasledne poslu na server,ktory ich spracuje a vysledok odosle naspet klientovi\n\n Pre ukoncenie klienta je urceny prikaz quit.\n Pre ukoncenie aj servera je urceny prikaz halt\n\nShell taktiez ponuka moznost konfigurovat si prompt, a to zadanim prikazu prompt s argumentom, ktore je cislo od 0 po 4  0-> default\n 1-> vymeneny nazov zariadenia s userom\n 2-> cas je ako posledny\n 3-> prompt bez aktualneho casu\n ";

    strcpy(port,"5050");                //default values
    strcpy(ip,"127.0.0.1");

    for(int i = 1;i < argc; i++)                // reading args
    {
        if(strcmp(argv[i],"-c") == 0) { client_bool = 1; continue;}         // client
        if(strcmp(argv[i],"-h") == 0){ h = 1; continue;}                    // help
        if(strcmp(argv[i],"-s") == 0) continue;                             // server
        if(strcmp(argv[i],"-p") == 0)                                       //port defined
        {
//            argv[i+1][strlen(argv[i+1])] = '\0';
            if((i+1 < argc) && (argv[i+1][0] != '-') ) strcpy(port,argv[i+1]);  // reading argument
            else {
                printf("error: zle zadane argumenty");
                exit(1);
            }
            i++;
            continue;
        }
        if(strcmp(argv[i],"-i") == 0)                                   // ip address defined
        {
            if((i+1 < argc) && (argv[i+1][0] != '-')) strcpy(ip,argv[i+1]);
            else {
                printf("error: zle zadane argumenty");
                exit(1);
            }
            i++;
            continue;
        }
        printf("error:Neznamy prepinac");
        exit(1);
    }

    if(h) printf("%s\n", help);
    if (client_bool) client(ip,port);
    else server(ip,port);

    return 0;
}

/*Podpora specialnych znakov ako napr(|,<,>,#,\) funguje len pri prvom vyskyte daneho znaku.
 * Program zvlada citat a vykonat prikazy aj bez medzery(napr ls;ls).
 * Pri konfigurovani promptu je mozne si zvolit zo 4 typov, teda nieje mozne si do neho vlozit hocico.
 * Server len prijima prikazy od klienta, pripadne vypise nove spojenie, teda nieje mozne vykonat prikazy zadanim
 * do shellu servera tak ako pri klientovi. Server je mozne ukoncit prikazom halt zadaneho v klientovi.
 * */
