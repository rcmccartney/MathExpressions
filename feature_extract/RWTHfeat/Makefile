FLAGS=-O3

rwthfeat: rwthfeat.o libpgm.o libpbm.o
	g++ -o rwthfeat rwthfeat.o libpgm.o libpbm.o $(FLAGS)

rwthfeat.o: rwthfeat.cc
	g++ -c rwthfeat.cc $(FLAGS)

libpgm.o: libpgm.c libpgm.h libpbm.o
	g++ -c libpgm.c $(FLAGS)

libpbm.o: libpbm.c libpbm.h
	g++ -c libpbm.c $(FLAGS)

clean:
	rm -f *.o *~
