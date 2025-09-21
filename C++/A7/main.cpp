#include "input.cpp"
#include "command.cpp"
using namespace std;

int main(){
  string s;
  User u("","","");
  while(getline(cin,s)){
    Command c(s);
    vector<string> v = c.analyze();
    Input i(v);
    i.check_input(u);
  }
  return 0;
}
