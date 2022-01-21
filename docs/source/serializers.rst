.. SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
..
.. SPDX-License-Identifier: CC-BY-4.0

Serializers
===================================

Serializers allow complex data such as querysets and model instances to be converted to native Python datatypes that can then be easily rendered into JSON, XML or other content types.
Serializers also provide deserialization, allowing parsed data to be converted back into complex types, after first validating the incoming data. Here the serialization is based on the Django REST Framework (DRF).

Those serializers are mainly used for the API and for import / export functions.

.. automodule:: cube.serializers
    :members:
