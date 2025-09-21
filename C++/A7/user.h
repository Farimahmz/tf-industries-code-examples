#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include "ex.h"
using namespace std;

class User{
public:
  User(string u , string p ) : usr(u) , pwd(p) , log(false) {}
  User(string u , string p , string r) : usr(u) , pwd(p) , role(r) , log(false) {}
  void set_false();
  string get_user() { return usr; }
  string get_passwd() { return pwd; }
  string get_role() { return role;}
  bool get_log() { return log; }
  bool set_log(bool b) { log = b; }
  vector<User> read_user_from_file();
  void check_account();
  void login();
  void set_account(string s , string t);
  void set(string s , string t);
  void set_role(string r) { role = r; }
  void reg(string s,string t,string r);
private:
  string usr;
  string pwd;
  string role;
  bool log;
};
extern const User admin;