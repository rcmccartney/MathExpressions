/*Copyright 2014 Francisco Alvaro

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

This file is a modification of the original online features software
covered by the following copyright and permission notice:

*/
/*
    Copyright (C) 2006,2007 Moisés Pastor <mpastorg@dsic.upv.es>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <iostream>
#include <istream>
#include <fstream>
#include <vector>
#include <string>
#include "online.h"
#include "read.h"
#include "features.h"

using namespace std;

void usage (char *f) {
  cerr << endl;
  cerr << "Usage: " << f << " [-o] [-f #int] [-i file] [-v #int] [-w #int] [<file> (def. stdin)]" << endl;
  cerr << endl;
  cerr << "  -f #   Specify the context window size for offline features" << endl;
  cerr << "         computation (def. 0 = no offline features)" << endl;
  cerr << "  -i out Save the rendered image in file 'out' (PGM)" << endl;
  cerr << "  -v #   Specify the height size for image renderization (def. 40)" << endl;
  cerr << "  -w #   Specify the max width size for image renderization (def. 200)" << endl;
  cerr << "  -o     Save output to disk (def. stdout)." << endl;
  cerr << endl;
  cerr <<"NOTE: input file must be in MOTOROLA format." << endl << endl;
  cerr << "Feature Vector Scheme:" << endl;
  cerr << "         < X Y Dx Dy Ax Ay K off(1x1) off(1x2) ... off(fxf) >" << endl << endl;
  cerr << "   where:" << endl;
  cerr << "          X: normalized coord x" << endl;
  cerr << "          Y: normalized coord y" << endl;
  cerr << "         Dx: first normalized derivative of X" << endl;
  cerr << "         Dy: first normalized derivative of Y" << endl;
  cerr << "         Ax: second derivative of X" << endl;
  cerr << "         Ay: second derivative of Y" << endl;
  cerr << "          K: curvature" << endl;
  cerr << "   Off(fxf): sequence of the fxf context window centered" << endl;
  cerr << "             in (x,y) in offline representation" << endl << endl;
  exit(-1);
}


int main(int argc, char ** argv) {
	
  char *prog;
  if ((prog=rindex(argv[0],'/'))) prog+=1;
  else prog=argv[0];

  if( argc==1 ) {
    usage(prog);
    return -1;
  }
  
  string filename;
  int opt;
  
  int OFFS=0;
  bool OutFile=false;
  int mh =  40;
  int mw = 200;
  char *out = NULL;
  
  while ((opt=getopt(argc,argv,"f:i:ov:w:")) != -1) {
    switch (opt) {
    case 0: usage(prog);
    case 'o': OutFile=true; break;
    case 'f': OFFS=atoi(optarg); break;
    case 'i': out=optarg; break;
    case 'v': mh=atoi(optarg); break;
    case 'w': mw=atoi(optarg); break;
    default:  cerr << "ERR: invalid option " << char(opt) << endl;
    case 'h': usage(prog);
    }
  }
  
  if (optind<argc) filename.append(argv[optind]);
  ifstream *fd=NULL, aux_fd;
  if (filename=="") filename.append("stdin");
  else {
    aux_fd.open(filename.c_str());
    if (aux_fd.fail()) {
      cerr << "ERR: file \"" << filename.c_str();
      cerr << "\" can't be opened\n" << endl;
      exit(-1);
    }
    fd=&aux_fd;
  }

  sentence * sample;
  if( !read_file_moto((fd==NULL?cin:*fd),&sample) ) {
    cerr << "ERROR: reading input sample" << endl;
    return -1;
  }

  // Remove repeated points
  sentence * no_rep=(*sample).remove_rep_points();	
  // Median filter
  sentence * smo_stks=(*no_rep).smooth_strokes();

  //Compute features
  sentenceF feat;
  feat.calculate_features(*smo_stks,OFFS,mh,mw,out);


  char *fname = new char[filename.size()+4+1]; //4 = len(.fea)
  sprintf(fname,"%s.fea",filename.c_str());
  
  ostream *fdo;
  if (OutFile) fdo=new ofstream(fname);
  else fdo=&cout;
  
  // Features header
  *fdo << "Name       " << fname << endl;
  *fdo << "Class      " << feat.transcrip << endl;
  *fdo << "NumVect    " << feat.n_frames << endl;
  *fdo << "NumParam   " << feat.frames[0].get_fr_dim() << endl;
  *fdo << "Data" << endl;
  feat.print(*fdo);
  
  if (OutFile) delete fdo;
  
  //Free memory
  delete sample;
  delete no_rep;
  delete smo_stks;
  delete [] fname;
    
  if (fd!=NULL) fd->close();

  return 0;
}
