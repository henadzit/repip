# repipe

[![PyPI - Version](https://img.shields.io/pypi/v/repipe.svg)](https://pypi.org/project/repipe)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/repipe.svg)](https://pypi.org/project/repipe)

Yet another one attempt to fix Python package management.

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install repipe
```

## Usage

`repipe install -r requirements.txt`

will create a lock file `requirements.txt.lock`. The next execution of `repipe install -r requirements.txt` will install dependencies from `requirements.txt.lock`. If you need to update dependencies, remove `requirements.txt.lock`.

## License

`repipe` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
