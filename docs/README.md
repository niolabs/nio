n.io SDK Documentation
======================

This README is intended to document how to build and deploy the documentation.

Setup
-----

```bash
pip install sphinx sphinx_rtd_theme
```

Building
--------

```bash
cd nio-sdk/docs
make html
```

Viewing the docs locally
------------------------

```bash
open build/html/index.html
```

Updating API Documentation
--------------------------

This is only needed if the code structure changes. Actual code and docstring
updates will be captured by the `make` command.

Run these command from the `docs` folder:

```bash
rm -rf sdk/*
sphinx-apidoc -T -f -E -M -o sdk ../nio
```
