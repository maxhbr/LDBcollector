# SPDX-FileCopyrightText: 2022 Martin Delabre <gitlab.com/delabre.martin>
#
# SPDX-License-Identifier: CC-BY-4.0

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import django
import inspect
from django.utils.html import strip_tags


# Specify settings module
sys.path.insert(0, os.path.abspath("../../hermine"))
# sys.path.append(os.path.abspath("../../hermine/"))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hermine.settings")

django.setup()


# -- Project information -----------------------------------------------------

project = "Hermine"
copyright = "2021, Hermine Team"
author = "Hermine Team"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.autosectionlabel"]
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_theme_options = {
    "analytics_id": "G-XXXXXXXXXX",  #  Provided by Google in your dashboard
    "analytics_anonymize_ip": False,
    "logo_only": True,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    # Toc options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}

html_logo = "./img/LogoHermine_noBG.png"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]


def process_docstring(app, what, name, obj, options, lines):
    from django.db import models

    if inspect.isclass(obj) and issubclass(obj, models.Model):
        fields = obj._meta.fields

        for field in fields:
            help_text = strip_tags(field.help_text)
            verbose_name = field.verbose_name
            lines.append(f":param {field.attname}: {help_text or verbose_name}")

            if field.choices is not None:
                lines[-1] += (
                    ". Possible values: "
                    + ", ".join(db_value for (db_value, label) in field.choices)
                    + "."
                )

            lines.append(":type %s: %s" % (field.attname, type(field).__name__))

    return lines


def setup(app):
    app.connect("autodoc-process-docstring", process_docstring)
