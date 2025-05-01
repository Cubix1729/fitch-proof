# Fitch

Fitch is a simple language for making propositional proofs in a Fitch-style natural deduction system.
The interpreter parses the proofs, renders them as text, and optionally generates a LaTeX document.
You can find over 40 example proofs in total in the examples folder.

## Installation

```
git clone https://github.com/Cubix1729/fitch-proof.git
cd fitch-proof
pip install -r requirements.txt
```

The project needs a Python version >=3.10.

## Usage

See the detailed langage explanation in the [documentation](./docs/syntax.md).

The CLI interface program can be found in [src/fitch_cli.py](./src/fitch_cli.py).

```
usage: fitch_cli.py [-h] [-l filename] [-v] filename

A small language to write, verify and format Fitch-style proofs in propositional logic

positional arguments:
  filename              the path to the file containing the proofs to interpret

options:
  -h, --help            show this help message and exit
  -l, --latex filename  write a LaTeX document with all the proofs to the file path given
  -v, --verify          if used, the output is printed only in case of error in the proof file given
```

## Dependencies

 - `lark` for parsing logical expression and Fitch-style rules

The code is formatted using `black`, with line length 120.

The optionally generated LaTeX outputs use the `fitch` package, available on [CTAN](https://ctan.org/pkg/fitch).
