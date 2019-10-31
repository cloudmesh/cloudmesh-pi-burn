.PHONY: paper

paper: manual
	cd paper; make

manual:
	cm-burn -h > paper/manual.md

view:
	#open docs/vonLaszewski-cmburn.pdf
	open -a skim docs/vonLaszewski-cmburn.pdf
