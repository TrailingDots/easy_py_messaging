#!/bin/bash
#
# Get a word count of source files.
#
echo =========== All files ==============
/usr/bin/wc `find . -name '*.py'   | grep -v \.coverage_html` \
            `find . -name '*.html' | grep -v \.coverage_html` \
            `find . -name '*.css'  | grep -v \.coverage_html` \
            `find . -name '*.js'   | grep -v \.coverage_html` \
            `find . -name '*.md'   | grep -v \.coverage_html` \
            `find . -name '*.sh'   | grep -v \.coverage_html`
echo
echo ========== Python files ==============
/usr/bin/wc `find . -name '*.py'   | grep -v \.coverage_html` 
