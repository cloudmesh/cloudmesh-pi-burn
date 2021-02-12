package=pi-burn
UNAME=$(shell uname)
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "###################################"
	@echo $(1)
	@echo "###################################"
endef

all: install

flake8:
	flake8 --max-line-length 124 --ignore=E722 cloudmesh
	flake8 --max-line-length 124 --ignore=E722 tests



install:
	pip install -e .

readme: parts
	cms man readme -p --toc
	cms man readme -p --tag="MANUAL-BURN" --command=burn
	cms man readme -p --tag="MANUAL-BRIDGE" --command=bridge
	cms man readme -p --tag="MANUAL-HOST" --command=host
	cms man readme -p --tag="MANUAL-PI" --command=pi

parts:
	python bin/parts.py > tmp.md 2>&1
	cms man readme -p --tag="PARTS" --file=README-parts.md --include=tmp.md
	rm -rf tmp.md

source:
	cd ../cloudmesh.cmd5; make source
	$(call banner, "Install cloudmesh-{package}")
	pip install -e . -U
	cms help

#requirements:
#	echo "cloudmesh-cmd5" > tmp.txt
#	echo "cloudmesh-sys" >> tmp.txt
#	echo "cloudmesh-inventory" >> tmp.txt
#	echo "cloudmesh-configuration" >> tmp.txt
#	# pip-compile setup.py
#	#fgrep -v "# via" requirements.txt | fgrep -v "cloudmesh" >> tmp.txt
#	mv tmp.txt requirements.txt
#	-git commit -m "update requirements" requirements.txt
#	-git push

manual:
	mkdir -p docs-source/source/manual
	cms help > /tmp/commands.rst
	echo "Commands" > docs-source/source/manual/commands.rst
	echo "========" >> docs-source/source/manual/commands.rst
	echo  >> docs-source/source/manual/commands.rst
	tail -n +4 /tmp/commands.rst >> docs-source/source/manual/commands.rst
	cms man --kind=rst burn > docs-source/source/manual/admin.rst
	cms man --kind=rst foo > docs-source/source/manual/banner.rst

doc:
	rm -rf docs
	mkdir -p dest
	cd docs-source; make html
	cp -r docs-source/build/html/ docs

view:
	open docs/index.html

#
# TODO: BUG: This is broken
#
#pylint:
#	mkdir -p docs/qc/pylint/cm
#	pylint --output-format=html cloudmesh > docs/qc/pylint/cm/cloudmesh.html
#	pylint --output-format=html cloud > docs/qc/pylint/cm/cloud.html

clean:
	$(call banner, "CLEAN")
	rm -rf dist
	rm -rf *.zip
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	rm -rf .tox
	rm -f *.whl

######################################################################
# PYPI
######################################################################


twine:
	pip install -U twine

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

patch: clean
	$(call banner, "bbuild")
	bump2version --no-tag --allow-dirty patch
	python setup.py sdist bdist_wheel
	git push
	# git push origin master --tags
	twine check dist/*
	twine upload --repository testpypi  dist/*
	# $(call banner, "install")
	# sleep 10
	# pip install --index-url https://test.pypi.org/simple/ cloudmesh-$(package) -U

	#make
	#git commit -m "update documentation" docs
	#git push

minor: clean
	$(call banner, "minor")
	bump2version minor --allow-dirty
	@cat VERSION
	@echo

release: clean
	$(call banner, "release")
	-git tag "v$(VERSION)"
	-git push origin master --tags
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo
	#sleep 10
	#pip install -U cloudmesh-common


dev:
	bump2version --new-version "$(VERSION)-dev0" part --allow-dirty
	bump2version patch --allow-dirty
	@cat VERSION
	@echo

reset:
	bump2version --new-version "4.0.0-dev0" part --allow-dirty

upload:
	twine check dist/*
	twine upload dist/*

pip:
	pip install --index-url https://test.pypi.org/simple/ cloudmesh-$(package) -U

#	    --extra-index-url https://test.pypi.org/simple

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push


