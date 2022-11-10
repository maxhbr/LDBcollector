Release notes
=============

Version 30.0.0
-----------------

- Drop Calver
- Fix minor bugs
- Upgrade dependencies
- Adopt black style


Version 21.6.1
---------------

- Disable tracing that had been left enabled by mistake


Version 21.5.31
---------------

(yanked from PyPI)

- Update vendored pygments to 2.9.0
- Update commoncode to latest version
- Use new libmagic configuration based on a plugin, and environment variable
  or the system path.
- Only do content-based detection for programing language if there is no extension.
- Remove Actionscript3 from programing language detection. This is not common
  enough and is the source of too many false positives.


Version 21.2.24
---------------

- Update typecode-libmagic in particular on macOS for v11/Big Sur support


Version 21.1.21
---------------

- Update typecode-libmagic
- Drop using the standard library mimetypes modules because of
  https://github.com/nexB/typecode/issues/14
- Fix testing issues and testing requirements
- Update documentation and comments
- Uupdate to use latest commoncode


Version 21.1.9.1
----------------

- Work around Python bug https://github.com/nexB/typecode/issues/14


Version 21.1.9
----------------

- Remove Python 2
- Switch to plain Apache license per https://github.com/nexB/scancode-toolkit/issues/2337
- Improve documentation
- Enable Ci on more OS/Python combos


Version 21.1.8.1
----------------

- Upgrade to latest boilerplate skeletton
- Improve detection of Windows executables 


Version 20.10.20
----------------

- Roll back Pygments and vendor with vendy


Version 20.10
-------------

- Code for content-based lexers from Pygments has been updated from v 2.2.0 to v 2.7.1
- Create data driven filetype tests and update test expectations


Version 20.09
-------------

- Initial release.
