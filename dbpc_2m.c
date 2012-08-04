#include   <errno.h>
#include   <strings.h>
#include   <string.h>
#include   <sys/stat.h>   
#include   <sys/types.h>   
#include   <sys/socket.h>   
#include   <stdio.h>   
#include   <malloc.h>   
#include   <netdb.h>   
#include   <fcntl.h>
#include   <unistd.h>
#include   <netinet/in.h>
#include   <arpa/inet.h>
#include   <sys/time.h> 

#define    RES_LENGTH  64

int     connect_socket(char * server,int serverPort);
int     send_msg(int sockfd,char * sendBuff);
char *  recv_msg(int sockfd);
int     close_socket(int sockfd);
static char response[64];

int main(int argc,char ** argv)
{
    int    sockfd=0;
    static char sendMsg[64]="{\"status\":[{\"service\":\"VTWeb\",\"component\":\"Test\"}]}";
    int     timeuse, connect_time, send_time, recv_time, close_time,recvlat;
    struct timeval start, end, connect_t, send_t, recv_t,recvlat_t;

    static char ip[1024];

    strcpy(ip, argv[1]);

    int count = 0;
    int c_count = 0;
    int r_count = 0;
    int local_port = 0;

    int i = 0;

    for(i=0; i<5000; i++) {
        gettimeofday( &start, NULL );
        sockfd = connect_socket(ip, 5800);
        if(sockfd == -1) {
            sleep(1);
            continue;
        }
        gettimeofday( &connect_t, NULL );
        send_msg(sockfd,sendMsg);
        gettimeofday( &send_t, NULL );
        recvlat = recv_issue(sockfd);
        gettimeofday( &recv_t, NULL );
        local_port = get_local_port(sockfd);
        close_socket(sockfd);
        gettimeofday( &end, NULL );
        connect_time = 1000000 * ( connect_t.tv_sec - start.tv_sec ) + connect_t.tv_usec - start.tv_usec; 
        send_time = 1000000 * ( send_t.tv_sec - connect_t.tv_sec ) + send_t.tv_usec - connect_t.tv_usec; 
        recv_time = 1000000 * ( recv_t.tv_sec - send_t.tv_sec ) + recv_t.tv_usec - send_t.tv_usec;
        close_time = 1000000 * ( end.tv_sec - recv_t.tv_sec ) + end.tv_sec - recv_t.tv_sec;
        timeuse = 1000000 * ( end.tv_sec - start.tv_sec ) + end.tv_usec - start.tv_usec; 
        if(timeuse > 1000000) {
            if(count % 20 == 0)
                fprintf(stderr, " count conn_wt  W  R  recv_wt  C total_tm  timestamp   port   response  con/rcv/all(%)\n");
            count += 1;
            if(connect_time > 1000000 ) c_count +=1;
            if(recv_time > 1000000 ) r_count +=1;
            fprintf(stderr, "%6d %7d %2d %2d %8d %2d %8d %10d %6d %10s %4.1f/%4.1f/%4.1f\n", i, connect_time, send_time, recvlat,recv_time, close_time, timeuse, (int)start.tv_sec, local_port, response, c_count*100.0/i, r_count*100.0/i, count*100.0/i);
        }
        sleep(0.01);
    }
    return 0;
}

int    get_local_port(int fd){
    struct sockaddr_in sa;
    int sa_len = 0;
    sa_len = sizeof(sa);
    getsockname(fd,(struct sockaddr *)&sa,(socklen_t *)&sa_len) ;
    return (int) ntohs(sa.sin_port);
}

int    connect_socket(char * server,int serverPort){
    int    sockfd=0;
    struct    sockaddr_in    addr;
    struct    hostent        * phost;
    if((sockfd = socket(AF_INET,SOCK_STREAM,0))<0){
        perror("Init socket error!");
        return -1;
    }

    bzero(&addr,sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(serverPort);
    addr.sin_addr.s_addr=inet_addr(server);
    if(addr.sin_addr.s_addr == INADDR_NONE){
        phost = (struct hostent*)gethostbyname(server);
        if(phost==NULL){
            perror("Init socket s_addr error!");
            return -1;
        }
        addr.sin_addr.s_addr =((struct in_addr*)phost->h_addr)->s_addr;
    }
    if(connect(sockfd,(struct sockaddr*)&addr,sizeof(addr))<0) {
        perror("connect to remote server");
        return -1;
    }
    else
        return sockfd;

}

int send_msg(int sockfd,char * sendBuff){
    int    sendSize=0;
    if((sendSize=send(sockfd, sendBuff, strlen(sendBuff),0))<=0){
        perror("Send msg error!");
        //herror("Send msg error!");
        return -1;
    }else
        return sendSize;
}

int recv_issue(int sockfd){
    struct timeval t_trigger;
    int flag = 0;
    int flags = fcntl(sockfd, F_GETFL, 0);
    static int start_time = 0;
    static int end_time = 0;
    int cnt=0;
    fcntl(sockfd, F_SETFL, flags|O_NONBLOCK);
    do {
        gettimeofday(&t_trigger,NULL);
        start_time = 1000000 * t_trigger.tv_sec + t_trigger.tv_usec;
        flag = recv(sockfd, response, RES_LENGTH,0);
        gettimeofday(&t_trigger,NULL);
        end_time = 1000000 * t_trigger.tv_sec + t_trigger.tv_usec;
        // success
        if( flag > 0) {
            response[flag]='\0';
            goto out;
        }
        // fatal error
        if(errno != EAGAIN) {
            perror("Recv msg error!");
            return -1;
        }
        sleep(0.1);
    } while(1);

out:
    return end_time - start_time;
}

int close_socket(int sockfd){
    close(sockfd);
    return 0;
}
