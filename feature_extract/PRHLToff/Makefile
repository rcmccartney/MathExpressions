OBJECTS=features.o  main.o  imageClass.o
LIBS=-ljpeg -lpng -lm
OPTI=-O3

all: featExtOffLine

featExtOffLine: $(OBJECTS)
	 g++ -o featExtOffLine $(OBJECTS) $(OPTI) $(LIBS)

features.o:  features.cc features.h
	g++ -c features.cc $(OPTI) $(LIBS)

main.o: main.cc
	g++ -c main.cc $(OPTI) $(LIBS)

imageClass.o: imageClass.cc
	 g++ -c imageClass.cc $(OPTI) $(LIBS)

clean       : 
	rm -rf $(OBJECTS) featExtOffLine
