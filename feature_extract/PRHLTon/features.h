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

#ifndef FEATURES_H
#define FEATURES_H

#include <math.h>
#include <iostream>
#include <iomanip>
#include <vector>
#include <values.h>
#include "online.h"
#include "offline.h"

using namespace std;

struct frame {
  double x,y,dx,dy,ax,ay,k;
  vector<double> off;
  
  void print(ostream & fd);
  int get_fr_dim();
};


class sentenceF {
  vector<PointR> normalizaAspect(vector<Point> & puntos);
  void calculate_derivatives(vector<PointR> & points, bool norm=true);
  void calculate_kurvature();
  void calculate_offline_feat(vector<PointR> & points, int wsize, int mh, int mw, char *out);

  public:
    string transcrip;
    int n_frames;
    frame * frames;
    
    sentenceF();
    ~sentenceF();

    bool print(ostream & fd);
    void calculate_features(sentence &s, int wsize, int mh, int mw, char *out=NULL);
};

#endif
