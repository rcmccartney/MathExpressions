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
*/

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "libpgm.h"

using namespace std;

int main(int argc, char *argv[]) {

  if( argc < 3 || argc > 4 ) {
    fprintf(stderr, "Usage: %s img.pgm w_size [-vr]\n", argv[0]);
    return -1;
  }

  FILE *fd = fopen(argv[1], "r");
  if( !fd ) {
    fprintf(stderr, "Error loading file '%s'\n", argv[1]);
    return -1;
  }
  
  int NCols=atoi(argv[2]);
  if( NCols < 1 ) {
    fprintf(stderr, "Error: w_size must be a positive integer >= 1\n");
    return -1;    
  }
  if( NCols%2 == 0 ) {
    fprintf(stderr, "Warning: even number of columns! using %d instead\n", ++NCols);
  }
  NCols /= 2;

  bool vRep=false;
  if( argc == 4 ) {
    if( !strcmp(argv[3], "-vr") )
      vRep=true;
    else
      fprintf(stderr, "Warning: unrecognized option '%s' (ignored)\n", argv[3]);
  }

  //Load image
  int W, H;
  gray **IMG, maxval;

  IMG = pgm_readpgm ( fd, &W, &H, &maxval );

  //For every column
  for(int i=0; i<W; i++) {

    if( !vRep ) {
      //NO vertical reposition
      for(int k=0; k<H; k++)
	for(int j=i-NCols; j<=i+NCols; j++) {
	  if( j>=0 && j<W )
	    printf(" %d", (int)IMG[k][j]);
	  else
	    printf(" 255"); //Background
	}
  
      printf("\n");
    }
    else { //With vertical reposition

      //Compute center of gravity
      int np=0, vcen=0;
      for(int k=0; k<H; k++)
	for(int j=i-NCols; j<=i+NCols; j++)
	  if( j>=0 && j<W && (int)IMG[k][j] < 255 ) { //Foreground pixel
	    vcen += k;
	    np++;
	  }
      
      if( np==0 ) //Prevent errors in empty slices
	vcen = H/2;
      else
	vcen /= np; //Vertical centroid

      //printf("Vertical centroid: %d (cen=%d)\n", vcen, H/2);

      //Print windows
      for(int k=0; k<H; k++) {
	for(int j=i-NCols; j<=i+NCols; j++) {
	  int krp = k + (vcen - H/2);
	  if( j>=0 && j<W && krp>=0 && krp <H )
	    printf(" %d", (int)IMG[krp][j]);
	  else
	    printf(" 255"); //Background
	}
      }
      printf("\n");
      
    }

  }//end for every column

  return 0;
}
