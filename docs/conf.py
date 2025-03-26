# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'lensql'
copyright = '2025, Davide Ponzini'
author = 'Davide Ponzini'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'autoapi.extension',
    # 'sphinx.ext.inheritance_diagram',
    # 'autoapi.sphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# -- Autoapi -----------------------------------------------------------------
autoapi_dirs = ['../src']
autodoc_typehints = 'description'
autoapi_options = [ 'members', 'private-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members', ]
