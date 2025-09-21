#include"manager.h"

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

Manager::~Manager()
{
	for(int i=0;i<users.size();i++)
		delete users[i];	
}
Manager::Manager()
{
	User* admin = new User("admin","3ecret");
	users.push_back(admin);
}
void Manager::connect_to_cli(int argc , char *argv[])
{
     int  portno;
     socklen_t clilen;
     char buffer[256];
     struct sockaddr_in serv_addr, cli_addr;
     int n;
     if (argc < 2) {
         fprintf(stderr,"ERROR, no port provided\n");
         exit(1);
     }
     sockfd = socket(AF_INET, SOCK_STREAM, 0);
     if (sockfd < 0)
        cout<<"ERROR opening socket"<<endl;
     bzero((char *) &serv_addr, sizeof(serv_addr));
     portno = atoi(argv[1]);
     serv_addr.sin_family = AF_INET;
     serv_addr.sin_addr.s_addr = INADDR_ANY;
     serv_addr.sin_port = htons(portno);
     if (bind(sockfd, (struct sockaddr *) &serv_addr,
              sizeof(serv_addr)) < 0)
           error("ERROR on binding");
		
     listen(sockfd,5);
     clilen = sizeof(cli_addr);
     newsockfd = accept(sockfd,
                 (struct sockaddr *) &cli_addr,
                 &clilen);
     if (newsockfd < 0)
          error("ERROR on accept");
	
}

//////////////*************

User* Manager::find_user(string user)
{	
	cout<<"user tu find_user :"<<user<<endl;
	for(int i=0;i<users.size();i++)
		if(users[i]->get_user() == user)
		{
		       	return users[i];
		}

	return NULL;	
}

////////////////*************

bool Manager::IsUser(string user,string pass)
{

	for(int i=0;i<users.size();i++)
	{
		if((user == users[i]->get_user()) && (users[i]->get_pass() == pass ))
			return true;	
	}
	return false;	
}
////////////////*****************

void Manager::disconnect()
{
	 close(newsockfd);
	 close(sockfd);
}
//////////////*******************

void Manager::Register()
{
	string user,pass;
	int n;
	char buffer[256];
	bzero(buffer,256);
	n = read(newsockfd,buffer,255);
	user = string(buffer);
	if(n < 0)
		cout<<"ERROR in reading\n";
	n = write(newsockfd,"alaki",5);
	if(n < 0)
		cout<<"ERROR in writing";
	bzero(buffer,256);
	n = read(newsockfd,buffer,255);
	if(n < 0)
		cout<<"ERROR in reading\n";
	pass = string(buffer);
	cout<<"user is: "<<user<<endl;
	cout<<"pass is: "<<pass<<endl;
	if(find_user(user) != NULL)
	{
		string str = "this user already exists";
		cout<<str<<endl;
		n = write(newsockfd,str.c_str(),strlen(str.c_str()));
		if(n < 0)
			error("ERROR in writing");
		throw has_user();
	}
	string str = "user registered successfully";
	n = write(newsockfd,str.c_str(),strlen(str.c_str()));
	if(n < 0)
		error("ERROR in writing");
	cout<<"after find user in register\n";
	User* u = new User(user,pass);
	users.push_back(u);
	cout<<"user.size "<<users.size()<<endl;
	
}

//////////////********************

void Manager::Run()
{
	//
	int n;
	string user,pass;
	char buffer[256];
	bzero(buffer,256);
	LogIn();
	
	while(1)
	{
		bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		 if (n < 0)
	                 cout<<"ERROR in reading from socket"<<endl;
		string command = string(buffer);
		cout<<"ham aknun be daste ma recde: "<<command<<endl;
	
		if(command == "Register")
		{
			cout<<"BEFORE REGISTE\n";	
					
			try{
				Register();	
			}
			catch(has_user){
			}
	
		}
		if(command == "addFriend")
		{	
			n = write(newsockfd,"alaki",5);
			if(n < 0)
				error("ERROR in writing");

			
				add_friend();	
					
		}
		if(command == "compose")
		{
			try{
			compose_msg();
			}
			catch(not_friend){	
			}
		//	online_user->show_msgs();	
		}
		if(command == "exit")
		 {
			return ;

		}
		if(command == "LogOut")
		{
	
			//online_user->show_msgs();
			LogIn();
		}
		if(command == "lastMsgs")
		{
			online_user->show_msgs(newsockfd);
		}
		if(command == "lastMsgsFrom")
		{
			cout<<"LAst Msgs From\n";
			bzero(buffer,256);
			n = read(newsockfd,buffer,255);
			if(n < 0)
				error("ERROR in reading");
			user = string(buffer);
			cout<<"FROM \n";
			cout<<user<<endl;
			if(!is_friend(user))
			{
				string str = "this user is not your friend";
				n = write(newsockfd,str.c_str(),strlen(str.c_str()));
				if(n < 0)
					error("ERROR in writing");
				continue;
			} 
			string str = "messages from her/him : ";
			n = write(newsockfd,str.c_str(),strlen(str.c_str()));
			if(n < 0)
				error("ERROR in writing");
			
			online_user->show_msgs_from(newsockfd,user);
		}
		if(command == "delAFriend")
		{
			n = write(newsockfd,"alaki",5);
			if(n < 0)
				error("ERROR in writing");
			try{
				del_friend();
			}
			catch(not_friend){
				string str = "this user wasn't your friend";
				n = write(newsockfd,str.c_str(),strlen(str.c_str()));
				if(n < 0)
					error("ERROR in writing");
			}
			
			
		}

	}
	
}
/////////////////*******************

