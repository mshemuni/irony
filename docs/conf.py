# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'irony'
copyright = '2022, Mohammad S.Niaei'
author = 'Mohammad S.Niaei'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    # 'sphinxawesome_theme'
]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'


html_theme_options = {
    'github_user': 'mshemuni',
    'github_repo': 'irony',
    'fixed_sidebar': 'true',
    'sidebar_collapse': 'ture',
    'link': '#cf5b65',
    'link_hover': '#cf5b65',
    'code_font_family': 'Monospace'
}

html_static_path = ['_static']
html_favicon = 'iront_icon.svg'
html_logo = "irony.svg"
