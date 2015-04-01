FLAGS=-O3

offpolarfeat: offpolarfeat.o polarhist.o libpgm.o libpbm.o
	g++ -o offpolarfeat offpolarfeat.o polarhist.o libpgm.o libpbm.o $(FLAGS)

offpolarfeat.o: offpolarfeat.cc
	g++ -c offpolarfeat.cc $(FLAGS)

polarhist.o: polarhist.h polarhist.cc
	g++ -c polarhist.cc $(FLAGS)

libpgm.o: libpgm.c libpgm.h libpbm.o
	g++ -c libpgm.c $(FLAGS)

libpbm.o: libpbm.c libpbm.h
	g++ -c libpbm.c $(FLAGS)

clean:
	rm -f *.o *~
