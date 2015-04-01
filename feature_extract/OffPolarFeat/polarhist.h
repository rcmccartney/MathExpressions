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

#ifndef _POLAR_FEAT_
#define _POLAR_FEAT_

class frame;

#include <cstdio>
#include <cstdlib>
#include "libpgm.h"

class polar_feat{
  double R;
  int D; //distances
  int A; //angles
  double *feat;
  bool vr;

 public:
  polar_feat(int rad, int dis, int ang, bool vRep);
  ~polar_feat();

  void getPointFeat(gray **IMG, int W, int H, gray maxmal, int col);
};


#endif
