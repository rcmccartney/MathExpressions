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

#include "online.h"


///////////////////////////////////////
// Aux functions
///////////////////////////////////////

inline int MAX(int a, int b) {
  if (a>=b) return a;
  else return b;		    
}

inline int MIN(int a, int b) {
  if (a<=b) return a;
  else return b;		    
}

///////////////////////////////////////
// stroke methods
///////////////////////////////////////

stroke::stroke(int n_p, bool pen_d, bool is_ht): n_points(n_p), pen_down(pen_d), is_hat(is_ht) {}

void stroke::print() {
  cout << n_points << endl << pen_down << endl;
  for (int i=0; i<n_points; i++) points[i].print();
}


///////////////////////////////////////
// sentence methods
///////////////////////////////////////

sentence::sentence(string w, int n_s): transcrip(w), n_strokes(n_s) {}

void sentence::print(bool print_pen_up) {
  cout << transcrip << endl << n_strokes<< endl;
  for (int i=0; i<n_strokes; i++)
    if (strokes[i].pen_down || print_pen_up) strokes[i].print();
}


// Remove repeated points
sentence * sentence::remove_rep_points() {
  sentence * sent_norep=new sentence(transcrip,n_strokes);
  for (int s=0; s<n_strokes; s++) {
    stroke stroke_norep;
    vector<Point> puntos=strokes[s].points;
    int np=strokes[s].n_points;
    for (int p=0; p<np; p++) {
      if (p<(np-1) && puntos[p]==puntos[p+1]) continue;
      Point point(puntos[p].x,puntos[p].y);
      stroke_norep.points.push_back(point);
    }
    stroke_norep.pen_down=strokes[s].pen_down;
    stroke_norep.n_points=stroke_norep.points.size();
    (*sent_norep).strokes.push_back(stroke_norep);
  }
  return sent_norep;
}

// Smoothing: median filter
sentence * sentence::smooth_strokes(int cont_size) {
  int sum_x,sum_y;
  sentence * sentNorm=new sentence(transcrip,n_strokes);
  for (int i=0; i<n_strokes; i++) {
    stroke strokeNorm;
    vector<Point> puntos=strokes[i].points;
    int np=strokes[i].n_points;
    for (int p=0; p<np; p++){
      sum_x=sum_y=0;
      for (int c=p-cont_size; c<=p+cont_size; c++)
	if (c<0) {
	  sum_x+=puntos[0].x;
	  sum_y+=puntos[0].y;
	} else if (c>=np) {
	  sum_x+=puntos[np-1].x;
	  sum_y+=puntos[np-1].y;
	} else {
	  sum_x+=puntos[c].x;
	  sum_y+=puntos[c].y;
	}
      Point point(int(sum_x/(cont_size*2+1)),int(sum_y/(cont_size*2+1)));
      strokeNorm.points.push_back(point);
    }
    strokeNorm.pen_down=strokes[i].pen_down;
    strokeNorm.n_points=strokeNorm.points.size();
    (*sentNorm).strokes.push_back(strokeNorm);
  }
  return sentNorm;
}
