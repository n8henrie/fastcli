# fastcli

[![master branch build
status](https://github.com/n8henrie/fastcli/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/n8henrie/fastcli/actions/workflows/python-package.yml)

Python3 CLI script for fast.com

- Free software: MIT
- Documentation: https://fastcli.readthedocs.org

## Features

Shows approximate download speed by way of Fast.com.

## Introduction

Fast.com is a newish Netflix download speed test. It bases its results on
download speed of actual Netflix video content, which makes it much harder for
ISPs to embellish their results (without also speeding up all of Netflix, which
may account for as much as 30% of all internet traffic).

It doesn't test upload speed or ping, so `fastcli` doesn't either.

## Dependencies

- Python >= 3.5
- See `requirements.txt`

## Quickstart

```bash
pip3 install fastcli
fastcli
```

### Development Setup

1. Clone the repo: `git clone https://github.com/n8henrie/fastcli && cd
   fastcli`
1. Install into a virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install .[dev]
```

## Configuration

- Optionally accepts a `--runtime` argument which may affect accuracy by
  changing to values shorter or longer than the default of 10 (seconds).

## Acknowledgements

- Netflix, for creating [Fast.com](https://fast.com)
- Many thanks to groundwork laid by <https://github.com/sanderjo/fast.com>

## Troubleshooting / FAQ

- fastcli requires Python >= 3.5
