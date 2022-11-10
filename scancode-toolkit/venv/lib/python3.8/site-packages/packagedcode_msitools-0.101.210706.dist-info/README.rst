A ScanCode Toolkit plugin to provide pre-built binary libraries and utilities
and their locations. This is for the executable binaries from msitools, which is
built from source. Only msiinfo is packaged and exposed in this LocationProvider
plugin.


This is built on Debian/Ubuntu in a Python virtualenv with these dependencies::

    $ sudo apt-get install -y \
        valac \
        perl \
        bison \
        libglib2.0-dev \
        libgsf-1-dev \
        libgirepository1.0-dev \
        libxml2-dev
    $ pip install meson ninja wheel
