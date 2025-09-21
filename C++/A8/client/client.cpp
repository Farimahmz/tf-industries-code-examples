#include"execute.h"

int main(int argc, char *argv[])
{
	Execute exe;
	exe.connect_to_server(argc,argv);
	exe.Run();
	exe.disconnect();	
}
