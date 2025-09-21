#include "user.h"

vector<User> User::read_user_from_file(){
  vector<User> uu;
  ifstream in;
  in.open("root/user.data");
  string s,t,r;
  while(in >> s >> t >> r){
    User u(s,t,r);
    uu.push_back(u);
  }
  in.close();
  uu.push_back(admin);
  return uu;
}
void User::check_account(){
  vector<User> u = read_user_from_file();
  bool status = false;
  for(int i=0 ; i<u.size() ; i++)
    if( ( usr == u[i].usr ) && ( pwd == u[i].pwd ) ){
      status = true;
    }
    try{
      if(!status)
	throw Ex();

      set_log(true);
      cout << "Welcome " << usr << "." << endl;

    }catch(Ex e){
      e.usr_pwd_error();
    }

}
void User::login(){
  vector<User> uu = read_user_from_file();
  check_account();
}
void User::set_account(string s , string t){
  ifstream in;
  in.open("root/user.data");
  string m,n,p,r;
  while(in >> m >> n >> p){
    if(m == s)
      r = p;
  }
  in.close();
  usr = s;
  pwd = t;
  role = r;
}
void User::set(string s , string t){
  usr = s;
  pwd = t;
}
void User::reg(string s,string t,string r){
  vector<User> uu = read_user_from_file();
  for(int i=0 ; i<uu.size() ; i++)
    try{if(uu[i].get_user() == s)
      throw Ex();}catch(Ex e){e.user_error();}

  fstream i;
  i.open("root/user.data",fstream::in | fstream::out | fstream::app);
  i << s << " " << t << " " << r << endl;
  i.close();
}
const User admin("admin","s3cret","admin");