#include "command.h"

vector<string> Command::analyze(){
	vector<string> v;
	for (int i=0 ; i<cmd.length() ; i++)
		if (cmd[i] == ' '){
			v.push_back(cmd.substr(0,i));
			cmd.erase(0,i+1);
			i = 0;
		}
	v.push_back(cmd.substr(0));
	return v;
}