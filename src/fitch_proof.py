from fitch_rules import *


class ProofError(Exception):
    pass


class ProofLine:
    def __init__(self, sentence: Expression, justification, subproof_depth):
        self.sentence = sentence
        self.justification = justification
        self.subproof_depth = subproof_depth


class Proof:
    def __init__(self, goal: Inference):
        self.goal = goal
        self.steps = []
        self.current_proof_depth = 0

    def add_premise(self, premise: Expression):
        if not len(self.steps) == 0:
            if not isinstance(self.steps[-1].justification, Premise):  # the last line wasn't a premise
                raise ProofError("all premises must be at the start of the proof")

        self.steps.append(ProofLine(sentence=premise, justification=Premise(), subproof_depth=0))

    def add_assumption(self, assumption: Expression):
        self.current_proof_depth += 1
        self.steps.append(
            ProofLine(sentence=assumption, justification=Assumption(), subproof_depth=self.current_proof_depth)
        )

    def discharge_assumption(self):
        if self.current_proof_depth != 0:
            self.current_proof_depth -= 1
        else:
            raise ProofError("no assumption is active")

    def verify_subproof(self, subproof_start: int, subproof_end: int) -> bool:
        """Verifies that the 'subproof' delimited by the two line numbers given is a valid one (returns True in this case and False otherwise)"""
        # First line must be an assumption
        try:
            if not isinstance(self.steps[subproof_start - 1].justification, Assumption):
                return False
            subproof_start_depth = self.steps[subproof_start - 1].subproof_depth
            subproof_end_depth = self.steps[subproof_end - 1].subproof_depth
        except IndexError:  # one of the two lines doesn't exist
            return False
        # The two lines must be at the same subproof level
        if subproof_start_depth != subproof_end_depth:
            return False
        # The assumption must not have been discharged between the two lines
        for line_index in range(subproof_start, subproof_end):
            proof_line = self.steps[line_index]
            if proof_line.subproof_depth < subproof_start_depth:
                return False
        # The assumption must have been discharged just after the end line
        try:
            if subproof_end_depth == self.steps[subproof_end].subproof_depth:
                if not isinstance(self.steps[subproof_end].justification, Assumption):
                    return False
        except IndexError:  # the second line is the end of the proof
            pass

        if self.current_proof_depth + 1 != subproof_end_depth:  # the subproof must be the last discharged one
            return False

        if self.current_proof_depth != 0:
            for index in range(subproof_end, len(self.steps) - 1):
                proof_line = self.steps[index]
                if proof_line.subproof_depth < subproof_start_depth - 1:
                    return False
                elif proof_line.subproof_depth == subproof_start_depth - 1:
                    if isinstance(proof_line.justification, Assumption):
                        return False

        return True

    def valid_justification_line(self, line_number: int) -> bool:
        try:
            line_cited_content = self.steps[line_number - 1]
        except IndexError:  # the line index doesn't exist
            return False
        corresponding_subproof_depth = line_cited_content.subproof_depth
        if corresponding_subproof_depth > self.current_proof_depth:
            return False

        if corresponding_subproof_depth != 0:
            for line_index in range(line_number, len(self.steps) - 1):
                proof_line = self.steps[line_index]
                if proof_line.subproof_depth < corresponding_subproof_depth:
                    return False
                elif proof_line.subproof_depth == corresponding_subproof_depth:
                    if isinstance(proof_line.justification, Assumption):
                        return False

        return True

    def add_line(self, line_content: Expression, justification: Rule):
        if isinstance(justification, RuleCitingOneLine):
            line_cited = self.steps[justification.line_number - 1].sentence
            if not self.valid_justification_line(justification.line_number):
                raise ProofError("invalid line number cited")
            new_line_correct = justification.verify(line_cited, line_content)

        elif isinstance(justification, RuleCitingTwoLines):
            line_cited_a = self.steps[justification.line_number_a - 1].sentence
            line_cited_b = self.steps[justification.line_number_b - 1].sentence
            if not (
                self.valid_justification_line(justification.line_number_a)
                and self.valid_justification_line(justification.line_number_b)
            ):
                raise ProofError("invalid line number cited")
            new_line_correct = justification.verify(line_cited_a, line_cited_b, line_content)

        elif isinstance(justification, RuleCitingOneSubproof):
            subproof_start = justification.subproof_start
            subproof_end = justification.subproof_end
            if not self.verify_subproof(subproof_start, subproof_end):
                raise ProofError("subproof cited is not valid")
            subproof_assumption = self.steps[subproof_start - 1].sentence
            subproof_conclusion = self.steps[subproof_end - 1].sentence
            new_line_correct = justification.verify(subproof_assumption, subproof_conclusion, line_content)

        elif isinstance(justification, BiConditionalIntro):
            subproof_1_start = justification.subproof_1_start
            subproof_1_end = justification.subproof_1_end
            subproof_2_start = justification.subproof_2_start
            subproof_2_end = justification.subproof_2_end

            if not (
                self.verify_subproof(subproof_1_start, subproof_1_end)
                and self.verify_subproof(subproof_2_start, subproof_2_end)
            ):
                raise ProofError("subproof cited is not valid")

            new_line_correct = justification.verify(
                self.steps[subproof_1_start - 1].sentence,
                self.steps[subproof_1_end - 1].sentence,
                self.steps[subproof_2_start - 1].sentence,
                self.steps[subproof_2_end - 1].sentence,
                line_content,
            )

        elif isinstance(justification, DisjunctionElim):
            first_line = justification.first_disjunction_line
            subproof_1_start = justification.subproof_1_start
            subproof_1_end = justification.subproof_1_end
            subproof_2_start = justification.subproof_2_start
            subproof_2_end = justification.subproof_2_end
            if not self.valid_justification_line(justification.first_disjunction_line):
                raise ProofError("invalid line number cited")
            if not (
                self.verify_subproof(subproof_1_start, subproof_1_end)
                and self.verify_subproof(subproof_2_start, subproof_2_end)
            ):
                raise ProofError("subproof cited is not valid")
            new_line_correct = justification.verify(
                self.steps[first_line - 1].sentence,
                self.steps[subproof_1_start - 1].sentence,
                self.steps[subproof_1_end - 1].sentence,
                self.steps[subproof_2_start - 1].sentence,
                self.steps[subproof_2_end - 1].sentence,
                line_content,
            )

        elif isinstance(justification, TheoremApplication):
            lines_cited = justification.lines_cited
            if not all([self.valid_justification_line(line_cited) for line_cited in lines_cited]):
                raise ProofError("invalid line number cited")

            new_line_correct = justification.verify(
                lines_cited_content=[self.steps[line_num - 1].sentence for line_num in lines_cited],
                conclusion=line_content,
            )

        if not new_line_correct:
            raise ProofError(f"incorrect justification '{justification}' for sentence '{line_content}'")

        self.steps.append(ProofLine(line_content, justification, self.current_proof_depth))

    def goal_accomplished(self) -> bool:
        if self.steps[-1].sentence == self.goal.conclusion:
            premises_used = []
            for line in self.steps:
                if isinstance(line.justification, Premise):
                    premises_used.append(line.sentence)
                else:
                    break
            if set(premises_used) == set(self.goal.premises):
                return True  # TODO: add premises
        return False

    def __str__(self) -> str:
        result = ""
        max_number_of_digits = len(str(len(self.steps)))

        for index, proof_line in enumerate(self.steps):
            justification_str = str(proof_line.justification)
            line_number_str = str(index + 1).zfill(max_number_of_digits)
            sentence_str = str(proof_line.sentence)
            corresponding_proof_depth = proof_line.subproof_depth

            line_to_add = line_number_str + " " + ("│  " * corresponding_proof_depth) + "│" + " " + sentence_str
            line_to_add = line_to_add.ljust(30)
            line_to_add += justification_str

            result += line_to_add + "\n"

            try:
                next_line = self.steps[index + 1]
                is_last_premise = isinstance(proof_line.justification, Premise) and (
                    not isinstance(next_line.justification, Premise)
                )
                add_space_between_subproofs = (
                    isinstance(next_line.justification, Assumption)
                    and next_line.subproof_depth == corresponding_proof_depth
                )
            except IndexError:  # the current line is the last line
                is_last_premise = False
                add_space_between_subproofs = False
            if isinstance(proof_line.justification, Assumption) or is_last_premise:
                # Add a 'bar' after the end of the premises or after an assumption
                result += " " * (max_number_of_digits + 1) + ("│  " * corresponding_proof_depth) + "├─────────" + "\n"

            if add_space_between_subproofs:
                result += " " * (max_number_of_digits + 1) + ("│  " * (corresponding_proof_depth - 1)) + "│" + "\n"

        return result

    def latex(self) -> str:
        result = r"$\begin{nd}" + "\n"
        for index, proof_line in enumerate(self.steps):
            line_number = index + 1
            current_proof_depth = proof_line.subproof_depth

            if isinstance(proof_line.justification, Premise):
                line_to_add = r"\hypo {" + str(line_number) + "} {" + proof_line.sentence.latex() + "} "
            elif isinstance(proof_line.justification, Assumption):
                result += r"\open" + "\n"
                line_to_add = r"\hypo {" + str(line_number) + "} {" + proof_line.sentence.latex() + "} "
            else:
                line_to_add = r"\have {" + str(line_number) + "} {" + proof_line.sentence.latex() + "} "

            line_to_add += proof_line.justification.latex()
            result += line_to_add + "\n"

            if index != len(self.steps) - 1:  # the current line is not the last one
                if self.steps[index + 1].subproof_depth < current_proof_depth:
                    result += r"\close" + "\n"
                elif self.steps[index + 1].subproof_depth == current_proof_depth and isinstance(
                    self.steps[index + 1].justification, Assumption
                ):
                    result += r"\close" + "\n"

        result += r"\end{nd}$"

        return result


"""concl = Expression("(A & B) v (A & C)")
A_and_B = Expression("A & B")
A_prop = Expression("A")
A_and_C = Expression("A & C")

test = Proof(Inference([concl], A_prop))

test.add_premise(concl)

test.add_assumption(A_and_B)

test.add_line(A_prop, ConjunctionElim(2))
test.discharge_assumption()

test.add_assumption(A_and_C)
test.add_line(A_prop, ConjunctionElim(4))

test.discharge_assumption()


test.add_line(A_prop, DisjunctionElim(1, 2, 3, 4, 5))


print(test)

print(test.latex())
print(test.goal_accomplished())
  # to remove
"""
