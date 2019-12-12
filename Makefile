.PHONY: paper

package=cloudmesh_pi_burn
UNAME=$(shell uname)
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

source:
	$(call banner, "Install cmburn")
	pip install -e . -U

requirements:
	pip-compile setup.py
	fgrep -v "# via" requirements.txt > tmp.txt
	mv tmp.txt requirements.txt

test:
	pytest -v --html=.report.html
	open .report.html

dtest:
	pytest -v --capture=no

clean:
	$(call banner, "CLEAN")
	rm -rf *.zip
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	find . -type d -name __pycache__ -delete
	find . -name '*.pyc' -delete
	rm -rf .tox
	rm -f *.whl

######################################################################
# PYPI
######################################################################

paper: manual
	cd paper; make

manual:
	cm-burn -h > paper/manual.md

view:
	#open docs/vonLaszewski-cmburn.pdf
	open -a skim docs/vonLaszewski-cmburn.pdf


######################################################################
# PYPI
######################################################################


twine:
	pip install -U twine

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

patch: clean
	$(call banner, "patch")
	bump2version --allow-dirty patch
	python setup.py sdist bdist_wheel
	git push origin master --tags
	twine check dist/*
	twine upload --repository testpypi  dist/*
	# $(call banner, "install")
	# pip search "cloudmesh" | fgrep $(package)
	# sleep 10
	# pip install --index-url https://test.pypi.org/simple/ $(package) -U

minor: clean
	$(call banner, "minor")
	bump2version minor --allow-dirty
	@cat VERSION
	@echo

release: clean
	$(call banner, "release")
	git tag "v$(VERSION)"
	git push origin master --tags
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo


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
	pip install --index-url https://test.pypi.org/simple/ $(package) -U

#	    --extra-index-url https://test.pypi.org/simple

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push

# bump:
#	git checkout master
#	git pull
#	tox
#	python setup.py sdist bdist_wheel upload
#	bumpversion --no-tag patch
#	git push origin master --tags


# API_JSON=$(printf '{"tag_name": "v%s","target_commitish": "master","name": "v%s","body": "Release of version %s","draft": false,"prerelease": false}' $VERSION $VERSION $VERSION)
# curl --data "$API_JSON" https://api.github.com/repos/:owner/:repository/releases?access_token=:access_token

