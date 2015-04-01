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
#include "libpbm.h"

using namespace std;

int main(int argc, char *argv[]) {

  if( argc != 2 ) {
    fprintf(stderr, "Usage: %s img.pbm\n", argv[0]);
    return -1;
  }

  FILE *fd = fopen(argv[1], "r");
  if( !fd ) {
    fprintf(stderr, "Error loading file '%s'\n", argv[1]);
    return -1;
  }

  //Load image
  int W, H;
  bit **IMG;

  IMG = pbm_readpbm ( fd, &W, &H );

  int c4ant=H+1, c5ant=0;
  //For every column
  for(int x=0; x<W; x++) {

    //Compute the FKI 9 features
    int c1=0, c8=0, c9=0;
    float c2=0, c3=0, c6, c7;
    int c4=H+1, c5=0;
    for(int y=1; y<=H; y++) {
      if( IMG[y-1][x] ) { //Black pixel
	c1++;
	c2 += y;
	c3 += y*y;
	if( y<c4 ) c4=y;
	if( y>c5 ) c5=y;
      }
      if( y>1 && IMG[y-1][x] != IMG[y-2][x] ) c8++; 
    }
    
    c2 /= H;
    c3 /= H*H;

    for(int y=c4+1; y<c5; y++)
      if( IMG[y-1][x] ) //Black pixel
	c9++;
    
    c6=H+1; c7=0;
    if( x+1 < W ) {
      for(int y=1; y<=H; y++) {
	if( IMG[y-1][x+1] ) { //Black pixel
	  if( y<c6 ) c6=y;
	  if( y>c7 ) c7=y;
	}
      }
    }
    c6 = (c6 - c4ant)/2;
    c7 = (c7 - c5ant)/2;
    
    printf("%d %g %g %d %d %g %g %d %d\n", 
	   c1, c2, c3, c4, c5, c6, c7, c8, c9);
    
    c4ant = c4;
    c5ant=c5;
  }

  return 0;
}
