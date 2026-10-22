"""Sphinx configuration for the hepanalysis documentation site (mirrors feynlag's)."""

project = "hepanalysis"
copyright = "2026, Moises Zeleny"
author = "Moises Zeleny"
release = "0.0.1"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}
myst_enable_extensions = ["dollarmath", "amsmath", "colon_fence", "deflist"]
# tutorials ship solved (executed outputs committed); MadGraph never runs on a docs build
nb_execution_mode = "off"
# ledgers link to repo files outside docs/ (model_requests/, scripts/); those are not pages
suppress_warnings = ["myst.xref_missing"]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

html_theme = "furo"
html_title = "hepanalysis"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
