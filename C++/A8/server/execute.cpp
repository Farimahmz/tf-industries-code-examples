#include"execute.h"

void Execute::connect_to_server(int argc , char *argv[])
{
    	int portno, n;
        struct sockaddr_in serv_addr;
        struct hostent *server;
        char buffer[256];
        if (argc < 3) {
                fprintf(stderr,"usage %s hostname port\n", argv[0]);
                exit(0);
        }
        portno = atoi(argv[2]);
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd < 0)
                cout<<"ERROR opening socket"<<endl;
        server = gethostbyname(argv[1]);
        if (server == NULL) {
                fprintf(stderr,"ERROR, no such host\n");
                exit(0);
        }
        bzero((char *) &serv_addr, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        bcopy((char *)server->h_addr,
        (char *)&serv_addr.sin_addr.s_addr,
        server->h_length);
        serv_addr.sin_port = htons(portno);
        if(connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)))
		cout<<"Error connecting"<<endl;

}

////////////*****************

void Execute::disconnect()
{
	close(sockfd);
}

/////////////***************

void Execute::print_instruction()
{
	system("clear");
	cout<<"Instructions:"<<endl;
	cout<<"for adding new friend to your addlist please press: '0'"<<endl;
	cout<<"for composing new message please press number: '2'"<<endl;	
	cout<<"for seeing last messages from  your friends please press: '1'"<<endl;
	cout<<"for seeing last messages from one of your friends please type: '3'"<<endl; 
	cout<<"for exit please press: 'q' "<<endl;
	cout<<"for logout please press :'4'"<<endl;
	cout<<"for deleting a friend please press: 'd'"<<endl;
	if(isAdmin == true)
		cout<<"for registering please press : '5'"<<endl;
}

///////////////**************

void Execute::Register()
{
	int n;
	string user;
	string pass;
	char buffer[256];
	bzero(buffer,256);
	cout<<"please insert his/her username\n";
	cin>>user;
	cout<<"please insert his/her password\n";
	cin>>pass;
	n = write(sockfd,user.c_str(),strlen(user.c_str()));
	if(n < 0)
		cout<<"ERROR in writing\n";
	n = read(sockfd,buffer,255);
	if(n < 0)
		cout<<"ERROR in reading\n";
	n = write(sockfd,pass.c_str(),strlen(pass.c_str()));
	if(n < 0)
		cout<<"ERROR in writing\n";
	bzero(buffer,256);
	n = read(sockfd,buffer,255);
	string str = string(buffer);
	cout<<str<<endl;
	sleep(2);
}

////////////////**************

void Execute::compose_msg()
{
	int n;
	char buffer[256];
	string to;
	string contents;
	string answer;
	cout<<"enter your friend's username which you to send message to"<<endl;
	cin>>to;
	n = write(sockfd,to.c_str(),strlen(to.c_str()));
        if(n < 0)
                cout<<"ERROR writing to socket"<<endl;
	bzero(buffer,256);
	n = read(sockfd,buffer,255);
	if(n < 0)
		cout<<"ERROR reading from socket\n";
	answer = string(buffer);
	if(answer == "this user is not your friend")
	{
		system("clear");
		cout<<answer<<endl;
		sleep(2);
		return;
	}
	system("clear");
	cout<<"please insert your message"<<endl;
	//getline(cin,contents);
	cin>>contents;
	n = write(sockfd,contents.c_str(),strlen(contents.c_str()));
        if(n < 0)
                cout<<"ERROR writing to socket"<<endl;
	cout<<answer<<endl;
	sleep(1);
}

///////////////************

