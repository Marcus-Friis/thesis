#-----------------------------------------------------------------------
# File    : makefile    (directory: moss)
# Contents: build molecular substructure miner (MoSS aka MoFa)
# Author  : Christian Borgelt
# History : 2002.07.16 file created
#           2006.05.13 other compilers added
#           2006.07.18 creation of a jar for the GUI version added
#           2006.10.25 creation of javadoc added
#           2019.04.16 html version selection added to javadoc call
#-----------------------------------------------------------------------
SHELL=/bin/bash

all:        moss predict

#-----------------------------------------------------------------------
# Molecular Substructure Miner
#-----------------------------------------------------------------------
moss:   *.java
	cd ..; javac -Xlint moss/MoSS.java
#	cd ..; \
#       gcj -O3 -Wall --main=moss.MoSS  moss/*.java -o moss/mossgui; \
#       gcj -O3 -Wall --main=moss.Miner moss/*.java -o moss/moss

#-----------------------------------------------------------------------
# Edge Predictor
#-----------------------------------------------------------------------
predict: *.java
	cd ..; javac -Xlint moss/Predictor.java

#-----------------------------------------------------------------------
# Distribution Packages
#-----------------------------------------------------------------------
dist:
	$(MAKE) clean jdoc src jdclean

src:
	cd ..; \
        zip -rq moss.zip \
            moss/{*.java,makefile,run,bench,doc} \
            moss/data/{*.smi,*.sln,example.nel,babab.nel} \
            -x moss/data/ic93.sln; \
        tar cfz moss.tar.gz \
            --exclude=moss/data/ic93.sln \
            moss/{*.java,makefile,run,bench,doc} \
            moss/data/{*.smi,*.sln,example.nel,babab.nel} \

jar:    moss
	cd ..; \
	echo "Main-Class: moss.MoSS" > manifest; \
	jar cfm moss.jar manifest moss/*.class; \
	rm -f manifest

#-----------------------------------------------------------------------
# Documentation
#-----------------------------------------------------------------------
jdoc:
	cd doc/java; rm -rf *; \
        javadoc -html5 -quiet -classpath ../../.. moss

#-----------------------------------------------------------------------
# Installation
#-----------------------------------------------------------------------
install:    jar
	cd ..; mv moss.jar $(HOME)/bin

#-----------------------------------------------------------------------
# Clean up
#-----------------------------------------------------------------------
clean:
	rm -f *.class *.sub *.ids *.tmp moss mossgui

jdclean:
	rm -rf doc/java/*
