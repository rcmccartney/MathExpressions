/*Copyright 2000-2009 Moisés Pastor, Alejandro H. Toselli

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

#ifndef FEAT_H
#define FEAT_H
#include <cmath>
#include "imageClass.h"

#ifndef PI
#define PI M_PI
#endif

class input_user {
 public:
  int nVectors;
  float vectFactor;
  int nCells;
  float ovVector;
  float ovCell;
  char filterType;
  int grey;
  int hder;
  int vder;
  int upperRow;
  int lowerRow;
  input_user () {
    nVectors = 0;
    vectFactor = 1.0;
    nCells = 20;
    ovVector = 2;
    ovCell = 2;
    filterType = 'g';
    grey = 1;
    hder = 1;
    vder = 1;
    upperRow = 0;
    lowerRow = 0;
  }
};


class FeatPRHLT {
private:

	input_user param;

	int RoundUp(float x) { return ((int)ceil(x)); }
	int Round(float x) { return ((int)(x+0.5)); }
	float **createMatrix(int rows, int cols);
	void freeMatrix(float **ARRAY, int rows);
	float funcFilter(float x, float u, float s, char type);
	float sumGreyLevel(float **Cell, float *yf, float *xf, int rows, int cols);
	float derivate(float **Cell, int rows, int cols, float *x, float *w, int maxval, char type);
	float **extrFeatPRHLT(const input_user &iuser, const imageClass &idata);

public:
	 FeatPRHLT(int nCells=20, float ovC=2, float ovV=2, float vctF=1.0, char flT='g', int nVectors=0);
	 virtual ~FeatPRHLT();

	/*!\brief Set up the parameters which control the Image Feature Extraction.
	 * \param set of parameters that control the Feature Extraction.
	 */
	 void setExtractionParameters(int nCells, float ovC, float ovV, float vctF, char flT);

	/*!\brief Set the number of vectors.
	 * \param number of features vectors.
	 */
	 void setNumberOfVectors(int nVectors);

	 int getNumberOfVectors();

	/*!\brief Reset the number of vectors to zero.
	 */
	 void resetNumberOfVectors();

	/*!\brief Compute the sequence of AHT features from the image \a tImage.
	 */
	 //SeqFeaturesPRHL* getSeqFeatures(const imageClass & image);
	 float ** getSeqFeatPRHLT(const imageClass & image);

	/*!\brief Compute the sequence of AHT features from the image \a tImage.
	 * \param tImage input binary image, lower and upper Rows.
	 */
	 float ** getSeqFeatPRHLTOnDelimitedImage (const imageClass & image, int upR, int lwR);

	/*!\brief Get back a sequence of features with all their component values set up to zero.
	 * \param tImage input binary image.
	 * \return the sequence of Null features.
	 */
	 float ** getSeqNullFeatPRHLT(const imageClass & image);

};


#endif /* FEAT_H */
