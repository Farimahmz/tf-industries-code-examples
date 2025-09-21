#include"user.h"


void User::show_msgs(int newsockfd)
{
	char buffer[256];
	bzero(buffer,256);
	int n;
	string sender;
	cout<<"IN SHOW_MSGS\n";
	
	for(int i=0;i<inbox.size();i++)
	{
		sender = inbox[i]->get_from();
		n = write(newsockfd,inbox[i]->get_from().c_str(),strlen(inbox[i]->get_from().c_str()));
		if(n < 0)
			cout<<"ERROR in writing\n";
		n = read(newsockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in readin\n";
		cout<<buffer<<endl;
	n= write(newsockfd,inbox[i]->get_contents().c_str(),strlen(inbox[i]->get_contents().c_str()));
		if(n < 0)
			cout<<"ERROR in writing\n";
		bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in reading\n";
	}
	n = write(newsockfd,"end",3);
	if(n < 0)
		cout<<"ERROR in writing\n";

}

/////////////*************

int User::frd_idx(string frd)
{
	for(int i=0;i<friends.size();i++)
		if(friends[i]->get_user() == frd)
			return i;
}

////////////**************

void User::del_frd(string frd)
{
	int index = frd_idx(frd);
	cout<<"here\n";
	friends.erase(friends.begin()+index);
}

/////////////***************

void User::show_msgs_from(int newsockfd,string user)
{
	char buffer[256];
	bzero(buffer,256);
	int n;
	string sender;
	cout<<"IN SHOW_MSGS\n";
	
	for(int i=0;i<inbox.size();i++)
	{
		sender = inbox[i]->get_from();
		cout<<"sender "<<sender<<endl;
		cout<<"user "<<user<<endl;
		if(sender != user)
			continue;
		n = write(newsockfd,inbox[i]->get_from().c_str(),strlen(inbox[i]->get_from().c_str()));
		if(n < 0)
			cout<<"ERROR in writing\n";
		n = read(newsockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in readin\n";
		cout<<buffer<<endl;
		n = write(newsockfd,inbox[i]->get_contents().c_str(),strlen(inbox[i]->get_contents().c_str()));
		if(n < 0)
			cout<<"ERROR in writing\n";
		bzero(buffer,256);
		n = read(newsockfd,buffer,255);
		if(n < 0)
			cout<<"ERROR in reading\n";
	}
	n = write(newsockfd,"end",3);
	if(n < 0)
		cout<<"ERROR in writing\n";

}

////////////**************

/*bool User::is_friend(string user)
{
	for(int i=0;i<friends.size();i++)
		if(friends[i]->get_user == user)
			return true;
	return false;
}*/

////////////*************
User::~User()
{
	for(int i=0;i<inbox.size();i++)
	{
		delete inbox[i];
	}
}

