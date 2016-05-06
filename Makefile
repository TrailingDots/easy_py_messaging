DESTDIR=/
PROJECT=simple_log_messaging
BUILDDIR=$(CURDIR)/$(PROJECT)
LIBDIR=$(CURDIR)/$(PROJECT)
TOOLSDIR=$(CURDIR)/$(PROJECT)
LOCALDIR=$(HOME)/.local

# Future versions may use python3
PYTHON=/usr/bin/python2.7

RM=/usr/bin/rm

RM=/usr/bin/rm
CP=/usr/bin/cp

all: clean
	$(PYTHON) setup.py sdist --formats=zip,gztar 

help:
	@echo "make - Build source distributable package. Test locally"
	@echo "make test - Run test suite. Capture with 'script' command."
	@echo "make install - install on local system"
	@echo "make backup - Create tgz backup one dir above base dir."
	@echo "make wc - Perform word count for ine counts."
	@echo "make clean - Get rid of scratch files"

source:
	$(PYTHON) setup.py sdist $(COMPIE)

test:
	(cd $(PROJECT); ./runTests.sh)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

wc:
	$(PROJECT)/wc.sh

backup:
	$(PROJECT)/backup.sh

# Due to difficulties in creating a package, kludge cleaning out the
# code to track difficulties and installing in various ways.
clean:
	$(PYTHON) setup.py clean
	$(RM) -rf build/ dist/ $(PROJECT).egg-info/
	find . -name logs.log -delete
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	sudo $(RM) -rf /usr/lib/python2.7/site-packages/$(PROJECT)
	sudo $(RM) -rf /usr/lib/python2.7/site-packages/$(PROJECT)-*
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)-*
	-for APP in logCollector listeningPort logCmd logFilterApp; do \
		sudo $(RM) -f /usr/bin/$$APP || true; \
		$(RM) $(LOCALDIR)/bin/$$APP; \
	done

