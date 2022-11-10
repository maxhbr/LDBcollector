Changelog
=========


v31.0.0 - 2022-08-24
------------------------

- Fix error when using ``get_license_detection_from_nameless_paragraph()`` on
  Debian copyright files who named the license field as ``licence`` #25
- Use latest skeleton
- Bump dependencies
- Drop Python 3.6 support


v30.0.0 - 2021-09-07
------------------------

This is a major incompatible version

- Switch back to semver/semantic versioning
- Add new deb822 parser for tracking line number in copyright files #13
- Track line numbers in copyright files to ensure proper line tracking in
  license detection in https://github.com/nexB/scancode-toolkit/issues/2643
- Drop sort arguments on debcon objects ``dump/s`` methods. This was not
  designed consistently and is not used anywhere.
- Remove deprecated debut module. Use the debian_inspector module instead.
- Adop latest skeleton: this rename virtual environment directory from ``tmp`` to ``venv``


v21.5.25 - 2021-05-25
------------------------

- Adopt calendar versioning, latest skeleton and various cosmetic code formatting
- Fix bug where some content could be dropped from invalid debian file


v0.9.10 - 2021-03-25
--------------------

- Rename module to debian_inspector
- Add compat debut module, marked as deprecated
- Drop support for Python 2
- Fix version parsing bugs using all new code from @xolox


v0.9.9 - 2021-02-12
-------------------

- Relax support for chardet versions
- Add new Contents index parser
- Improve docstrings
- Remove Alpine support (moved to scancode-toolkit)


v0.9.8 - 2020-07-07
-------------------

- Correct setup.py typo


v0.9.7 - 2020-07-07
-------------------

- Correct configure script


v0.9.6 - 2020-07-07
-------------------

- Support parsing Alpine installed db. This is a debian-like file but the keys
  are case-sensitive


v0.9.5 - 2020-06-09
-------------------

- Simplify configure and fix minor bugs


v0.9.4 - 2020-04-28
-------------------

- Add new DebianCopyright.from_text() method to copyright module.


v0.9.3 - 2020-04-20
-------------------

 - Add support for CodeArchive and minor refactorings.


v0.9.2 - 2020-04-17
-------------------

- Initial release.
