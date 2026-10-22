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
# Tutorials are MyST text notebooks with no stored outputs: the docs build executes them
# (offline, from committed samples; MadGraph never runs here) and fails on any error, so
# `sphinx-build -W` is also the notebook test.
import os

os.environ["HEPANALYSIS_STATIC"] = "1"  # explore cells draw their static plot (hepanalysis.notebook)
nb_execution_mode = "cache"
nb_execution_raise_on_error = True
nb_execution_cache_path = "_build/.jupyter_cache"
nb_execution_timeout = 900
nb_execution_excludepatterns = ["tutorials/data/*"]
# stderr from the reader's local environment (e.g. a broken matplotlib style) is not content
nb_output_stderr = "remove"
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
exclude_patterns = ["_build", "jupyter_execute", ".jupyter_cache", "Thumbs.db", ".DS_Store",
                    "tutorials/data", "**/.ipynb_checkpoints"]
