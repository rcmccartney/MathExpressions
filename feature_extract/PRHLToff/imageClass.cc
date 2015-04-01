/*Copyright 2013 Moisés Pastor

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

#include <sstream>
#include <string>
#include <fstream>
#include <climits>
#include <jpeglib.h>
#include <png.h>
#include "imageClass.h"

imageClass::imageClass(){
  image=0;
  rows=cols=0;
}
imageClass::imageClass (imageClass & otra){
  rows=otra.rows;
  cols=otra.cols;
  maxval=otra.maxval;
  verbosity=otra.verbosity;

  image= new gray *[rows];
  for (int r=0; r<rows; r++)
    image[r]=new gray [cols];
  for (int r=0; r<rows;r++)
    for (int c=0;c<cols;c++)
      image[r][c]=otra.image[r][c];
}

imageClass::imageClass(int rows, int cols, gray maxval){
  this->rows=rows;
  this->cols=cols;
  this->maxval=maxval;

  image= new gray *[rows];
  for (int r=0; r<rows; r++ )
    image[r]=new gray [cols];
  
  for (int r=0; r<rows;r++)
    for (int c=0;c<cols;c++)
      image[r][c]=maxval;
}

imageClass::~imageClass(){
  if (image){
    for (int r=0; r<rows; r++)
      if (image[r])
      delete [] image[r];
    delete [] image;
  }
}

#ifndef ONLY_PGM
bool imageClass::read_png(FILE * file){
  png_structp png_ptr;
  png_infop info_ptr;
  //  const int PNG_BYTES_TO_CHECK = 4;
  // unsigned char header[8];


  // fread(header, 1, 8, file);
  // if (png_sig_cmp(header, 0, 8))
  //   return false;
  //  abort_("[read_png_file] File %s is not recognized as a PNG file", file_name);
  png_ptr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (png_ptr == NULL) {
    return false;
  }

  info_ptr = png_create_info_struct(png_ptr);
  if (info_ptr == NULL) {
    png_destroy_read_struct(&png_ptr, png_infopp_NULL, png_infopp_NULL);
    return false;
  }
  
  if (setjmp(png_jmpbuf(png_ptr))) {
    png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);
    return false;
  }

  png_info_init(info_ptr);

  png_init_io(png_ptr, file);
  //png_set_sig_bytes(png_ptr, 8);
  png_read_info(png_ptr, info_ptr);

  rows = (int)png_get_image_height(png_ptr, info_ptr);
  cols = (int)png_get_image_width(png_ptr, info_ptr);
  maxval = 255;
  
  int channels = (int)png_get_channels(png_ptr, info_ptr);
  // int color_type = png_get_color_type(png_ptr, info_ptr); ////******
  //int bit_depth= png_get_bit_depth(png_ptr, info_ptr); 
  
  if (setjmp(png_jmpbuf(png_ptr))){
    png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);
    return false;
  }

 
  png_bytep * row_pointers= new png_bytep[rows];
  for (int r = 0; r < rows; r++)
    row_pointers[r] = (png_bytep)png_malloc(png_ptr, png_get_rowbytes(png_ptr, info_ptr));
  
  png_read_image(png_ptr, row_pointers);


  image = new gray*[rows];
  for (int r=0; r<rows; r++)
    image[r]=new gray[cols];
  
  if (channels == 1 ){ //|| bit_depth == 8)

    for (int r = 0; r < rows; r++)
      for (int c = 0; c < cols; c++)
	image[r][c] = row_pointers[r][c];
    
  } else if ( channels == 2){
    for (int r = 0; r < rows; r++){
      unsigned char *ptr=(unsigned char*) row_pointers[r];
      for (int c = 0; c < cols; c++){
	image[r][c] = *ptr;
	ptr+=2;
      }
    }
  } else if (channels == 3){
    for (int ro = 0; ro < rows; ro++){
      unsigned char *ptr=(unsigned char*) row_pointers[ro];
      for (int c = 0; c < cols; c++){
	int r = *ptr++;
	int g = *ptr++;
	int b = *ptr++;
	//image[ro][c]= 0.2126*r + 0.7152*g + 0.0722*b;
	//image[ro][c]=(a<<24) | (r << 16) | (g << 8) | (b);
	image[ro][c]=(r << 16) | (g << 8) | (b);
      }  
    }
  } if (channels == 4){
    imageClass * alpha = new imageClass(rows, cols,maxval);

    for (int ro = 0; ro < rows; ro++){
      unsigned char *ptr=(unsigned char*) row_pointers[ro];      
      for (int c = 0; c < cols; c++){
	int r = *ptr++;
	int g = *ptr++;
	int b = *ptr++;
	alpha->image[ro][c] =  *ptr++; //alpha channel

	//image[ro][c]= 0.2126*r + 0.7152*g + 0.0722*b;
	//image[ro][c]=(a<<24) | (r << 16) | (g << 8) | (b);
	image[ro][c]=(r << 16) | (g << 8) | (b);
      }
    }
   
    int * hist=getHistGreyLevel();
    int pos =0 ;
    for (int i=0; i<255; i++)
      if (hist[i] > hist[pos]) 
	pos = i;

    unsigned int background= pos;
    for (int r = 0; r < rows; r++)
      for (int c=0; c < cols; c++)
	if (alpha->image[r][c]==0)
	  image[r][c]=background;
    
    delete alpha;
  }

  png_read_end(png_ptr, NULL);
  png_destroy_read_struct(&png_ptr, &info_ptr, NULL);
  delete [] row_pointers;
  return true;

}
//bool imageClass::read_jpg(istream & fitx){
bool imageClass::read_jpg(FILE * file){
  struct jpeg_decompress_struct cinfo;
  struct jpeg_error_mgr jerr;

  cinfo.err = jpeg_std_error(&jerr);
  /* Now we can initialize the JPEG decompression object. */
  jpeg_create_decompress(&cinfo);
  /* specify data source (eg, a file) */
  jpeg_stdio_src(&cinfo, file);
  /*read file parameters with jpeg_read_header() */
  jpeg_read_header(&cinfo, true);
   
  /* Start decompressor */
  jpeg_start_decompress(&cinfo);
    
  int stride = cinfo.output_width * cinfo.output_components;
  unsigned char** buffer = (*cinfo.mem->alloc_sarray) ((j_common_ptr) &cinfo, JPOOL_IMAGE, stride, 1);
  cols = cinfo.output_width;
  rows = cinfo.output_height;
  maxval = 0;

  image=new gray *[rows];
  for (int r=0; r<rows; r++)
    image[r]=new gray [cols];

  const int a = 255;
    
  int f=0; 
  while (cinfo.output_scanline < cinfo.output_height) {
    jpeg_read_scanlines(&cinfo, buffer, 1);
    unsigned char* pcomp = *buffer;
    for (unsigned int c = 0; c < cinfo.output_width; c++) {
      if (cinfo.output_components == 3) { //RGB
	int r = *pcomp++;
	int g = *pcomp++;
	int b = *pcomp++;
	image[f][c]=(a<<24) | (r << 16) | (g << 8) | (b);
      } else
	image[f][c] = *pcomp++;

      if (image[f][c] > maxval) maxval = image[f][c];
    }
      f++;
    }
    
    jpeg_finish_decompress(&cinfo);
    jpeg_destroy_decompress(&cinfo);
    
    return true;
    
}
#endif

