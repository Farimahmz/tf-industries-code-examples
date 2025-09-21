#ifndef __MESSAGE_H
#define __MESSAGE_H

#include<iostream>
#include<vector>
#include<string>
#include<fstream>
using namespace std;

class msg{
public:
	string get_contents() { return contents; }
	string get_from() { return from; }
	msg(string c,string f,string t) 
	{
		cout<<"C "<<c<<endl;
		cout<<"F "<<f<<endl;
		contents = c;
		from = f;
		to = t;
	}
	void set_contents( string c ) { contents = c; }
	void set_SD(string f, string t) { from = f , to = t; }
private:
	string contents;
        vector <msg*> replies;
	string from;
	string to;
	fstream fp;
};

#endif
