#!/bin/bash
#
# Get a word count of source files.
#
echo =========== All programmatic text files ==============
/usr/bin/wc `find . -name '*.py'   | grep -v \.coverage_html` \
            `find . -name '*.html' | grep -v \.coverage_html` \
            `find . -name '*.css'  | grep -v \.coverage_html` \
            `find . -name '*.js'   | grep -v \.coverage_html` \
            `find . -name '*.md'   | grep -v \.coverage_html` \
            `find . -name '*.css'  | grep -v \.coverage_html` \
            `find . -name Makefile | grep -v \.coverage_html` \
            `find . -name '*.sh'   | grep -v \.coverage_html`
echo
echo ========== Python only files ==============
/usr/bin/wc `find . -name '*.py'   | grep -v \.coverage_html` 
