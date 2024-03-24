[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/datanorm)](https://pypi.org/project/datanorm/)
![Build Status](https://github.com/FahrJo/datanorm-python/actions/workflows/ci.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/FahrJo/datanorm-python/badge.svg?branch=main)](https://coveralls.io/github/FahrJo/datanorm-python?branch=main)

## Handling DATANORM 4 files with Python

This library contains a collection of classes to parse DATANORM files in Python. The library follows
[this informal specification](https://docplayer.org/115761786-Technische-spezifikationen-der-datanorm-dateien-in-haufe-lexware.html)
and is compatible with DATANORM 4 files.

## State of the library

This library is still under development and the API might still change a little bit. At the moment
it supports parsing of the following files:

- **DATANORM 4 Artikelstammdatendatei** (without `Dimensionssatz` and `Langtextsatz`)
- **DATANORM 4 Preisdatendatei**
- **DATANORM 4 Warengruppendatei**

Support for writing/updating Datanorm files is possible, but not yet implemented.

## Installation

The InvenTree python library can be easily installed using PIP:

```bash
pip install datanorm
```