///////////////********************

void Manager::compose_msg()
{
	char buffer[256];
	bzero(buffer,256);
	string contents;
        int n= read(newsockfd,buffer,255);
        if (n < 0)
                error("ERROR reading from socket");
	string to = string(buffer);
	if(!is_friend(to))
	{
		cout<<"not friend"<<endl;
		n = write(newsockfd,"this user is not your friend",28);
		throw not_friend();
		return;
	}
	n = write(newsockfd,"your message sent successfully",30);
	if(n < 0)
		error("ERROR writing");
	bzero(buffer,256);
	n = read(newsockfd,buffer,255);
	if(n < 0)
		error("ERROR reading from socket");
	contents = string(buffer);
	msg* message = new msg(contents, online_user->get_user(),to);
	cout<<"mohtava: "<<message->get_contents()<<endl;
        User* dest = find_user(to);
        dest -> add_msg( message );
}

////////////////*******************

void Manager::add_friend()
{
	char buffer[256];
	bzero(buffer,256);
	string frd;
	int n= read(newsockfd,buffer,255);
        if (n < 0)
                error("ERROR reading from socket");
	frd = string(buffer);
	cout<<frd<<endl;
	User* f = find_user(frd);
	cout<<"bade find_user"<<endl;
	if(f == NULL || is_friend(frd))
	{
		cout<<"NULL bud"<<endl;
		string str="adding faild";
		n=write(newsockfd,str.c_str(),strlen(str.c_str()));
		 if(n < 0)
                        error("ERROR in writing");
		return;
	}

	online_user->add_friend(f);
	string str="user added successfully";
	cout<<str;
	 n=write(newsockfd,str.c_str(),strlen(str.c_str()));
        if(n < 0)
     	          error("ERROR in writing");
	show_friends();

}

///////////////////*************

void Manager::del_friend()
{
	int n;
	int index;
	char buffer[256];
	bzero(buffer,256);
	string frd;
	n = read(newsockfd,buffer,255);
	if(n < 0)
		error("ERROR in readin");
	frd = string(buffer);
	
	online_user->show_frds();
	if(!is_friend(frd))
		throw not_friend();
	string str = "this user deleted from your addlist successfully";
	online_user->del_frd(frd);
	n = write(newsockfd,str.c_str(),strlen(str.c_str()));
	if(n < 0)
		error("ERROR in writing");
	

}
///////////////////**************

void User::show_frds()
{
	cout<<"friends: "<<endl;
	for(int i=0;i<friends.size();i++)
		cout<<friends[i]->get_user()<<endl;
}

//////////////////*************
void Manager::show_friends()
{
	vector <User*> frds;
	frds = online_user->get_friends();
	for(int i=0 ; i< frds.size() ; i++)
		cout<<frds[i]->get_user();

}

///////////***************

bool Manager::is_friend(string user)
{
	vector <User*> frds = online_user -> get_friends();
	for(int i=0;i < frds.size();i++)
	{
		if(frds[i]->get_user() == user)
			return true;
	}
	return false;

}

//////////////*************

////////////////**************
 
void Manager::LogIn()
{
	
	int n;
        string user,pass;
        char buffer[256];
        bzero(buffer,256);
	while(1)
        {
                n=read(newsockfd,buffer,255);
                if(n < 0)
                        error("ERROR in reading from socket");
                n = write(newsockfd,"alaki",5);
                if(n < 0)
                        error("ERROR in writing");
                user = string(buffer);
                cout<<"user is: "<<user<<endl;
                bzero(buffer,256);
                n=read(newsockfd,buffer,255);
                if(n < 0)
                        error("Error in reading from socket");
                pass = string(buffer);
                cout<<"pass is "<<pass<<endl;
		         if(IsUser(user,pass))
	                {
				
				cout<<"USER\n";
	                        online_user = find_user(user);
	                        string str= "you are logged in";
	                        n = write(newsockfd,str.c_str(),strlen(str.c_str()));
                     	   if(n < 0)
                        	        error("ERROR in writing");
			cout<<"LOGIN AND MSGS: ";

			//online_user->show_msgs();
			cout<<"TOROKHODA\n";
			//online_user->show_msgs();
                        break;
                }
		string str = "Invalid user or pass";
		
		n = write(newsockfd,str.c_str(),strlen(str.c_str()));
		if(n < 0)
			error("ERROR in writing");

}
}
