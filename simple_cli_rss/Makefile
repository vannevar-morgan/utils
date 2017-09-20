OBJS_MAIN = main.o
CC = g++
CFLAGS = -c -Wall -std=c++11
LFLAGS = -Wall -lcurl -lcurlpp

all : rss

rss : $(OBJS_MAIN)
	$(CC) -o rss $(OBJS_MAIN) $(LFLAGS)

main.o : main.cpp
	$(CC) $(CFLAGS) main.cpp

clean:
	\rm -rf *.o
