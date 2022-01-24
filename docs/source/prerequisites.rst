.. SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
.. SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
..
.. SPDX-License-Identifier: AGPL-3.0-only

Prerequisites
===================================

In order to contribute to Hermine, you'll need to ensure to fit with the following rules.


DCO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hermine uses the Developer Certificate of Origin Version 1.1.

To be able to push commits through the Hermine's CI, you'll need to sign off every commit you make. In order to do that, you'll first want to enable a GPG key in GitLab. You can check if you already have a GPG key generated on your computer by typing in your terminal:


.. code-block:: bash

    $ gpg --list-secret-keys --keyid-format=long

If you don't have a GPG, see GitHub's `documentation <https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key>`_ to quickly generate one. Then, ensure you're using the right GPG key by typing:


.. code-block:: bash

    git config --global user.signingKey SHORTNAMEOFYOURGPGKEY

Once your public GPG is configured and added to GitLab, you should be able to sign your commits with command commit like:


.. code-block:: bash

    $ git commit -S -m "your commit message"

You are also able to sign every commit by default by typing


.. code-block:: bash

    git config --global commit.gpgsign true


REUSE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Hermine software is REUSE-compliant. It means every file is clearly license marked at the top of the file, like the following template:


.. code-block:: python

    # SPDX-FileCopyrightText: 2021 Hermine-team <hermine@inno3.fr>
    #
    # SPDX-License-Identifier: AGPL-3.0-only

To ensure REUSE-compliance, a CI pipeline is set. In order to properly write those headers, you'll want to use the REUSE helper tool packages within the virtualenv:


.. code-block:: bash

    reuse addheader --copyright="Hermine-team <hermine@inno3.fr>" --license="AGPL-3.0-only"  your_awesome_new_file.py
    