BINARIES=	get_Hyb_Feat
CC	=	g++
LIBS	=	-lm
CFLAGS	=	-O3
OBJ	=	online.o read.o features.o main.o offline.o


all: $(BINARIES)

$(BINARIES): $(OBJ)
	$(CC) $(CFLAGS) -o $(BINARIES) *.o $(LIBS)

main.o: main.cc online.h read.h features.h offline.h
	$(CC) $(CFLAGS) -c $< -o $@

features.o: features.cc features.h online.h offline.h
	$(CC) $(CFLAGS) -c $< -o $@

read.o: read.cc read.h online.h offline.h
	$(CC) $(CFLAGS) -c $< -o $@

online.o: online.cc online.h
	$(CC) $(CFLAGS) -c $< -o $@

offline.o: offline.cc offline.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	-rm -f *.o *~ gmon.out $(BINARIES)
