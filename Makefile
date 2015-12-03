# This file is part of tidetable.
# https://github.com/fitnr/tidetable

# Licensed under the GPL-3.0 license:
# http://www.opensource.org/licenses/GPL-3.0
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

.PHONY: install upload
install: README.rst
	python setup.py install

README.rst: README.md
	pandoc $< -o $@ || touch $@

upload:
	rm -rf dist
	python setup.py bdist_wheel
	python3 setup.py bdist_wheel
	twine upload dist/*
