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

#include "read.h"


int read_file_moto(istream &fd, sentence ** S) {
  
  char linea[MAX_LIN];
  static int line_counter=0;
  
  while (fd.getline(linea,MAX_LIN)) {
    line_counter++;
    if (linea[0]!='#' && linea[0]!=' ' && strlen(linea)>0) break;
  }
  if (fd.eof()) return false;

  if (!isgraph(linea[0])) {
    cerr << "ERR 2: incorrect file format. Line " << line_counter << endl;
    return false;
  }

  // New sentence
  int n_strokes;
  fd >> n_strokes;
  line_counter++;
  sentence *sent=new sentence(linea,n_strokes);
  
  // Read strokes
  for (int s=0; s<n_strokes; s++) {		
    int num_points_stroke;
    line_counter++;
    fd >> num_points_stroke;
    if (!fd.good()) {
      cerr << "ERR 1: incorrect file format. Line: " << line_counter << endl;
      return false;
    }
      
    int is_pen_down;
    line_counter++;
    fd >> is_pen_down;
    if (!fd.good()) {
      cerr << "ERR 1: incorrect file format. Line: " << line_counter << endl;
      return false;
    }
      
    stroke st(num_points_stroke,is_pen_down);
    // Read sequence of points of the stroke
    for (int i=0; i<num_points_stroke; i++) {
      int x, y;
      line_counter++;
      fd >> x >> y;
      if (!fd.good()) {
	cerr << "ERR 1: incorrect file format. Line: " << line_counter << endl;
        return false;
      }
      Point p(x,y);
      st.points.push_back(p);
    }

    // Add stroke to sentence
    if (st.points.size()>0) (*sent).strokes.push_back(st);
    else if (n_strokes>0) (*sent).n_strokes--;
  }
  *S=sent;
  
  return true;
}

