# Configuration file for the Sphinx documentation builder.
import sphinx_rtd_theme
# pyshell must be installed for this import to work
import pyshell
# -- Project information

project = pyshell.__title__
copyright = pyshell.__copyright__
author = pyshell.__author__
version = pyshell.__version__

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output
# import sphinx_bootstrap_theme

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
pygments_style = 'sphinx'
html_theme_options = {
    'collapse_navigation': False,
    'display_version': False,
}
# html_theme = 'bootstrap'
# html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# -- Options for EPUB output
epub_show_urls = 'footnote'
intersphinx_mapping = {"python": ("https://docs.python.org/3.9", None)}
