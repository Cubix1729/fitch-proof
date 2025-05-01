from fitch_interpreter import *
import argparse

parser = argparse.ArgumentParser(
    description="A small language to write, verify and format Fitch-style proofs in propositional logic"
)

parser.add_argument("filename", help="the path to the file containing the proofs to interpret")

parser.add_argument(
    "-l",
    "--latex",
    help="write a LaTeX document with all the proofs to the file path given",
    metavar="filename",
)

parser.add_argument(
    "-v",
    "--verify",
    action="store_true",
    help="if used, the output is printed only in case of error in the proof file given",
)

args = parser.parse_args()

try:
    interpreter = FitchInterpreter(args.filename)
    for i in interpreter.interpret_code():
        print(i)

    if args.latex is not None:
        with open(args.latex, "w") as file:
            file.write(interpreter.generate_latex_document())

except FitchError as e:
    print("Error:", str(e))

except FileNotFoundError:
    print(f'Error: file "{args.filename}" does not exist')
