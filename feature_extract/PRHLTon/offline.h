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

#ifndef _OFFLINE_FEAT_
#define _OFFLINE_FEAT_

class frame;

#include <iostream>
#include <cstdlib>
#include <vector>
#include "online.h"
#include "features.h"

class offline_feat{
  int REND_H, REND_W;
  int xMin, yMin, xMax, yMax;
  int W, H;
  int **img;

 public:
  offline_feat(vector<PointR> & points, int MH, int MW, char *out);
  ~offline_feat();

  void render(vector<PointR> & points, char *outfile);
  void line(PointR &pa, PointR &pb);
  void setPointFeat(PointR &P, frame &F, int N);
};


#endif
