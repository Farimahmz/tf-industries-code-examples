/* A simple server in the internet domain using TCP
   The port number is passed as an argument */
#ifndef __MANAGER_H
#define __MANAGER_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <vector>
#include <string>
#include"user.h"
#include"exceptions.h"
using namespace std;

class Manager{
public:
	~Manager();
	Manager();
	void register_user();
	void Register();
	void connect_to_cli(int , char**);
	void disconnect();
	bool IsUser(string ,string );
	void Run();
	void LogIn();
	void compose_msg();
	User* find_user(string );
	void show_friends();
	void add_friend();
	void show_last_msgs();
	void show_last_msgs_from();
	bool is_friend(string user);
	void del_friend();
private:
	vector <User*> users;
	int sockfd;
	int newsockfd;
	User* online_user;
};

#endif
