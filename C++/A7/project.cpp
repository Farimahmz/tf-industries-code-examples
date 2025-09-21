#include "project.h"

void Project::add(string pn){
  string path = "root/";
  path.append(pn.c_str());
  mkdir(path.c_str(),S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH );
}
void Project::set_manager(User u){ manager->set_account(u.get_user(),u.get_passwd()); }
void Project::add_programmer(User u){
  programmer.push_back(u);
}
void Project::hire(string s){
  User u("","");
  string p;
  vector<User> v = u.read_user_from_file();
  for(int i=0 ; i<v.size() ; i++)
    if(v[i].get_user() == s)
      p = v[i].get_passwd();

  u.set_account(s,p);
  add_programmer(u);
}
void Project::remove(string s){
	for(int i=0 ; i<programmer.size() ; i++)
		if(programmer[i].get_user() == s)
			programmer.erase(programmer.begin()+i,programmer.begin()+i+1);
}
void Project::show_programmer(){
  for(int i=0 ; i<programmer.size() ; i++)
    cout << programmer[i].get_user() << " , ";
  cout << endl;
}
