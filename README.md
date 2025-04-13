# Fitch

Fitch is a simple language for making propositional proofs in a Fitch-style natural deduction system.
The interpreter parses the proofs, renders them as text, and optionally generates a LaTex document.
You can find over 40 example proofs in total in the examples folder.

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
  -l, --latex filename  write a LaTex document with all the proofs to the file path given
  -v, --verify          if used, the output is printed only in case of error in the proof file given
```

## Dependencies

 - `lark` for parsing logical expression and Fitch-style rules

The code was formatted using `black`, with line length 120.
The generated LaTex output uses the `fitch` package, available on [CTAN](https://ctan.org/pkg/fitch).
