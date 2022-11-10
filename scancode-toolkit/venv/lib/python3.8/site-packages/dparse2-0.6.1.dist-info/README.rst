=================
Dependency Parser
=================


A parser for Python manifests and dependency files now at 
https://github.com/nexB/dparse2

Originally at https://github.com/pyupio/dparse

This is a maintained fork by some of the contributors since upstream stopped
updating this.


Supported Files
---------------

+------------------+------------+
| File             | parse      |
+==================+============+
| conda.yml        | yes        |
+------------------+------------+
| tox.ini          | yes        |
+------------------+------------+
| Pipfile          | yes        |
+------------------+------------+
| Pipfile.lock     | yes        |
+------------------+------------+

************
Installation
************

To install dparse2, run:

.. code-block:: console

    $ pip install dparse2

If you want to update Pipfiles, install the pipenv extra:

.. code-block:: console

    $ pip install dparse2[pipenv]

*****
Usage
*****

To use dparse2 in a Python project::

    from dparse2 import parse
    from dparse2 import filetypes

    content = """
    South==1.0.1 --hash=sha256:abcdefghijklmno
    pycrypto>=2.6
    """

    df = parse(content, file_type=filetypes.requirements_txt)

    print(df.json())


    {
      "file_type": "requirements.txt",
      "content": "\nSouth==1.0.1 --hash=sha256:abcdefghijklmno\npycrypto>=2.6\n",
      "path": null,
      "sha": null,
      "dependencies": [
        {
          "name": "South",
          "specs": [
            [
              "==",
              "1.0.1"
            ]
          ],
          "line": "South==1.0.1 --hash=sha256:abcdefghijklmno",
          "source": "pypi",
          "meta": {},
          "line_numbers": null,
          "index_server": null,
          "hashes": [
            "--hash=sha256:abcdefghijklmno"
          ],
          "dependency_type": "requirements.txt",
          "extras": []
        },
        {
          "name": "pycrypto",
          "specs": [
            [
              ">=",
              "2.6"
            ]
          ],
          "line": "pycrypto>=2.6",
          "source": "pypi",
          "meta": {},
          "line_numbers": null,
          "index_server": null,
          "hashes": [],
          "dependency_type": "requirements.txt",
          "extras": []
        }
      ]
    }



This tool supports Python 3.6 and up. Older version support older Python versions
