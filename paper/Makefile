PANDOC = pandoc
OUTPUT = ../docs

FLAGS = \
	-F pandoc-crossref \
	-f markdown \
	--pdf-engine=pdflatex \
	--filter table-filter.py \
	--filter=pandoc-citeproc \
	--bibliography=bibliography.bib \
	--csl=bibliography.csl \
	-s

FLAGS_TEX =
	--bibliography=bibliography.bib \
	--csl=bibliography.csl \
	-s \
	-F pandoc-crossref

FLAGS_PDF = --template=template.latex

all: vonLaszewski-cmburn.pdf

mkdir:
	@if [ ! -e build ]; then mkdir build; fi

%.pdf : %.md | mkdir
	$(PANDOC) -o $(OUTPUT)/$@ $(FLAGS) $(FLAGS_PDF) metadata.yaml $<

%.tex : %.md | mkdir
	$(PANDOC) -o $(OUTPUT)/$@ $(FLAGS_TEX) $(FLAGS_PDF) metadata.yaml $<

clean:
	rm -f docs/vonLaszewski-cmburn.pdf
