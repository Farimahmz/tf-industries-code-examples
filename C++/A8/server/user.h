#ifndef __USER_H
#define __USER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include"message.h"

class User{
public:
	~User();
	User(string user ,string pass ) : username(user) ,password(pass) {}
	string get_user() { return username; }
	string get_pass() { return password; }
	void add_friend( User* frd) { friends.push_back(frd); }
	void add_msg(msg* m) { inbox.push_back(m); } 
        void  show_last_msgs();
	void show_last_msgs_from(string );
	void show_msgs(int );
	void show_msgs_from(int ,string);		
	vector <User*> get_friends() { return friends; }
	int frd_idx(string );
	void del_frd(string );
	void show_frds();
	bool is_friend(string );
private:
	vector <msg*> inbox;
	string username;
	string password;
	vector <User*> friends;
};

#endif
