#include"manager.h"

int main(int argc, char *argv[])
{
	Manager mng;
	mng.connect_to_cli(argc,argv);
	mng.Run();
	mng.disconnect();	
}
