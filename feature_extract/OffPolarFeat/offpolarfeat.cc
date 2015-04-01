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
#include "polarhist.h"

using namespace std;

int main(int argc, char *argv[]) {

  if( argc < 5 || argc > 6 ) {
    fprintf(stderr, "Usage: %s image.pgm rad dis ang [-vr]\n", argv[0]);
    return -1;
  }

  FILE *fd = fopen(argv[1], "r");
  if( !fd ) {
    fprintf(stderr, "Error loading file '%s'\n", argv[1]);
    return -1;
  }

  int R, D, A;
  R = atoi(argv[2]);
  if( R<1 ) {
    fprintf(stderr, "Error: 'rad' must be integer >= 1\n");
    return -1;
  }
  D = atoi(argv[3]);
  if( D<1 ) {
    fprintf(stderr, "Error: 'dis' must be integer >= 1\n");
    return -1;
  }
  A = atoi(argv[4]);
  if( A<1 ) {
    fprintf(stderr, "Error: 'ang' must be integer >= 1\n");
    return -1;
  }
  bool vr=false;
  if( argc == 6 ) {
    if( !strcmp(argv[5], "-vr") )
      vr=true;
    else
      fprintf(stderr, "Warning: unrecognized option '%s' (ignored)\n", argv[5]);
  }
  
  //Load image
  int W, H;
  gray **IMG, maxval;
  IMG = pgm_readpgm ( fd, &W, &H, &maxval );
  fclose(fd);

  polar_feat PolarFeat(R, D, A, vr);

  //Get polar features for every column
  for(int i=0; i<W; i++)
    PolarFeat.getPointFeat(IMG, W, H, maxval, i);
  
  return 0;
}
