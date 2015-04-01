/*Copyright 2000-2009 Moisés Pastor, Alejandro H. Toselli

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
*/

#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <cstring>
#include <cstdlib>
#include <endian.h>
#include <unistd.h>
#include "imageClass.h"
#include "features.h"

using namespace std;

void usage(char * nomProg){
  cerr << "Usage: "<< nomProg << " options" << endl;
  cerr << "      options:" << endl;
  cerr << "             -i inputfile      (by default stdin)" << endl;
  cerr << "             -o outputfile     (by default stdout)" << endl;
  cerr << "             -t transcription  (by default NULL)" << endl;
  cerr << "             -c numberOfCells  (by default 20)" << endl;
  cerr << "             -V <num:float>    overlapping vertical factor of cells (def. 2.0) "<< endl;
  cerr << "             -O <num:float>    overlapping horizontal factor (def. 2.0)"<<endl;
  cerr << "             -F <num:float>    scaling factor of frecuency (def. 1.0)"<<endl;
  cerr << "             -H                HTK output format (def. PRHLT format)" << endl;

  cerr << "             -v                verbosityLevel (by default 0)" << endl;
}

int main (int argc, char ** argv){
  string inFileName,outFileName;
  bool HTK_format=false;
  int option;
  ifstream ifd;
  ofstream ofd;
  ofstream xfd;
  bool verbosity=false;
  char * ortTrans=0;
  int  nCells=20;
  float scalingFrec=1;
  int vertOverlapping=2, horizOverlapping=2;

  /*******/
  while ((option=getopt(argc,argv,"h:i:o:t:c:V:O:F:Hv"))!=-1)
    switch (option)  {
    case 'i':
      inFileName=optarg;
      break;
    case 'o':
      outFileName=optarg;
      break;
    case 't':
      ortTrans=new char [strlen(optarg)+1];
      strcpy(ortTrans,optarg);
      break;
    case 'v':
      verbosity=true;
      break;
    case 'c':
      nCells=atoi(optarg);
      break;
    case 'V':
      vertOverlapping=atof(optarg);
      break;
    case 'O':
      horizOverlapping=atof(optarg);
      break;
    case 'F':
      scalingFrec=atof(optarg);
      break;
    case 'H':
      HTK_format=true;
      break;
    case 'h':
    default:
      usage(argv[0]);
      return(-1);
    }
   
  imageClass image;

  if (!image.read(inFileName)) return -1;

  float **seqFctrR;
  FeatPRHLT method;
  
  method.resetNumberOfVectors();

  //cerr << scalingFrec << endl;
  method.setExtractionParameters(nCells,vertOverlapping,horizOverlapping,scalingFrec,'g');
  seqFctrR=method.getSeqFeatPRHLTOnDelimitedImage(image,0,image.rows-1);
  
  ostream * ofdp=&cout;
 
  int nVectors=method.getNumberOfVectors();

  if (HTK_format){
    ofstream fich_out;
    
    if (outFileName.size()!=0){ // salida estandard 
      fich_out.open (outFileName.c_str(), ios::out | ios::binary);
      ofdp=&fich_out;
    } else 
      fich_out.open ("/dev/stdout", ios::out | ios::binary);
    
    //Num of samples
    long int nVec=htobe32(nVectors); //to big-endian
    fich_out.write((char*) &(nVec),4);
    
    //period sample does'nt mather
    long int sampPeriod=1;
    sampPeriod=htobe32(sampPeriod); //to big-endian
    fich_out.write((char*) &(sampPeriod),4);
    
    //sampSize
    short int  sampSize=htobe16((nCells)*3*4);
    fich_out.write((char*) &(sampSize), 2);

    //parmKind=9;
    short int parmKind=htobe16((short int) 6);
    fich_out.write((char*) &(parmKind), 2);

    for (int i=0; i<nVectors; i++){
      //Grey level average feature    
      for (int j=0; j< nCells; j++){
	float g = seqFctrR[i][j];
	fich_out.write(((char*) &g)+3, sizeof(char) );
	fich_out.write(((char*) &g)+2, sizeof(char) );
	fich_out.write(((char*) &g)+1, sizeof(char) );
	fich_out.write((char*) &g, sizeof(char) );
      }

      // first derivative
      for (int j=nCells; j< nCells * 2; j++){
	float fd=seqFctrR[i][j];
	fich_out.write(((char*) &fd)+3, sizeof(char) );
	fich_out.write(((char*) &fd)+2, sizeof(char) );
	fich_out.write(((char*) &fd)+1, sizeof(char) );
	fich_out.write((char*) &fd, sizeof(char) );
      }
            
      // second derivative
      for (int j=nCells*2; j< nCells * 3 ; j++){
	float sd=seqFctrR[i][j];
	fich_out.write(((char*) &sd)+3, sizeof(char) );
	fich_out.write(((char*) &sd)+2, sizeof(char) );
	fich_out.write(((char*) &sd)+1, sizeof(char) );
	fich_out.write((char*) &sd, sizeof(char) );
      }
    }

    fich_out.close();
  } else { //ATROS format

    ofstream fich_out;
    if (outFileName.size()!=0){ // estandar output
      fich_out.open(outFileName.c_str());
      ofdp=&fich_out;
    }
    //head
    if (outFileName.size()!=0)
      *ofdp <<"Name        " << outFileName << endl;
    else 
      *ofdp <<"Name        stdout" << endl;
    if (ortTrans)
      *ofdp <<"OrtTrans    " << ortTrans << endl;

    *ofdp <<"NumParam    " << nCells*3 << endl;
    *ofdp <<"NumVect     " << nVectors << endl;
    *ofdp <<"Data" << endl;
    
    //features
    ofdp->precision (6);
    for (int i=0; i<nVectors; i++){    
      //Grey level average feature    
      for (int j=0; j< nCells; j++)
	*ofdp <<scientific<<scientific<<seqFctrR[i][j] << " ";
            
      // first derivative
      for (int j=nCells; j< nCells * 2; j++)
	*ofdp <<scientific<<scientific<<seqFctrR[i][j] << " ";
            
      // second derivative
      for (int j=nCells*2; j< nCells * 3 ; j++)
	*ofdp <<scientific<<scientific<<seqFctrR[i][j] << " ";
      
      *ofdp<< endl;
    }
    fich_out.close();
  }


 delete seqFctrR;
 return 0;
}