void Execute::LogIn()
{
	int n;
	string user;
	string pass;
	char buffer[256];
	while(1)
	{
		system("clear");
		cout<<"please enter username then press enter"<<endl;
		cin>>user;
	        n = write(sockfd,user.c_str(),strlen(user.c_str()));
	        if (n < 0)
	                 cout<<"ERROR writing to socket"<<endl;
		bzero(buffer,256);
		n = read(sockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in reading"<<endl;
	        cout<<"please enter password then press enter"<<endl;
	        cin>>pass;
		if(user == "admin" && pass == "3ecret")
			isAdmin = true;
		else 
			isAdmin = false;
	        n = write(sockfd,pass.c_str(),strlen(pass.c_str()));
	        if (n < 0)
	                 cout<<"ERROR writing to socket"<<endl;
	        bzero(buffer,256);
	        n = read(sockfd,buffer,255);
		if (n < 0)
			cout<<"ERROR reading from socket"<<endl;
		string str=string(buffer);
		cout<<str<<endl;
		sleep(1);
		if(str == "you are logged in")
		{
			  system("clear");
			  break; 
		}
		
	}
}

/////////////////*************

void Execute::add_friend()
{
	char buffer[256];
	int n;
	string frd;
	string str;
	cout<<"please enter his/her username who you want to add"<<endl;
	cin>>frd;
	bzero(buffer,256);
	n = read(sockfd,buffer,255);//vase ine ke ghati nakone
	if(n < 0)
		cout<<"ERROR in reading";
        n = write(sockfd,frd.c_str(),strlen(frd.c_str()));
        if (n < 0)
                 cout<<"ERROR writing to socket"<<endl;
        bzero(buffer,256);
        n = read(sockfd,buffer,255);
	string isAdded;
	isAdded = buffer;
        cout<<isAdded<<endl;
	sleep(2);
        if(n < 0)
                cout<<"Error reading from socket"<<endl;
	
}

/////////////**************

void Execute::del_friend()
{
	int n;
	char buffer[256];
	bzero(buffer,256);
	string user;
	string feedback;
	
	cout<<"please insert his/her username\n";
	cin>>user;
	n = write(sockfd,user.c_str(),strlen(user.c_str()));
	if(n < 0)
		cout<<"ERROR in writing\n";
	bzero(buffer,256);
	n = read(sockfd,buffer,255);
	if(n < 0)
		cout<<"ERROR in reading\n";
	feedback = string(buffer);
	cout<<feedback<<endl;
	sleep(2);
}

////////////****************

void Execute::show_msgs()
{
	while(1)
	{
		system("clear");
		int n;
		string sender;
		string content;
		char buffer[256];
		bzero(buffer,256);
		n = read(sockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in reading\n";
		sender = string(buffer);
		if(sender == "end")
			return ; 

		n = write(sockfd,"alaki",5);
		if(n < 0)
			cout<<"ERROR in writing\n";
		bzero(buffer,256);
		n = read(sockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in reading\n";
		content = string(buffer);
		n = write(sockfd,"alaki",5);
		if(n < 0)
			cout<<"ERROR in writing\n";
		cout<<sender<<" : "<<endl;
		cout<<content<<endl;
		sleep(2); 
	}
}

///////////****************

void Execute::show_msgs_from()
{
	int n;
	char buffer[256];
	cout<<"insert the person's username who you want to see his/her messages\n";
	string user;
	cin>>user;
	n = write(sockfd,user.c_str(),strlen(user.c_str()));
	if(n < 0)
		cout<<"ERROR in writing\n";
	bzero(buffer,256);
	n = read(sockfd,buffer,255);
	if(n < 0)
		cout<<"ERROR in reading\n";
	
	string feedback = string(buffer);
	cout<<feedback<<endl;
	sleep(1);
	if(feedback == "this user is not your friend")
		return;
	show_msgs();
}

///////////****************

void Execute::Run()
{
	LogIn();
	print_instruction();
	char ch;
	int n;
	char buffer[256];
	while(1)
	{
		print_instruction();	
		cin>>ch;
		
		if(ch == '5')
		{
			system("clear");
			sleep(1);
			n = write(sockfd,"Register",8);
			if(n < 0)
				cout<<"ERROR in writing\n";
			Register();
			
		}
		if(ch == '4')
		{
			n = write(sockfd,"LogOut",6);
			if(n < 0)
				cout<<"ERROR in writing"<<endl;
			system("clear");
			cout<<"you have logged out"<<endl;
			sleep(1);
			LogIn();	
			print_instruction();
			sleep(1);
			cin>>ch;
			//system("clear");
		}

		if(ch == 'q')
		{
			system("clear");
			n = write(sockfd,"exit",4);
                        if (n < 0)
                                cout<<"ERROR writing to socket"<<endl;
			return;
		}
		if(ch == '0')
		{
			system("clear");
			n = write(sockfd,"addFriend",9);
	                if (n < 0)
                 		cout<<"ERROR writing to socket"<<endl;
			add_friend();
		}
		if(ch == '2')
		{
			system("clear");
			n = write(sockfd,"compose",7);
			if(n < 0)
				cout<<"ERROR writing to socket"<<endl;	
			compose_msg();
		}	
		if(ch == '1')
		{
			system("clear");
			string str = "lastMsgs";

			n = write(sockfd,str.c_str(),strlen(str.c_str()));
			if(n < 0)
				cout<<"ERROR in writing";
			show_msgs();
		}
		if(ch == '3')
		{
			system("clear");
			string str = "lastMsgsFrom";
			n = write(sockfd,str.c_str(),strlen(str.c_str()));
			if(n < 0)
				cout<<"ERROR in writing";
			show_msgs_from();
			
			
		}
		if(ch == 'd')
		{
			system("clear");
			string str = "delAFriend";
			n = write(sockfd,str.c_str(),strlen(str.c_str()));
			if(n < 0)
				cout<<"ERROR in writing\n"; 
			bzero(buffer,256);
			n = read(sockfd,buffer,255);//alaki baraye in ke ghati nakone vase 2 ta write poshte ham
			if(n < 0)
				cout<<"ERROR in reading\n";
			del_friend();	
		}
	}
	
} 
