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

#include "offline.h"
#include <cstdio>

#define OFFSET   2

offline_feat::offline_feat(vector<PointR> & points, int MH, int MW, char *out) {
  REND_H = MH;
  REND_W = MW;
  render( points, out );
}

offline_feat::~offline_feat() {
  for(int i=0; i<H+2*OFFSET; i++)
    delete[] img[i];
  delete[] img;
}

void offline_feat::render(vector<PointR> & points, char *outfile) {
  xMin = yMin =  INT_MAX;
  xMax = yMax = -INT_MAX;
  
  //Compute bounding box of the region containing the sequence of points
  for (int i=0; i<points.size(); i++) {
    if( points[i].x < xMin ) xMin = points[i].x;
    if( points[i].y < yMin ) yMin = points[i].y;
    if( points[i].x > xMax ) xMax = points[i].x;
    if( points[i].y > yMax ) yMax = points[i].y;
  }
  
  W = xMax - xMin + 1;
  H = yMax - yMin + 1;
  
  //Keeping the aspect ratio, scale the image to REND_H pixels height
  W = REND_H * (float)W/H;
  H = REND_H;

  //If the image is too wide (e.g. a fraction bar) limit the width of the image to REND_W
  if( W > REND_W )
    W = REND_W;

  //Enforce a minimum size in both dimensions
  if( H < 5 ) H = 3;
  if( W < 5 ) W = 3;

  //Create image
  img = new int*[H+OFFSET*2];
  for(int i=0; i<H+OFFSET*2; i++) {
    img[i] = new int[W+OFFSET*2];
    for(int j=0; j<W+OFFSET*2; j++)
      img[i][j] = 255;
  }

  PointR pant(0,0), aux(0,0);

  if( points.size() == 1 ) {
    //A single point is represented as a full black image
    for(int i=OFFSET; i<H+OFFSET; i++)
      for(int j=OFFSET; j<W+OFFSET; j++)
	img[i][j] = 0;

  } else {

    //Render strokes
    for(int i=0; i<points.size(); i++) {
      aux.x = OFFSET + (W-1)*(points[i].x - xMin)/(float)(xMax-xMin+1);
      aux.y = OFFSET + (H-1)*(points[i].y - yMin)/(float)(yMax-yMin+1);

      img[(int)aux.y][(int)aux.x] = 0;

      //Draw a line between last point and current point
      if( i>=1 && !points[i-1].getpu() ) //Do not draw a point between strokes (getpu)
	line(pant, aux);
      
      //Draw single-point strokes
      if( ( i==0 && points[i].getpu() )
	  || (i>=1 && points[i-1].getpu() && points[i].getpu() ) )
	line(aux,aux);

      //Update last point
      pant = aux;
    }

  }

  //Create smoothed image
  int **img_smo = new int*[H+OFFSET*2];
  for(int i=0; i<H+OFFSET*2; i++) {
    img_smo[i] = new int[W+OFFSET*2];
    for(int j=0; j<W+OFFSET*2; j++)
      img_smo[i][j] = 0;
  }

  //Smooth AVG(3x3)
  for(int y=0; y<H+2*OFFSET; y++)
    for(int x=0; x<W+2*OFFSET; x++) {

      for(int i=y-1; i<=y+1; i++)
	for(int j=x-1; j<=x+1; j++)
	  if( i>=0 && j>=0 && i<H+2*OFFSET && j<W+2*OFFSET )
	    img_smo[y][x] += img[i][j];
	  else
	    img_smo[y][x] += 255; //Background
      
      img_smo[y][x] /= 9; //3x3
    }

  //Replace IMG with the smoothed image and free memory
  for(int y=0; y<H+2*OFFSET; y++)
    delete[] img[y];
  delete[] img;

  img = img_smo;

  //Save PGM image if required
  if( outfile ) {
    FILE *fd=fopen(outfile,"w");
    if( fd ) {
      fprintf(fd, "P2\n%d %d\n255\n", W+2*OFFSET, H+2*OFFSET);
      for(int i=0; i<H+2*OFFSET; i++) {
	for(int j=0; j<W+2*OFFSET; j++)
	  fprintf(fd, " %3d", img[i][j]);
	fprintf(fd, "\n");
      }
    }
    else {
      fprintf(stderr, "Error creating image '%s'\n", outfile);
      exit(-1);
    }
    fclose(fd);
  }

}


//Draw line between points pa and pb
void offline_feat::line(PointR &pa, PointR &pb) {
  const float dl = 3.125e-3;
  int dx = (int)pb.x - (int)pa.x;
  int dy = (int)pb.y - (int)pa.y;

  for(float l=0.0; l < 1.0; l += dl) {
    int x = (int)pa.x + (int)(dx*l+0.5);
    int y = (int)pa.y + (int)(dy*l+0.5);

    //Draw 3x3 pixels for each point
    for(int i=y-1; i<=y+1; i++)
      for(int j=x-1; j<=x+1; j++)
	if( i>=0 && i<H+2*OFFSET && j>=0 && j<W+2*OFFSET)
	  img[i][j] = 0;
  }
}

//Compute context-window (size NxN) for point P and save it in frame F
void offline_feat::setPointFeat(PointR &P, frame &F, int N) {
  if( N>0 ) {
    PointR aux(0,0);

    aux.x = (int)(OFFSET + (W-1)*(P.x - xMin)/(xMax-xMin+1));
    aux.y = (int)(OFFSET + (H-1)*(P.y - yMin)/(yMax-yMin+1));
    
    for(int i=aux.y-N/2; i<=aux.y+N/2; i++)
      for(int j=aux.x-N/2; j<=aux.x+N/2; j++)
	if( i<0 || i>=H+2*OFFSET || j<0 || j>=W+2*OFFSET )
	  F.off.push_back( 255 ); //Background
	else
	  F.off.push_back( img[i][j] );
  }
}
