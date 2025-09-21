#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>
#include "project.cpp"
using namespace std;

class Input{
public:
  Input(vector<string> v) : in(v) {}
  vector<string> get_input() { return in; }
  int inputs();
  void check_input(User& u);
private:
  vector<string> in;
  bool login;
};
void show(string s);