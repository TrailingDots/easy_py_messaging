#
#
#
PROJECT=easy_py_messaging
LOCALDIR=$(HOME)/.local

# Future versions may use python3
PYTHON=/usr/bin/python2.7

# Where site packages get installed
SITE=/usr/lib/python2.7/site-packages

RM=/usr/bin/rm

RM=/usr/bin/rm
CP=/usr/bin/cp
CHMOD=/usr/bin/chmod

all:
	$(PYTHON) setup.py bdist

install: all

help:
	@echo "make - Build source distributable package. Test locally"
	@echo "make test - Run test suite. Capture with 'script' command."
	@echo "make install - create install package for pip on local system"
	@echo "make wc - Perform word count for ine counts."
	@echo "make clean - Get rid of scratch files"

test:
	(cd $(PROJECT); ./runTests.sh)

wc:
	$(PROJECT)/wc.sh

backup:
	./backup.sh

# Due to difficulties in creating a package, kludge cleaning out the
# code to track difficulties and installing in various ways.
clean:
	$(PYTHON) setup.py clean
	(cd $(PROJECT); $(RM) -rf bin dist $(PROJECT).egg-info)
	find . -name logs.log -delete
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	$(RM) -rf build dist easy_py_messaging.egg-info
	sudo $(RM) -rf $(SITE)/$(PROJECT)
	sudo $(RM) -rf $(SITE)/$(PROJECT)-*
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)-*


