# Fitch


Fitch is a simple language for making propositional proofs in a Fitch-style natural deduction system.
The interpreter parses the proofs, renders them as text, and optionally generates a LaTex document.
You can find over 40 example proofs in total in the examples folder.


## Usage


See the detailed langage explanation in the [documentation](./docs/syntax.md).

The CLI interface program can be found in [src/fitch_cli.py](./src/fitch_cli.py).

```
usage: fitch_cli.py [-h] [-l LATEX] [-v] filename

A small language to write, verify and format Fitch-style proofs in propositional logic

positional arguments:
  filename           the path to the file containing the proofs to interpret

options:
  -h, --help         show this help message and exit
  -l, --latex LATEX  write a LaTex document with all the proofs, using the 'fitch' package
  -v, --verify       if used, the output is printed only in case of error in the proof file given
```


## Dependencies

 - `lark` for parsing logical expression and Fitch-style rules

The code was formatted using `black`, with line length 120.
The generated LaTex output uses the `fitch` package, available on [CTAN](https://ctan.org/pkg/fitch).

An explanation of the language

|  Logical name  |       Symbol(s)        |
|----------------|------------------------|
|  Proposition   | Any upper case letter  |
|     False      | `⊥`, `False` or `false`|
|   Negation     |      `~` or `¬`        |
|  Conjunction   |      `&` or `∧`        |
|  Disjunction   |      `v` or `∨`        |
|  Conditional   |      `->` or `→`       |
| Biconditional  |     `<->` or `↔`       |
|Single turnstile|     `\|-` or `⊢`       |



|          Rule            |                        Explanation                           |       Symbol(s)       |
|--------------------------|--------------------------------------------------------------|-----------------------|
|         Premise          |                                                              |`Pr`, `PR` or `Premise`|
|        Assumption        |                                                              |`As`, `AS` or `Assumption`|
|       Reiteration        | ![alt text](https://proofs.openlogicproject.org/rules/r.svg) |           `R m`       |
| Conjunction introduction | ![alt text](https://proofs.openlogicproject.org/rules/ai.svg)| `&I m, n` or `∧I m, n`|
|  Conjunction elimination | ![alt text](https://proofs.openlogicproject.org/rules/ae.svg)|    `&E m` or `∧I m`   |
| Disjunction introduction | ![alt text](https://proofs.openlogicproject.org/rules/oi.svg)|    `vI m` or `∨I m`   |
|  Disjunction elimination | ![alt text](https://proofs.openlogicproject.org/rules/oe.svg)|`vE m, i-j, k-l` or `∨I m, i-j, k-l`|
| Conditional introduction | ![alt text](https://proofs.openlogicproject.org/rules/ci.svg)| `->I i-j` or `→I i-j` |
|  Conditional elimination | ![alt text](https://proofs.openlogicproject.org/rules/ce.svg)|`->E m, n` or `→E m, n`|
|   Negation introduction  | ![alt text](https://proofs.openlogicproject.org/rules/ni.svg)|  `~I i-j` or `¬I i-j` |
|   Negation elimination   | ![alt text](https://proofs.openlogicproject.org/rules/ne.svg)| `~E m, n` or `¬E m, n`|
|Biconditional introduction| ![alt text](https://proofs.openlogicproject.org/rules/bi.svg)|`<->I i-j, k-l` or `↔I i-j, k-l`|
|Biconditional elimination | ![alt text](https://proofs.openlogicproject.org/rules/be.svg)|`<->E m, n` or `↔E m, n`|


