from fitch_proof import *
from expressions import *
from fitch_rules import *
from typing import Generator
from pathlib import Path
import re


PROOF_KEYWORD = "proof"
JUSTIFICATION_KEYWORD = "by"
IMPORT_KEYWORD = "#import"
COMMENT_SYMBOL = "%"
TAB_INDENTATION_VALUE = 4


class FitchError(Exception):
    def __init__(self, message: str, file: str, line_number: int):
        self.message = message
        self.file = file
        self.line_number = line_number

    def __str__(self) -> str:
        return f'File "{self.file}", line {self.line_number}: {self.message}'


def remove_comments(code: str) -> str:
    return re.sub(f"{COMMENT_SYMBOL}.*", "", code)


def remove_line_number(line: str) -> str:
    return re.sub(r"[0-9]+\.\s*?", "", line, count=0)


def indentation_value(line: str) -> int:
    value = 0
    for char in line:
        if char == " ":
            value += 1
        elif char == "\t":
            value += TAB_INDENTATION_VALUE
        else:
            break
    return value


class FitchInterpreter:
    def __init__(self, file_name):
        self.file_name = file_name
        self.current_line_number = 0
        self.imported_proofs_list = []
        self.proofs_list = []
        self.all_proved_inferences = []

    def interpret_code(self) -> Generator[str]:
        with open(self.file_name, "r") as file:
            file_content = file.read()

        file_directory = Path(self.file_name).parent
        print(file_directory)

        file_content = remove_comments(file_content)
        proof_split = re.split(f"({PROOF_KEYWORD}.*?)", file_content, flags=re.DOTALL)
        import_statements_found = False

        if proof_split[0] != "":  # file might contain import statements
            import_statements = proof_split[0].splitlines()
            for line in import_statements:
                self.current_line_number += 1
                line = line.rstrip()

                if line == "":  # ignore blank lines
                    continue

                if not line.startswith(IMPORT_KEYWORD):
                    raise FitchError("expected import statement", self.file_name, self.current_line_number)

                imported_file_name = line[len(IMPORT_KEYWORD) :].strip()
                try:
                    open(Path((file_directory / imported_file_name).resolve()), "r")

                except FileNotFoundError:
                    raise FitchError("imported file doesn't exist", self.file_name, self.current_line_number)

                file_interpreter = FitchInterpreter((file_directory / imported_file_name).resolve())
                for _ in file_interpreter.interpret_code():  # we don't display the imported proofs
                    pass

                yield f'Imported file "{imported_file_name}"\n'

                self.imported_proofs_list.extend(file_interpreter.imported_proofs_list + file_interpreter.proofs_list)
                self.all_proved_inferences.extend(
                    [proof.goal for proof in (file_interpreter.imported_proofs_list + file_interpreter.proofs_list)]
                )
                import_statements_found = True

        if import_statements_found:
            yield "\n"

        for index, proof_part in enumerate(proof_split):
            if proof_part == "":
                continue

            if proof_part == PROOF_KEYWORD:
                for str_output in self.interpret_proof(PROOF_KEYWORD + proof_split[index + 1]):
                    yield str_output
                if index < len(proof_split) - 2:  # we do not display blank lines at the end of the output
                    yield "\n\n"

    def interpret_proof(self, proof_str: str) -> Generator[str]:
        proof_lines = proof_str.splitlines()
        first_line = proof_lines[0]

        try:
            proof_goal = inference_from_str(first_line[len(PROOF_KEYWORD) :].strip())
        except:
            raise FitchError("could not parse proof goal", self.file_name, self.current_line_number)

        proof = Proof(goal=proof_goal)
        previous_indentation_level = 0  # initialise previous indentation level
        is_first_line = True

        self.current_line_number += 1  # first line interpreted

        for proof_line_str in proof_lines[1:]:  # without the first line, which describes the goal
            self.current_line_number += 1
            proof_line_str = proof_line_str.rstrip()
            proof_line_str = remove_line_number(proof_line_str)

            if proof_line_str == "":  # the line is blank
                continue
            current_indentation_level = indentation_value(proof_line_str)
            proof_line_str = proof_line_str.strip()  # we can now remove indentation

            if proof_line_str.count(JUSTIFICATION_KEYWORD) == 0:
                raise FitchError("expected justification keyword", self.file_name, self.current_line_number)

            formula_part = proof_line_str.split(JUSTIFICATION_KEYWORD)[0].strip()
            justification_part = proof_line_str.split(JUSTIFICATION_KEYWORD)[1].strip()

            try:
                line_formula = Expression(formula_part)
            except:
                raise FitchError(
                    f"invalid syntax for line main formula '{formula_part}'", self.file_name, self.current_line_number
                )

            try:
                line_justification = justification_from_str(justification_part)
            except:
                raise FitchError(
                    f"invalid syntax for justification '{justification_part}'", self.file_name, self.current_line_number
                )

            if current_indentation_level < previous_indentation_level and not is_first_line:  # assumption discharged
                try:
                    proof.discharge_assumption()
                except ProofError:
                    raise FitchError("could not discharge assumption", self.file_name, self.current_line_number)

            if isinstance(line_justification, Premise):  # premise
                try:
                    proof.add_premise(line_formula)
                except ProofError as e:
                    raise FitchError(str(e), self.file_name, self.current_line_number)

            elif isinstance(line_justification, Assumption):  # assumption
                if current_indentation_level > previous_indentation_level:
                    proof.add_assumption(line_formula)
                elif (
                    current_indentation_level == previous_indentation_level
                ):  # assumption discharged then new assumption
                    try:
                        proof.discharge_assumption()
                    except ProofError as e:
                        raise FitchError(str(e), self.file_name, self.current_line_number)
                    proof.add_assumption(line_formula)
                else:
                    raise FitchError("expected assumption", self.file_name, self.current_line_number)

            else:  # normal line added
                if isinstance(line_justification, TheoremApplication):
                    if not line_justification.theorem in self.all_proved_inferences:
                        raise FitchError(
                            f"inference '{line_justification.theorem}' was never proved",
                            self.file_name,
                            self.current_line_number,
                        )
                try:
                    proof.add_line(line_formula, line_justification)
                except ProofError as e:
                    raise FitchError(str(e), self.file_name, self.current_line_number)
                except IndexError:
                    raise FitchError("line number cited does not exist", self.file_name, self.current_line_number)

            previous_indentation_level = current_indentation_level
            is_first_line = False

        if not proof.goal_accomplished():
            raise FitchError("proof did not reach goal", self.file_name, self.current_line_number)

        self.proofs_list.append(proof)
        self.all_proved_inferences.append(proof.goal)

        yield f"Proof of {proof.goal} successful\n"
        yield str(proof)

    def generate_latex_document(self) -> str:
        latex_document = r"""\documentclass{article}
\usepackage{fitch}
\renewcommand*\contentsname{Proof list}

\begin{document}
\tableofcontents
"""
        for proof_made in self.proofs_list:
            latex_document += rf"\section{{${proof_made.goal.latex()}$}}" + "\n"
            latex_document += (
                "$" + proof_made.latex() + "$\n"
            )

        latex_document += r"\end{document}"
        return latex_document
