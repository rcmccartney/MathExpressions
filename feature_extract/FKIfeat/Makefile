FLAGS=-O3

fkifeat: fkifeat.o libpbm.o
	g++ -o fkifeat fkifeat.o libpbm.o $(FLAGS)

fkifeat.o: fkifeat.cc
	g++ -c fkifeat.cc $(FLAGS)

libpbm.o: libpbm.c libpbm.h
	g++ -c libpbm.c $(FLAGS)

clean:
	rm -f *.o *~
