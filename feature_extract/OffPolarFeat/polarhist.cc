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

#include "polarhist.h"
#include <cstdio>
#include <cmath>

#define PI 3.14159265

polar_feat::polar_feat(int rad, int dis, int ang, bool vRep) {
  //Polar histogram of DxA bins
  D = dis;
  A = ang;
  R = rad;
  vr = vRep;

  feat = new double[D * A];
}

polar_feat::~polar_feat() {
  delete[] feat;
}

void polar_feat::getPointFeat(gray **IMG, int W, int H, gray maxval, int col) {
  //Polar shape D distances, A angles
  int npoints = 0;
  for(int i=0; i<D*A; i++)
    feat[i] = 0;

  int cenR = H/2; //NO vertical reposition
  if( vr ) {
    //Compute center for vertical reposition
    cenR = 0;

    //For every pixel in [col-R, col+R]
    for(int k=0; k<H; k++)
      for(int j=col-R; j<=col+R; j++)
	if( j>=0 && j<W && IMG[k][j] < maxval ) {
	  cenR += k;
	  npoints++;
	}

    if( npoints==0 ) //Prevent errors in empty slices
      cenR = H/2;
    else
      cenR /= npoints;

    //Reset npoints, it will be used for normalization
    npoints = 0;
  }

  for(int k=0; k<H; k++)
    for(int j=col-R; j<=col+R; j++) {
      if( j>=0 && j<W && IMG[k][j] < maxval ) {
	//distance from center
	double d = sqrt((k-cenR)*(k-cenR) + (j-col)*(j-col));
	
	//If the point falls into the shape descriptor radius
	if( d <= R ) {
	  npoints++;
	  
	  double ang = atan2( k-cenR, j-col )*180.0/PI;
	  if( ang < 0.0 ) ang += 360;
	  
	  int pd = (int)(D*(d/R));
	  int pa = (int)(A*(ang/360.0));
	  
	  if( pd == D ) pd--;
	  if( pa == A ) pa--;
	  
	  feat[ pd*A + pa ] += 1;
	}
	
      }
    }
  
  if( npoints > 0 ) {
    for(int i=0; i<D*A; i++) {
      feat[i] /= (double)npoints;
      printf(" %g", feat[i]);
    }
    printf("\n");
  }
  else {
    for(int i=0; i<D*A; i++)
      printf(" 0");
    printf("\n");
  }

}
