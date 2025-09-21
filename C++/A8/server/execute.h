#ifndef __EXECUTE_H
#define __EXECUTE_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Execute{
public:
	void LogIn();
	void print_instruction();
	void Run();
	void Run1();
	void connect_to_server(int argc , char* argv[] );
	void disconnect();
	void compose_msg1();
	void compose_msg();
  	void add_friend();
	void show_last_msgs();
	void show_msgs_from();
	void Register();
	void show_msgs();
	void del_friend();
private:
	int sockfd;
	bool isAdmin;
};

#endif
