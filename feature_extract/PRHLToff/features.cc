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

#include "features.h"
#include "imageClass.h"

#define SAMPLES_PER_PIXEL 5


FeatPRHLT::FeatPRHLT(int nCells, float ovC, float ovV, float vctF, char flT, int nVectors)
{
  param.nCells = nCells;
  param.ovCell = ovC;
  param.ovVector = ovV;
  param.vectFactor = vctF;
  param.filterType = flT;
  param.nVectors = nVectors;
}


FeatPRHLT::~FeatPRHLT() {
}

float ** FeatPRHLT::createMatrix(int rows, int cols)
{
  float ** array = (float **) new float*[rows];
  for (int r=0; r<rows; r++)
    array[r] = (float *) new float[cols];
  return array;
}


void FeatPRHLT::freeMatrix(float **array, int rows)
{
  for (int r=0; r<rows; r++) delete [] array[r];
  delete [] array;
}


float FeatPRHLT::funcFilter(float x, float u, float s, char type)
{
  float result;
  switch (type){
  case 'g':
    s=s/4;
    result=exp(-0.5*pow(((x-u)/s),2));
    break;
  case 'h':
    result=0.54+0.46*cos(PI*(x-u)/s);
    break;
  default:
    result=1.0;
  }
  return(result);
}


float FeatPRHLT::sumGreyLevel(float **Cell, float *yf, float *xf, 
			      int rows, int cols)
{
  float result=0.0;
  for (int i=0; i<rows; i++)
    for (int j=0; j<cols; j++) 
      result+=Cell[i][j]*yf[i]*xf[j];
  return result;
}


float FeatPRHLT::derivate(float **Cell, int rows, int cols, float *x, float *w,
			  int maxval, char type)
{
    float *y=NULL, slope=0.0;
    int n=0;
    
    switch (type)  {
    case 'h':
      y = new float[cols];
      for (int j=0; j<cols; j++) {
	float aux=0.0;
	for (int i=0;i<rows;i++) aux+=Cell[i][j];
	y[j]=aux/(rows*maxval);
      }
      n=cols;
      break;
    case 'v':
      y = new float[rows];
      for (int i=0;i<rows;i++) {
	float aux=0.0;
	for (int j=0; j<cols; j++) aux+=Cell[i][j];
	y[i]=aux/(cols*maxval);
      }
      n=rows;
      break;
    }
    
    float A, B, sumA=0.0, sumAX=0.0, sumB=0.0, sumBX=0.0, sumW=0.0;
    
    for (int i=0; i<n; i++) {
      A=w[i]*x[i];
      B=w[i]*y[i];
      sumA+=A;
      sumB+=B;
      sumW+=w[i];
      sumAX+=A*x[i];
      sumBX+=B*x[i];
    }
    slope=(sumB*sumA-sumW*sumBX)/(sumA*sumA-sumW*sumAX);
    
    delete [] y;
    return(atan(slope));
}


float ** FeatPRHLT::extrFeatPRHLT(const input_user &iuser, 
				  const imageClass &idata)
{
  float size_x_cell, size_y_cell, pos_x_cell, pos_y_cell;
  float x_cell, y_cell, Normalization_Value=0.0;
  float **getfeatures=NULL, **sample_cell=NULL;
  float *X_coord=NULL, *X_filt=NULL, *Y_coord=NULL, *Y_filt=NULL;
  int sub_frec_x, sub_frec_y;
  int pos_hder, pos_vder, num_features;
  
  int COLS=idata.getWidth();
  int ROWS=idata.getHeight();
  int MAXVAL=255;
  
  size_x_cell=((float)COLS/(float)iuser.nVectors)*(1+2*iuser.ovVector);
  pos_x_cell=0.5*((float)COLS/(float)iuser.nVectors);
  sub_frec_x=RoundUp(size_x_cell*SAMPLES_PER_PIXEL);
  
  if (iuser.lowerRow)  {
    int auxROWS=iuser.lowerRow-iuser.upperRow+1;
    size_y_cell=((float)auxROWS/(float)iuser.nCells)*(1+2*iuser.ovCell);
    pos_y_cell=0.5*((float)auxROWS/(float)iuser.nCells);
  } else {
    size_y_cell=((float)ROWS/(float)iuser.nCells)*(1+2*iuser.ovCell);
    pos_y_cell=0.5*((float)ROWS/(float)iuser.nCells);
  }
  sub_frec_y=RoundUp(size_y_cell*SAMPLES_PER_PIXEL);
  
  pos_hder=pos_vder=num_features=0;
  pos_hder=iuser.grey;
  pos_vder=pos_hder+iuser.hder;

  num_features=iuser.grey+iuser.hder+iuser.vder;
  
  getfeatures=createMatrix(iuser.nVectors,num_features*iuser.nCells);
  X_coord = new float[sub_frec_x];
  X_filt  = new float[sub_frec_x];
  Y_coord = new float[sub_frec_y];
  Y_filt  = new float[sub_frec_y];
  sample_cell=createMatrix(sub_frec_y,sub_frec_x);
  
  for (int k=0; k<sub_frec_x; k++)
  {
      X_coord[k]=size_x_cell*(((float)k/sub_frec_x)+(0.5/sub_frec_x)-0.5);
      X_filt[k]=funcFilter(X_coord[k],0,size_x_cell,iuser.filterType);
  }
  for (int h=0; h<sub_frec_y; h++)
  {
      Y_coord[h]=size_y_cell*(((float)h/sub_frec_y)+(0.5/sub_frec_y)-0.5);
      Y_filt[h]=funcFilter(Y_coord[h],0,size_y_cell,iuser.filterType);
  }
  for (int k=0; k<sub_frec_x; k++)
      for (int h=0;h<sub_frec_y;h++) Normalization_Value+=Y_filt[h]*X_filt[k];
  Normalization_Value*=MAXVAL;
  
  for (int v=0; v<iuser.nVectors; v++)
      for (int f=0; f<iuser.nCells; f++)
      {
	  for (int k=0; k<sub_frec_x; k++)
	  {
	      x_cell=X_coord[k]+pos_x_cell*(1+2*v);
	      for (int h=0; h<sub_frec_y; h++)
	      {
		  y_cell=Y_coord[h]+pos_y_cell*(1+2*f) + iuser.upperRow;
		  if (x_cell<0 || x_cell>=COLS || y_cell<0 || y_cell>=ROWS)
		      sample_cell[h][k]=0;
		  else
		      sample_cell[h][k]=(MAXVAL-(float)idata.image  [(int)y_cell][(int)x_cell]);
	      }
	  }
	  if (iuser.grey) {
	      getfeatures[v][f]=100*sumGreyLevel(sample_cell,Y_filt,X_filt,sub_frec_y,sub_frec_x)/Normalization_Value;
	      if (! isnormal(getfeatures[v][f]))
		getfeatures[v][f]=0;
	  }
	  
	  if (iuser.hder){
	    getfeatures[v][f+pos_hder*iuser.nCells]=derivate(sample_cell,sub_frec_y,sub_frec_x,X_coord,X_filt,MAXVAL,'h');
	    if (! isnormal(getfeatures[v][f+pos_hder*iuser.nCells]))
	      getfeatures[v][f+pos_hder*iuser.nCells]=0;
	  }
	  if (iuser.vder){
	    getfeatures[v][f+pos_vder*iuser.nCells]=derivate(sample_cell,sub_frec_y,sub_frec_x,Y_coord,Y_filt,MAXVAL,'v');
	    if (! isnormal(getfeatures[v][f+pos_vder*iuser.nCells]))
	      getfeatures[v][f+pos_vder*iuser.nCells]=0;
	  }
      }
  
  freeMatrix(sample_cell,sub_frec_y);
  delete [] X_coord;
  delete [] Y_coord;
  delete [] X_filt;
  delete [] Y_filt;
  
  return(getfeatures);
}


