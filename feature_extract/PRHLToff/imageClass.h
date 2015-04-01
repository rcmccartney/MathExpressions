/*Copyright 2007 Moisés Pastor

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

#ifndef PGMCLASS_H
#define PGMCLASS_H

#include <iostream>


#define PGM_MAXVAL 255
/* Magic constants. */
#define PGM_MAGIC1 'P'
#define PGM_MAGIC2 '2'
#define RPGM_MAGIC2 '5'
#define PPM_MAGIC2 '3'

using namespace std;

typedef unsigned char gray;

class imageClass{

  bool read_pgm(istream & file);
#ifndef ONLY_PGM
 bool read_jpg(FILE * fitx);
 bool read_png(FILE*);

 bool write_jpg(FILE * fitx,int quality=90);
 bool write_png(FILE * file);
#endif

 bool write_pgm(ostream & file, bool binary=true);
 void mean_double(int * h, int k, float & mu1, float & mu2, float & muT);

public:
  gray ** image;
  int rows,cols;
  gray maxval;
  int verbosity;
  imageClass();
  imageClass(int r, int c, gray maxv);
  imageClass(imageClass & otra);
  ~imageClass();
  int getWidth() const {return cols;};
  int getHeight() const {return rows;};
  const gray getPixel(int f,int c) const {return image[f][c];};
  bool read(string & fitx);
 
  bool write(string fitx, bool binary=false);
  void invertir();
  int otsu() ;
  int otsu(int r_ini, int r_fi);
  int otsu(int rowIni, int colIni, int nCols, int nRows);
  int* getHorizProjection(int r_ini, int r_fi);
  int* getHorizProjection();
  int* getVerticalProjection();
  int * getHistGreyLevel();
  int * getHistGreyLevel(int r_ini, int r_fi);
  int * getHistGreyLevel(int rowIni, int colIni, int nCols, int nRows);
  imageClass * crop(bool vertical=true, bool horizontal=true);
  int tamanyo_medio_huecos(int * V_Projection, int cols);
 
};

#endif
