PYTHON=`which python`
DESTDIR=/
PROJECT=simple_log_messaging
BUILDDIR=$(CURDIR)/debian/$(PROJECT)

# $(PYTHON) setup.py build
# Generate a distributable package.
# Test this by installing locally - over and over!!!
all:
	$(PYTHON) setup.py sdist

help:
	@echo "make - Build source distributable package. Test locally"
	@echo "make test - Run test suite. Capture with 'script' command."
	@echo "make install - install on local system"
	@echo "make buildrpm - Generate an rpm package"
	@echo "make backup - Create tgz backup one dir above base dir."
	@echo "make wc - Perform word count for ine counts."
	@echo "make clean - Get rid of scratch files"

source:
	$(PYTHON) setup.py sdist $(COMPIE)

test:
	(cd src; ./runTests.sh)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

wc:
	./tools/wc.sh

backup:
	./tools/backup.sh

clean:
	$(PYTHON) setup.py clean
	rm -rf build/ dist/
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name typescript -delete