void FeatPRHLT::setExtractionParameters(int nCells, float ovVert, float ovHoriz, float vctF, char flT) {
	param.nCells = nCells;
	param.ovCell = ovVert;        // Overlaping Vertical
	param.ovVector = ovHoriz;      // Overlaping Horitzontal
	param.vectFactor = vctF; 
	param.filterType = flT;
}

void FeatPRHLT::setNumberOfVectors(int nVectors)
{
	param.nVectors = nVectors;
}

int  FeatPRHLT::getNumberOfVectors(){
  return  param.nVectors;
}

void FeatPRHLT::resetNumberOfVectors()
{
	param.nVectors = 0;
}

float ** FeatPRHLT::getSeqFeatPRHLTOnDelimitedImage(const imageClass & image, int upR, int lwR) {
  float ** sfeats;
  if (upR>=0 && upR<lwR && lwR<image.getHeight())  {
    param.upperRow=upR;
    param.lowerRow=lwR;
    sfeats = getSeqFeatPRHLT(image);
  } else
    sfeats = getSeqNullFeatPRHLT(image);
  
  // Reset param.upperRow and param.lowerRow values to zero.
  param.upperRow=param.lowerRow=0;
  
  return sfeats;
}

float ** FeatPRHLT::getSeqFeatPRHLT(const imageClass & image) {
  bool popBack = false;
  // Use the previous computed param.nVectors if param.nVectors!=0
  if (param.nVectors==0)  {
    int imgW=image.getWidth(), imgH;
    if (param.lowerRow)
      imgH=param.lowerRow-param.upperRow+1;
    else
      imgH=image.getHeight();
    float asp_rat=(float)imgW/(float)imgH;
    param.nVectors=Round(param.vectFactor*asp_rat*param.nCells);
  } else if(param.nVectors==-1) {
    popBack = true;
    param.nVectors = image.getWidth();
  }
  
  //int number_feature=param.grey+param.hder+param.vder;
  float **Attributes = extrFeatPRHLT(param, image);

  if(popBack)
    param.nVectors = -1;
	
  return Attributes;
}

float ** FeatPRHLT::getSeqNullFeatPRHLT(const imageClass & image){

  bool popBack = false;
  // Use the previous computed param.nVectors if param.nVectors!=0
  if (param.nVectors==0)	{
    int imgW=image.getWidth(), imgH;
    if (param.lowerRow)
      imgH=param.lowerRow-param.upperRow+1;
    else
      imgH=image.getHeight();
    float asp_rat=(float)imgW/(float)imgH;
    param.nVectors=Round(param.vectFactor*asp_rat*param.nCells);
  } else if(param.nVectors==-1) {
    popBack = true;
    param.nVectors = image.getWidth();
  }
  
  int number_feature=param.grey+param.hder+param.vder;
  
  float ** sfeats=createMatrix(param.nVectors,number_feature*param.nCells);
  for (int i=0; i<param.nVectors; i++) {
    for (int j=0; j<number_feature*param.nCells; j++) 
      sfeats[i][j]=0;
  }

  if(popBack)
    param.nVectors = -1;
  
  return sfeats;
}
