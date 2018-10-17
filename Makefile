# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install deploy

install: README.rst
	python setup.py install

test:
	python setup.py test

README.rst: README.md
	- pandoc $< -o $@
	@touch $@

deploy: README.rst
	git push
	git push --tags
	rm -rf dist
	python setup.py bdist_wheel
	python3 setup.py bdist_wheel
	twine upload dist/*