bool  imageClass::read_pgm(istream & file){
  char char1,char2; 
  string line;

  //llegim numero magic
  do{
    getline(file,line);
  }while (line[0]=='#' || line.empty());
  
  
  istringstream l(line);
  l >> char1 >> char2;
  if (char1 != PGM_MAGIC1 || (char2 != PGM_MAGIC2 && (char2 !=RPGM_MAGIC2))){
    cerr << "Error: Bad magic number - not an  pgm file" << endl;
    return(false);
  }
  
  //llegin columna i fila
  do 
      getline(file,line);
  while (line[0]=='#' || line.empty());  // per als comentaris
  istringstream l2(line);
  l2 >> cols >> rows;

  //llegim el max rang dels grisos
  do
      getline(file,line);
  while (line[0]=='#' || line.empty());  // per als comentaris
  istringstream l3(line);
  int aux;
  l3 >> aux;
  maxval=gray(aux);
  if (maxval == 0){
    cerr << "Error: Maxval of input image is zero." << endl;
    return(false);
  }
  //demanem memoria
  image=new gray *[rows];
  for (int r=0; r<rows; r++)
    image[r]=new gray [cols];

  if (  char2 == PGM_MAGIC2 ) //formato ascii
    for (int r=0; r<rows;r++)
      for (int c=0;c<cols;c++){
	file >> aux;
	image[r][c]=gray(aux);
      }
  else if ( char2 == RPGM_MAGIC2){ // formato binario
      for (int r=0; r<rows;r++)
	  file.read ((char*) image[r] , sizeof(char)*cols );
  }
  return true;
}

