#include <iostream>
#include <string>
#include <vector>
using namespace std;

class Command{
public:
	Command(string c) : cmd(c) {}
	vector<string> analyze ();
private:
	string cmd;
};