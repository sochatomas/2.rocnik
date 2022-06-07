

#ifndef ZADANIE2_PROMPT_H
#define ZADANIE2_PROMPT_H

void prompt(int prompt_status){

    time_t mytime = time(NULL);
    char * time_str = ctime(&mytime);
    time_str[strlen(time_str)-1] = '\0';

    struct passwd *pass = getpwuid(getuid());               // user name
    char *name = pass->pw_name;

    char hostname[HOST_NAME_MAX];                           // device name
    gethostname(hostname, HOST_NAME_MAX);

    char * curr_time = malloc(50*sizeof(char));        // current time
    bzero(curr_time,50);
    strncpy(curr_time,(time_str)+10,6);

    char * prompt = malloc(50*sizeof(char));

    if (prompt_status == 0){
        strcpy(prompt,name);
        strcat(prompt,"@");
        strcat(prompt,hostname);
        strcat(prompt,"# ");
        strcat(curr_time," ");
        strcat(curr_time,prompt);
    }
    if(prompt_status == 1)                      // swap hostname and name
        {
        strcpy(prompt,hostname);
        strcat(prompt,"@");
        strcat(prompt,name);
        strcat(prompt,"# ");
        strcat(curr_time," ");
        strcat(curr_time,prompt);
        }
    if(prompt_status == 2)                      // time at the end of the prompt
        {
        strcpy(prompt,name);
        strcat(prompt,"@");
        strcat(prompt,hostname);
        strcat(prompt," ");
        strcat(prompt,curr_time);
        strcpy(curr_time,prompt);
        strcat(curr_time,"# ");
        }
    if(prompt_status == 3)                      // time omitted
        {
        strcpy(prompt,name);
        strcat(prompt,"@");
        strcat(prompt,hostname);
        strcat(prompt,"# ");
        strcpy(curr_time,prompt);
        }


    write(1, curr_time, strlen(curr_time));     //write prompt
    free(curr_time);
}


#endif //ZADANIE2_PROMPT_H
