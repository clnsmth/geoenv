# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'geoenv'
copyright = '2025, Colin Smith'
author = 'Colin Smith'
release = '0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser',
]

# Configure autodoc
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))  # path to source code
napoleon_numpy_docstring = True  # use numpy
napoleon_google_docstring = False  # not google

templates_path = ['_templates']
exclude_patterns = []

sys.path.insert(0, os.path.abspath("../src/geoenv"))
# Get the current version of geoenv for display in the docs
from importlib.metadata import version
version = version("geoenv")



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "show_powered_by": False,
    "github_user": "clnsmth",
    "github_repo": "geoenv",
    "github_banner": False,
    "show_related": False,
    "note_bg": "#FFF59C",
}

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "index": [
        "sidebarintro.html",
        "sourcelink.html",
        "searchbox.html",
        # "hacks.html"
    ],
    "**": [
        "sidebarlogo.html",
        "localtoc.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
        # "hacks.html",
    ],
}

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False
