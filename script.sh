#!/bin/bash

PDF_DIR = "./pdfs"
OUT_DIR = './named_files'
mkdir $OUT_DIR

# FOR ALL FILES IN DIRECTORY
for FILENAME in $(ls ${PDF_DIR})
do

	# ONLY CONTINUE IF FILE IS PDF
	PDF='.pdf'
	if [[ $FILENAME != *"$PDF"* ]]; then
		break
	fi

	# TRY ARXIV
	curl -s https://arxiv.org/abs/${FILENAME%.pdf} | grep -o "<title>.*</title>" >> temp.txt

	# TRY DL.ACM
	if grep -q 'not recognized' temp.txt; then
		: > temp.txt
	        wget -q -O - https://dl.acm.org/doi/10.1145/${FILENAME%.pdf} | grep "<title>.*</title>" >> temp.txt
	fi

	# GRAB TITLE (FROM FIRST <TITLE> TAG>)
	title=$(head -1 temp.txt)

	# CLEAN TITLE
	tag1="<title>"
	tag2="</title>"
	title=${title#"$tag1"}
	title=${title%"$tag2"}
	title=${title// /_}

	# CREATE NEW FILE WITH TITLE
	echo ${title} found for $FILENAME
	scp ${PDF_DIR}${FILENAME} ${OUT_DIR}/${title}.pdf

	# EMPTY BUFFER
	: > temp.txt
done

rm temp.txt
