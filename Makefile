DESTDIR=/
PROJECT=easy_py_messaging
BUILDDIR=$(CURDIR)/$(PROJECT)
LIBDIR=$(CURDIR)/$(PROJECT)
TOOLSDIR=$(CURDIR)/$(PROJECT)
LOCALDIR=$(HOME)/.local

# Future versions may use python3
PYTHON=/usr/bin/python2.7

RM=/usr/bin/rm

RM=/usr/bin/rm
CP=/usr/bin/cp
CHMOD=/usr/bin/chmod

# The files that will likely used as stand-alone applications.
APP_FIILES=client_create_basic \
	client_create_skeleton \
	client_create_test \
	client_sync \
	demoSocket \
	dirClient \
	dirSvc \
	logCmd \
	logCollector \
	logFilterApp \
	loggingClientTask \
	loggingLoopApp \
	loggingSpeedTest \
	server_create_basic \
	server_create_test

all: create_apps 
	echo Making all
	echo APP_FILES=$(echo $APP_FILES)
	$(PYTHON) setup.py sdist --formats=zip,gztar 

# Have to go through file renaming because the python
# setup.py install process is SSSOOO clumsy! Yuck!!
create_apps: clean_bin
	echo Making create_apps
	# Create bin dir if it does not exist.
	-mkdir $(PROJECT)/bin
	echo App files: $APP_FILES
	(cd $(PROJECT); \
		for FILE in $$APP_FILES; do \
			$(CP) $$FILE bin; \
			$(CHMOD) a+x bin/$$FILE; \
		done;)
	ls -l $(PROJECT)/bin
	exit

# Clear out the bin dir in the primary working directory.
clean_bin:
	echo Making clean_bin
	(cd $(PROJECT); $(RM) -rf bin; mkdir bin; touch bin/__init__.py)

help:
	@echo "make - Build source distributable package. Test locally"
	@echo "make test - Run test suite. Capture with 'script' command."
	@echo "make install - install on local system"
	@echo "make backup - Create tgz backup one dir above base dir."
	@echo "make wc - Perform word count for ine counts."
	@echo "make clean - Get rid of scratch files"

source:
	$(PYTHON) setup.py sdist $(COMPILE)

test:
	(cd $(PROJECT)/$(PROJECT); ./runTests.sh)

install: create_apps
	echo Making install
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

wc:
	$(PROJECT)/wc.sh

backup:
	$(PROJECT)/backup.sh

# Due to difficulties in creating a package, kludge cleaning out the
# code to track difficulties and installing in various ways.
clean:
	echo Making clean
	$(PYTHON) setup.py clean
	$(RM) -rf build/ dist/ $(PROJECT).egg-info/
	find . -name logs.log -delete
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	sudo $(RM) -rf /usr/lib/python2.7/site-packages/$(PROJECT)
	sudo $(RM) -rf /usr/lib/python2.7/site-packages/$(PROJECT)-*
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)
	$(RM) -rf $(LOCALDIR)/lib/python2.7/site-packages/$(PROJECT)-*
	-for APP in logCollector logCmd logFilterApp; do \
		sudo $(RM) -f /usr/bin/$$APP || true; \
		$(RM) $(LOCALDIR)/bin/$$APP; \
	done


