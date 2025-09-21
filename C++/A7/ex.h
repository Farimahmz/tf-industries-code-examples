#include <iostream>
using namespace std;

class Ex {
public:
  void login_error() { cout <<"You Can Not Login." << endl; }
  void log_error() { cout <<"You Are Not Login." << endl; }
  void usr_pwd_error() { cout << "Invalid Username Or Password." << endl; }
  void user_error() { cout << "This Username Is Already Existed." << endl; }
  void command_error() { cout << "Command Not Found." << endl; }
  void input_error(){cout << "Invalid Input." << endl;}
  void fire_error(){ cout << "Only Manager Can Fire!" << endl;}
  void reg_error(){cout<<"Only Admin Can Register."<<endl;}
};