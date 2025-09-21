#include <iostream>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <unistd.h>
#include "user.cpp"

class Project{
public:
  Project(string n) : name(n) {}
  string get_name() { return name; }
  User* get_manager() { return manager; }
  void set_manager();
  void add(string pn);
  void set_manager(User u);
  void add_programmer(User u);
  void hire(string s);
  void remove(string s);
  void show_programmer();
private:
  string name;
  string direction;
  User* manager;
  vector<User> programmer;
};
