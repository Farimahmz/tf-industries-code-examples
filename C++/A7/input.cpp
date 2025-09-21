#include "input.h"

void show(string s){
  string p = "root/";
  p.append(s.c_str());
  const char *q;
  q = p.c_str();
  DIR* dir = opendir(q);
  if(dir == NULL)
    cout << "error!" <<endl;
  dirent* de;
  while((de = readdir(dir))){
    cout << de->d_name << " " ;
  }
  cout << endl;
}
int Input::inputs(){
	if(in[0] == "login")
		return 1;
	if(in[0] == "register")
		return 2;
	if(in[0] == "logout")
		return 3;
	if(in[0] == "add")
		return 4;
	if(in[0] == "hire")
		return 5;
	if(in[0] == "fire")
		return 6;
	if(in[0] == "commit")
		return 7;
	if(in[0] == "release")
		return 8;
	if(in[0] == "revert")
		return 9;
	if(in[0] == "show")
		return 10;
	if(in[0] == "exit")
		return 11;
}
void Input::check_input(User& u){
  int i = inputs();
  switch(i){
  case 1:{ //login
    try{if(u.get_log())
      throw Ex();
    if(in[1] == "admin"){
      u.set_account("admin","s3cret");
      u.set_role("admin");
    }
    u.set_account(in[1],in[2]);
    u.login();}catch(Ex e){e.login_error();}
  }
  break;
  case 2:{
    try{
      if(!u.get_log())
	throw Ex();
      
      try{
	if(in[1] != "admin" && in[1] != "user")
	  throw Ex();
	
	
	if(u.get_user() == "admin"){
	    u.set("admin","s3cret");
	    u.set_role("admin");
	  }
	  
	  
	try{
	  if(u.get_role() != "admin")
	    throw Ex();
	  
	  
	  u.reg(in[2],in[3],in[1]);
	  
	}catch(Ex e){e.reg_error();}
	
      }catch(Ex e){e.input_error();}
      
    }catch(Ex e){e.login_error();}
  }
  break;
  case 3:{ //logout
    try{if(!u.get_log())
      throw Ex();
      cout <<  "Waiting for next user ..." << endl;
    u.set_log(false);
    }catch(Ex e){e.login_error();}

  }
    break;
  case 4:{ //add --> naghes
    try{if(!u.get_log())
      throw Ex();
      Project p(in[1]);
    p.add(in[1]);
    p.set_manager(u);
    }catch(Ex e){e.login_error();}

  }
    break;
  case 5:{ //hire
    try{if(!u.get_log())
      throw Ex();
      Project p(in[1]);
    if(p.get_manager()->get_user() != u.get_user())
      break;
    p.hire(in[2]);
    }catch(Ex e){e.login_error();}

  }
    break;
  case 6:{ //fire
    try{if(!u.get_log())
      throw Ex();
    }catch(Ex e){e.login_error();} 
    Project p(in[1]);
    try{if(p.get_manager()->get_user() != u.get_user())
      throw Ex();
      p.remove(in[2]);}catch(Ex e){e.fire_error();}
  }
    break;
  case 7:{
    try{if(!u.get_log())
      throw Ex();}catch(Ex e){e.login_error();}
  }
    break;
  case 8:{
    try{if(!u.get_log())
      throw Ex();}catch(Ex e){e.login_error();}
  }
    break;
  case 9:{
    try{if(!u.get_log())
      throw Ex();}catch(Ex e){e.login_error();}
  }
    break;
  case 10:{ //show
    try{if(!u.get_log())
      throw Ex();

    if(in[2] == "-a" || in[2] == "-d" || in[2] == "-v"){
      Project p(in[1]);
      if(in[2] == "-a"){
	cout << "Manager: " << p.get_manager() << endl;
      }
      if(in[2] == "-d"){
	cout << "Programmer: ";
	p.show_programmer();
      }
      if(in[2] == "-v"){}
      if(in[3] == "-a"){
	cout << "Manager: " << p.get_manager() << endl;
      }
      if(in[3] == "-d"){
	cout << "Programmer: ";
	p.show_programmer();
      }
      if(in[3] == "-v"){}
      if(in[4] == "-a"){
	cout << "Manager: " << p.get_manager() << endl;
      }
      if(in[4] == "-d"){
	cout << "Programmer: ";
	p.show_programmer();
      }
      if(in[4] == "-v"){}
      
    }
      show(in[2]);
    }catch(Ex e){e.log_error();}
    
  }
    break;
  case 11:{
    exit(1);
  }
  break;
  default:
      try{
	if(1)
	  throw Ex();
      }catch(Ex e) { e.command_error(); }
  }
}