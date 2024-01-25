# repip

[![PyPI - Version](https://img.shields.io/pypi/v/repip.svg)](https://pypi.org/project/repip)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/repip.svg)](https://pypi.org/project/repip)

Yet another one attempt to fix Python package management.

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install repip
```

## Usage

`repip install -r requirements.txt`

will create a lock file `requirements.txt.lock`. The next execution of `repip install -r requirements.txt` will install dependencies from `requirements.txt.lock`. If you need to update dependencies, remove `requirements.txt.lock`.

## License

`repip` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