bool  imageClass::read(string & fileName){

 
  if (fileName.size()==0) { // Standard input
    FILE * inFile=stdin;
   
    unsigned char buffer[4];
    
    int n=fread(buffer, sizeof(unsigned char), 4, inFile);

    if(n!=4 || buffer[0]==-1 || buffer[1]==-1) {
      fprintf(stderr,"read error: problems reading stream\n");
      return false;
    }
    
    //retornem els chars al stream
    int cnt=0;
    if((ungetc(buffer[3],inFile))!=buffer[3])
      cnt++;
    if((ungetc(buffer[2],inFile))!=buffer[2])
      cnt++;
    if((ungetc(buffer[1],inFile))!=buffer[1])
      cnt++;
    if((ungetc(buffer[0],inFile))!=buffer[0])
      cnt++;
    if(cnt) {
      fprintf(stderr,"read error: unable to ungetc\n");
      return false;
    }

    if (buffer[0]=='P' && (buffer[1]=='2' || buffer[1]=='5') )  // pgm format
      return read_pgm(cin);

 #ifndef ONLY_PGM
   else if((unsigned char)buffer[0]==0xFF && (unsigned char)buffer[1]==0xD8)   // jpg format
      return read_jpg(inFile);
    else if((unsigned char)buffer[0]==0x89 && buffer[1]=='P' && buffer[2]=='N' && buffer[3]=='G') 
      return read_png(inFile);
#endif

    else {
      fprintf(stderr,"read error: unknown format\n");
      return false;;
    }
  }else { // Input from a file
    if (fileName.find(".pgm")!=string::npos){
      ifstream ifd;
      ifd.open(fileName.c_str());
      if (!ifd){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return read_pgm(ifd);
    
    } 
#ifndef ONLY_PGM
    else if (fileName.find(".jpg")!=string::npos ||fileName.find(".jpeg")!=string::npos ){
      FILE * ifd;
      ifd=fopen(fileName.c_str(),"rb");
      if (ifd == NULL){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return read_jpg(ifd);
    } else  if (fileName.find(".png")!=string::npos){
      FILE * ifd;
      ifd=fopen(fileName.c_str(),"rb");
      if (ifd == NULL){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return read_png(ifd);
    }  
#endif
    else {
      cerr << "Input file format not supported (jpg/pgm/png)" << endl;
      return false;
    }
  }
  return true;
}

#ifndef ONLY_PGM
bool imageClass::write_png(FILE * file){
  png_structp png_ptr;
  png_infop info_ptr;
  
  png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (png_ptr == NULL) 
    return false;
  
  info_ptr = png_create_info_struct(png_ptr);
  if (info_ptr == NULL) {
    png_destroy_read_struct(&png_ptr, png_infopp_NULL, png_infopp_NULL);
    return false;
  }

  if (setjmp(png_jmpbuf(png_ptr))) {
    png_destroy_read_struct(&png_ptr, &info_ptr, png_infopp_NULL);
    return false;
  }

  png_init_io(png_ptr, file);
  png_set_IHDR(png_ptr, info_ptr, cols, rows, 8, PNG_COLOR_TYPE_GRAY,
	       PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
  png_set_rows(png_ptr, info_ptr, image);
  png_write_png(png_ptr, info_ptr, PNG_TRANSFORM_IDENTITY, png_voidp_NULL);
  
  return true;

}

bool  imageClass::write_jpg(FILE * file, int quality){
  struct jpeg_compress_struct cinfo;
  struct jpeg_error_mgr jerr;

  cinfo.err = jpeg_std_error(&jerr);
  jpeg_create_compress(&cinfo);
  jpeg_stdio_dest(&cinfo,file);

  cinfo.image_width = cols;
  cinfo.image_height = rows;
  cinfo.input_components = 1;
  cinfo.in_color_space = JCS_GRAYSCALE;

  jpeg_set_defaults(&cinfo);
  jpeg_set_quality(&cinfo,quality,TRUE);
  jpeg_start_compress(&cinfo,TRUE);

  jpeg_write_scanlines(&cinfo,(JSAMPROW*)image,rows);

  (void)jpeg_finish_compress(&cinfo);
  jpeg_destroy_compress(&cinfo);

  return true;

}

#endif

bool  imageClass:: write_pgm(ostream & file, bool binary){
  file << PGM_MAGIC1;
  if (binary)
    file << RPGM_MAGIC2 << endl;
  else 
    file << PGM_MAGIC2 << endl;
    
  file << cols << " " << rows << endl;
  file << int(maxval) << endl;
  if (binary)
      for (int r=0; r<rows; r++)
	  file.write((char*)image[r],sizeof(gray)*cols);
  else
      for (int r=0; r<rows; r++){
	  int charcount=1;
	  for (int c=0; c<cols; c++){
	      if ( charcount%65==0)
		  file <<endl;
	      file << int(image[r][c]) << " ";
	  }
	  file << endl;
      }
  //file.flush();
  return true;
}

bool imageClass:: write(string fileName, bool binary){

  if (fileName.size()==0){  // Standard input
    return write_pgm(cout, binary);
  } else
    if (fileName.find(".pgm")!=string::npos){
      ofstream ofd;
      ofd.open(fileName.c_str());
      if (!ofd){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return write_pgm(ofd, binary);
      
    }
#ifndef ONLY_PGM
    else if (fileName.find(".jpg")!=string::npos||fileName.find(".jpeg")!=string::npos ){
      FILE * ofd;
      ofd=fopen(fileName.c_str(),"wb");
      if (ofd == NULL){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return write_jpg(ofd);
    } else if (fileName.find(".png")!=string::npos ){
      FILE * ofd;
      ofd=fopen(fileName.c_str(),"wb");
      if (ofd == NULL){
	cerr << "Error: File \""<< fileName << "\" could not be open "<< endl;
	return  false;
      }
      return write_png(ofd);
    } 
#endif
    else {
      cerr << "Output file format not supported (jpg/pgm/png)" <<endl;
      return false;
    }
  
  return true;
}

void  imageClass::invertir() {
  for (int row=0; row<rows/2; row++) 
    for (int col=0; col<cols; col++){
      unsigned int aux = image[rows-1-row][col];
      image[rows-1-row][col]=image[row][col];
      image[row][col]=aux;
    }
}
int * imageClass::getHorizProjection(int r_ini, int r_fi) {
  unsigned int thresh=otsu(r_ini, r_fi);
  int * histHoriz = new int[r_fi - r_ini + 1];
  for (int r=0; r<= r_fi-r_ini; r++) histHoriz[r]=0;

  for (int r=r_ini; r<= r_fi; r++)
    for (int c=0; c<cols; c++){
      if ((unsigned(image[r][c]) <= thresh)) 
        histHoriz[r-r_ini]++; 
    }
     
  return histHoriz;
}

int * imageClass::getHorizProjection() {
  static unsigned int thresh=otsu();
  int * histHoriz = new int[rows];
  for (int r=0; r<rows; r++) histHoriz[r]=0;
  for (int r=0; r<rows; r++)
    for (int c=0; c<cols; c++)
      if ((unsigned(image[r][c]) <= thresh)) 
        histHoriz[r]++;
     
  return histHoriz;
}

int * imageClass::getVerticalProjection(){ 
    static unsigned int thresh=otsu();
    int * histver;

    int i,j;
    histver= new int [cols];
    for (j=0; j < cols; j++)
        histver[j]=0;
    
    for (j=0; j < cols; j++) {
      for (i=0; i < rows ; i++) 
        if (image[i][j] <= thresh){ 
          histver[j]++;
        }
      
    } 
    return histver;
}


int * imageClass::getHistGreyLevel(int rowIni, int colIni, int nRows, int nCols){

  if (rowIni == -1 || colIni == -1 || nCols == -1 || nRows == -1){
    rowIni=0;
    colIni=0;
    nRows=rows;
    nCols=cols;
  } else {
    rowIni = rowIni < 0? 0: rowIni;
    colIni = colIni < 0? 0: colIni;
    nRows = nRows > rows? rows: nRows;
    nCols = nCols > cols? cols: nCols;
  }

  int * histGreyLevel=new int [maxval+1];
  for (int i=0; i<=maxval; i++) histGreyLevel[i]=0;
  for (int r=rowIni; r<rowIni+nRows; r++)
    for (int c=colIni; c<colIni+nCols; c++) 
      if (image[r][c] <= maxval)
	histGreyLevel[image[r][c]]++;
      else
	cerr << "Value greater than maxval ¿? "<< (int)image[r][c]<< " " << (int)maxval << endl;
  
  return histGreyLevel;

}
int * imageClass::getHistGreyLevel(int r_ini, int r_fi) {
  return getHistGreyLevel(r_ini, 0, r_fi - r_ini + 1, cols);
  // float * histGreyLevel=new float [maxval+1];
  // for (int i=0; i<=maxval; i++) histGreyLevel[i]=0;
  // for (int r=r_ini; r<=r_fi; r++)
  //   for (int c=0; c<cols; c++) 
  //     if (image[r][c] <= maxval)
  // 	histGreyLevel[image[r][c]]++;
  //     else
  // 	cerr << "Value greater than maxval ¿? "<< (int)image[r][c]<< " " << (int)maxval << endl;
  
  // return histGreyLevel;
}

int * imageClass::getHistGreyLevel() {
  return getHistGreyLevel(0, 0, rows, cols);
  // float * histGreyLevel=new float [maxval+1];
  // for (int i=0; i<=maxval; i++) histGreyLevel[i]=0;
  // for (int r=0; r<rows; r++)
  //   for (int c=0; c<cols; c++) 
  //     if (image[r][c] <= maxval)
  // 	histGreyLevel[image[r][c]]++;
  //     else
  // 	cerr << "Value greater than maxval ¿? "<< (int)image[r][c]<< " " << (int)maxval << endl;
  
  // return histGreyLevel;
}
void imageClass::mean_double(int * h, int k, float & mu1, float & mu2,
                           float & muT) {
  float sum0=0, sum_tot0=0,sum1=0, sum_tot1=0;
  for (int i=0; i<=k; i++) {
    sum0+=i*h[i];
    sum_tot0+=h[i];
  }
  mu1=(sum_tot0>0)?sum0/sum_tot0:0;
  //mu1=sum0/sum_tot0;
  for (int i=k+1; i<=maxval; i++){
    sum1+=i*h[i];
    sum_tot1+=h[i];
  }
  //mu2=sum1/sum_tot1;
  mu2=(sum_tot1>0)?sum1/sum_tot1:0;

  muT=(sum0+sum1)/(sum_tot0+sum_tot1);
}


int  imageClass::otsu(int rowIni, int colIni, int nRows, int nCols){
  int * histGreyLevel=getHistGreyLevel(rowIni,colIni,nRows,nCols);
  float mu0, mu1, muT, max_sig_B2=0;
  int max_k=0;
  for (int k=0; k<=maxval; k++) {
    mean_double(histGreyLevel,k,mu0,mu1,muT);
    //prob a priori de la classe 0
    float Pr_C0=0;
    for (int i=0; i<=k; i++) Pr_C0+=histGreyLevel[i];
    // funcio objectiu
    //float sig_B2=(Pr_C0)*(1-Pr_C0)*(mu0-mu1)*(mu0-mu1);
    float sig_B2=(Pr_C0)*(muT-mu0)*(muT-mu0)+(1-Pr_C0)*(muT-mu1)*(muT-mu1);
    // optimitzacio
    if ( sig_B2 > max_sig_B2) {
      max_sig_B2 = sig_B2;
      max_k=k;
    }
  }
  delete [] histGreyLevel;
  return max_k;
}

int  imageClass::otsu(int r_ini, int r_fi) {
  return otsu(r_ini, 0, r_fi - r_ini + 1, cols);
  // float * histGreyLevel=getHistGreyLevel(r_ini, r_fi);
  // float mu0, mu1, muT, max_sig_B2=0;
  // int max_k=0;
  // for (int k=0; k<=maxval; k++) {
  //   mean_double(histGreyLevel,k,mu0,mu1,muT);
  //   //prob a priori de la classe 0
  //   float Pr_C0=0;
  //   for (int i=0; i<=k; i++) Pr_C0+=histGreyLevel[i];
  //   // funcio objectiu
  //   //float sig_B2=(Pr_C0)*(1-Pr_C0)*(mu0-mu1)*(mu0-mu1);
  //   float sig_B2=(Pr_C0)*(muT-mu0)*(muT-mu0)+(1-Pr_C0)*(muT-mu1)*(muT-mu1);
  //   // optimitzacio
  //   if ( sig_B2 > max_sig_B2) {
  //     max_sig_B2 = sig_B2;
  //     max_k=k;
  //   }
  // }
  // delete [] histGreyLevel;
  // return max_k;
}


int  imageClass::otsu() {
    return otsu(0,0,rows, cols);
    // float * histGreyLevel=getHistGreyLevel(0,);
 
  // float mu0, mu1, muT, max_sig_B2=0;
  // int max_k=0;
  // for (int k=0; k<=maxval; k++) {
  //   mean_double(histGreyLevel,k,mu0,mu1,muT);
  //   //prob a priori de la classe 0
  //   float Pr_C0=0;
  //   for (int i=0; i<=k; i++) Pr_C0+=histGreyLevel[i];
  //   // funci<F3> objectiu
  //   //float sig_B2=(Pr_C0)*(1-Pr_C0)*(mu0-mu1)*(mu0-mu1);
  //   float sig_B2=(Pr_C0)*(muT-mu0)*(muT-mu0)+(1-Pr_C0)*(muT-mu1)*(muT-mu1);
  //   // optimitzaci<F3>
  //   if ( sig_B2 > max_sig_B2) {
  //     max_sig_B2 = sig_B2;
  //     max_k=k;
  //   }
  // }
  // delete [] histGreyLevel;
  // return max_k;
}


imageClass * imageClass::crop(bool vertical, bool horizontal){
  int r_up=0,r_down=rows,c_ini=0, c_fin=cols;
  int N_pixels=0;
  imageClass * img_crop;
  
  int threshold=otsu();
  
  if (vertical){
    //crop arriba  --------------------------
    for (r_up=0; r_up<rows; r_up++){
      N_pixels=0;
      for (int c=0; c<cols; c++)
	if(image[r_up][c]<= threshold)
	  N_pixels++;
      if (N_pixels >= 5) break;
    }
  
    if (r_up > rows) r_up=0;
  
    if (verbosity>0)
      cerr << "crop arriba: " << r_up << endl;
  
    //crop abajo  --------------------------
    for (r_down=rows-1; r_down>=0; r_down--){
      N_pixels=0;
      for (int c=0; c<cols; c++)
	if(image[r_down][c] <= threshold)
	  N_pixels++;
      if (N_pixels >= 5) break;
    }
    if (r_down <0) r_down=rows-1;
  
    if (verbosity>0)
      cerr << "crop abajo: "<< r_down << endl;
  }
  if (horizontal){
    //crop derecha  --------------------------
    for (c_fin=cols-1; c_fin>=0;c_fin--){
      N_pixels=0;
      for(int r=0;r<rows;r++)
	if(image[r][c_fin] <= threshold)
	  N_pixels++;
      if (N_pixels >= 5)  break;
    }
  
    if (verbosity>0)
      cerr << "crop derecha:  "<<  c_fin << endl;                            
  
    // crop izquierda ¿?
    for (c_ini=0; c_ini <cols; c_ini++){
      N_pixels=0;
      for(int r=0;r<rows;r++)
	if(image[r][c_ini] <= threshold)
	  N_pixels++;
      if (N_pixels >= 5)  break;
    }
    if (verbosity > 0)
      cerr << "crop izquierda:  "<<  c_ini << endl;                            
  }
  
  
  int cols_crop= c_fin - c_ini + 1;
  int rows_crop= r_down - r_up + 1;
  
  if (( rows_crop <= 0) || (cols_crop <= 0)){
    return new imageClass(*this); 
  }
  img_crop= new imageClass(rows_crop, cols_crop, maxval);    //recalcular maxval
  
  for (int r=0; r< rows_crop; r++)
    for (int c=0; c<cols_crop; c++)
      img_crop->image[r][c]=image[r_up + r][c_ini+c];
  
  return img_crop;
}


int imageClass::tamanyo_medio_huecos(int * V_Projection, int cols){ 
  int contador=0, suma_huecos=0, total_huecos=0, i;

#define SEPARACION_MIN_LETRAS 1
#define UMBRAL_VERTICAL 1
#define MAX(x,y) ( ((x)>(y)) ? (x) : (y) )

  for (i=0;i<cols;i++) {
    contador=0;
    while ((i<cols) && (V_Projection[i]<UMBRAL_VERTICAL))
      {
        contador++;
        i++;
      }
    if (i<=cols && contador>0)
      {
        suma_huecos+=contador;
        total_huecos++;
      }
    //  fprintf(stderr,"suma_huecos=%i total_huecos%i \n",suma_huecos,total_huecos);
  }
  // cerr << "separacion " << suma_huecos<< "/" <<total_huecos<< endl;
  if (total_huecos) return(MAX(suma_huecos/total_huecos,SEPARACION_MIN_LETRAS));
  else return(INT_MAX);
 }
