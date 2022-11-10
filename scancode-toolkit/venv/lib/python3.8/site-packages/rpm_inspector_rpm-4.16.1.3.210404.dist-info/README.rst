A ScanCode Toolkit plugin to provide pre-built binary libraries and utilities
and their locations. This is for the RPM command which is built from sources
with the support for many rpmdb formats.


This is built on Debian/Ubuntu with these dependencies::

    $ sudo apt-get install -y \
        libsqlite3-dev \
        libgcrypt20-dev \
        libbz2-dev \
        liblzma-dev \
        libpopt-dev \
        libzstd1-dev

These are the runtime dependencies::

    $ sudo apt-get install -y \
        libsqlite3-0 \
        libgcrypt20 \
        libbz2-1.0 \
        liblzma5 \
        libpopt0 \
        libzstd1