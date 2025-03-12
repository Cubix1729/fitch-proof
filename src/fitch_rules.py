from expressions import *
from lark import Lark, Tree
from collections import defaultdict
import re


class Rule:
    pass


class RuleCitingNoLines(Rule):
    RULE_SYMBOL: str = None
    LATEX_SYMBOL: str = None

    def __str__(self) -> str:
        return self.RULE_SYMBOL

    def latex(self) -> str:
        return self.LATEX_SYMBOL


class RuleCitingOneLine(Rule):
    RULE_SYMBOL: str = None
    LATEX_SYMBOL: str = None

    def __init__(self, line_number: int):
        self.line_number = line_number

    def __str__(self) -> str:
        return f"{self.RULE_SYMBOL} {self.line_number}"

    def latex(self) -> str:
        return f"{self.LATEX_SYMBOL}{{{self.line_number}}}"


class RuleCitingTwoLines(Rule):
    RULE_SYMBOL: str = None
    LATEX_SYMBOL: str = None

    def __init__(self, line_number_a: int, line_number_b: int):
        self.line_number_a = line_number_a
        self.line_number_b = line_number_b

    def __str__(self) -> str:
        return f"{self.RULE_SYMBOL} {self.line_number_a}, {self.line_number_b}"

    def latex(self) -> str:
        return f"{self.LATEX_SYMBOL}{{{self.line_number_a}, {self.line_number_b}}}"


class RuleCitingOneSubproof:
    RULE_SYMBOL: str = None
    LATEX_SYMBOL: str = None

    def __init__(self, subproof_start: int, subproof_end: int):
        self.subproof_start = subproof_start
        self.subproof_end = subproof_end

    def __str__(self) -> str:
        return f"{self.RULE_SYMBOL} {self.subproof_start}-{self.subproof_end}"

    def latex(self) -> str:
        return f"{self.LATEX_SYMBOL}{{{self.subproof_start}-{self.subproof_end}}}"


class Premise(RuleCitingNoLines):
    RULE_SYMBOL = "Premise"
    LATEX_SYMBOL = r"\by{Premise}{}"


class Assumption(RuleCitingNoLines):
    RULE_SYMBOL = "Assumption"
    LATEX_SYMBOL = r"\by{Assumption}{}"


class Reiteration(RuleCitingOneLine):
    RULE_SYMBOL = "R"
    LATEX_SYMBOL = r"\r"

    def verify(self, line_content: Expression, conclusion: Expression) -> bool:
        return line_content == conclusion


class ConjunctionIntro(RuleCitingTwoLines):
    RULE_SYMBOL = "∧I"
    LATEX_SYMBOL = r"\ai"

    def verify(self, line_content_a: Expression, line_content_b: Expression, conclusion: Expression) -> bool:
        if conclusion.is_conjunction():
            if line_content_a.expr == conclusion.expr.a:
                if line_content_b.expr == conclusion.expr.b:
                    return True
        return False


class ConjunctionElim(RuleCitingOneLine):
    RULE_SYMBOL = "∧E"
    LATEX_SYMBOL = r"\ae"

    def verify(self, line_content: Expression, conclusion: Expression) -> bool:
        if line_content.is_conjunction():
            if conclusion.expr == line_content.expr.a or conclusion.expr == line_content.expr.b:
                return True
        return False


class ConditionalIntro(RuleCitingOneSubproof):
    RULE_SYMBOL = "→I"
    LATEX_SYMBOL = r"\by{$\to$I}"

    def verify(self, subproof_assumption: Expression, subproof_conclusion: Expression, conclusion: Expression) -> bool:
        if conclusion.is_implication():
            if subproof_assumption.expr == conclusion.expr.a:
                if subproof_conclusion.expr == conclusion.expr.b:
                    return True
        return False


class ConditionalElim(RuleCitingTwoLines):  # equivalent to Modus Ponens
    RULE_SYMBOL = "→E"
    LATEX_SYMBOL = r"\by{$\to$E}"

    def verify(self, line_content_a: Expression, line_content_b: Expression, conclusion: Expression) -> bool:
        # We accept both line orders (A, A -> B |- B or A -> B, A |- B)
        verified_first_direction = (
            line_content_a.is_implication()
            and line_content_b.expr == line_content_a.expr.a
            and conclusion.expr == line_content_a.expr.b
        )
        verified_other_direction = (
            line_content_b.is_implication()
            and line_content_a.expr == line_content_b.expr.a
            and conclusion.expr == line_content_b.expr.b
        )
        return verified_first_direction or verified_other_direction


class DisjunctionIntro(RuleCitingOneLine):
    RULE_SYMBOL = "∨I"
    LATEX_SYMBOL = r"\oi"

    def verify(self, line_content: Expression, conclusion: Expression) -> bool:
        if conclusion.is_disjunction():
            if conclusion.expr.a == line_content.expr or conclusion.expr.b == line_content.expr:
                return True
        return False


class DisjunctionElim(Rule):
    RULE_SYMBOL = "∨E"
    LATEX_SYMBOL = r"\oe"

    def __init__(
        self,
        first_disjunction_line: int,
        subproof_1_start: int,
        subproof_1_end: int,
        subproof_2_start: int,
        subproof_2_end: int,
    ):
        self.first_disjunction_line = first_disjunction_line
        self.subproof_1_start = subproof_1_start
        self.subproof_1_end = subproof_1_end
        self.subproof_2_start = subproof_2_start
        self.subproof_2_end = subproof_2_end

    def __str__(self) -> str:
        return f"{self.RULE_SYMBOL} {self.first_disjunction_line}, {self.subproof_1_start}-{self.subproof_1_end}, {self.subproof_2_start}-{self.subproof_2_end}"

    def latex(self) -> str:
        return f"{self.LATEX_SYMBOL}{{{self.first_disjunction_line}, {self.subproof_1_start}-{self.subproof_1_end}, {self.subproof_2_start}-{self.subproof_2_end}}}"

    def verify(
        self,
        first_disjunction: Expression,
        subproof_1_assumption: Expression,
        subproof_1_conclusion: Expression,
        subproof_2_assumption: Expression,
        subproof_2_conclusion: Expression,
        conlusion: Expression,
    ):
        if first_disjunction.is_disjunction():
            if first_disjunction.expr.a == subproof_1_assumption.expr:
                if first_disjunction.expr.b == subproof_2_assumption.expr:
                    if subproof_1_conclusion == subproof_2_conclusion == conlusion:
                        return True
        return False


class NegationIntro(RuleCitingOneSubproof):
    RULE_SYMBOL = "¬I"
    LATEX_SYMBOL = r"\ni"

    def verify(self, subproof_assumption: Expression, subproof_conclusion: Expression, conclusion: Expression) -> bool:
        if conclusion.expr == Not(subproof_assumption.expr):
            if subproof_conclusion.expr == Bottom():
                return True
        return False


class NegationElim(RuleCitingTwoLines):
    RULE_SYMBOL = "¬E"
    LATEX_SYMBOL = r"\ne"

    def verify(self, line_content_a: Expression, line_content_b: Expression, conclusion: Expression) -> bool:
        if (line_content_a.expr == Not(line_content_b.expr)) or (line_content_b.expr == Not(line_content_a.expr)):
            if conclusion.expr == Bottom():
                return True
        return False


class BiConditionalIntro(Rule):
    RULE_SYMBOL = "↔I"
    LATEX_SYMBOL = r"\by{$\leftrightarrow$I}"

    def __init__(
        self,
        subproof_1_start: int,
        subproof_1_end: int,
        subproof_2_start: int,
        subproof_2_end: int,
    ):
        self.subproof_1_start = subproof_1_start
        self.subproof_1_end = subproof_1_end
        self.subproof_2_start = subproof_2_start
        self.subproof_2_end = subproof_2_end

    def __str__(self) -> str:
        return f"{self.RULE_SYMBOL} {self.subproof_1_start}-{self.subproof_1_end}, {self.subproof_2_start}-{self.subproof_2_end}"

    def latex(self) -> str:
        return f"{self.LATEX_SYMBOL}{{{self.subproof_1_start}-{self.subproof_1_end}, {self.subproof_2_start}-{self.subproof_2_end}}}"

    def verify(
        self,
        subproof_1_assumption: Expression,
        subproof_1_conclusion: Expression,
        subproof_2_assumption: Expression,
        subproof_2_conclusion: Expression,
        conlusion: Expression,
    ):
        if conlusion.is_biconditional():
            if subproof_1_assumption.expr == conlusion.expr.a and subproof_1_conclusion.expr == conlusion.expr.b:
                if subproof_2_assumption.expr == conlusion.expr.b and subproof_2_conclusion.expr == conlusion.expr.a:
                    return True
        return False


class BiConditionalElim(RuleCitingTwoLines):
    RULE_SYMBOL = "↔E"
    LATEX_SYMBOL = r"\by{$\leftrightarrow$E}"

    def verify(self, line_content_a: Expression, line_content_b: Expression, conclusion: Expression) -> bool:
        verified_first_direction = line_content_a.is_biconditional() and (
            (
                # A <-> B, A |- B
                line_content_b.expr == line_content_a.expr.a
                and conclusion.expr == line_content_a.expr.b
            )
            or (
                # A <-> B, B |- A
                line_content_b.expr == line_content_a.expr.b
                and conclusion.expr == line_content_a.expr.a
            )
        )
        verified_other_direction = line_content_b.is_biconditional() and (
            (
                # A, A <-> B |- B
                line_content_a.expr == line_content_b.expr.a
                and conclusion.expr == line_content_b.expr.b
            )
            or (
                # B, A <-> B |- A
                line_content_a.expr == line_content_b.expr.b
                and conclusion.expr == line_content_b.expr.a
            )
        )
        return verified_first_direction or verified_other_direction


class DoubleNegationElim(RuleCitingOneLine):
    RULE_SYMBOL = "¬¬E"
    LATEX_SYMBOL = r"\nne"

    def verify(self, line_content: Expression, conclusion: Expression) -> bool:
        return Not(Not(conclusion.expr)) == line_content.expr


def make_regex_from_expr(expr: Expression) -> str:
    expr_props = expr.propositions()
    expr_str = str(expr)
    expr_str = expr_str.replace("(", r"\(").replace(")", r"\)")
    for prop in expr_props:
        # For every proposition in the formula, we first replace it by its regex definition
        expr_str = expr_str.replace(prop, f"(?P<{prop}>.*)", count=1)
        # We then replace the backreferences
        expr_str = re.sub(f"([\\s\\(])({prop})", r"\1(?P=\2)", expr_str)
    return expr_str


class TheoremApplication(Rule):
    def __init__(self, theorem: Inference, lines_cited: list[int]):
        self.theorem = theorem
        self.lines_cited = lines_cited

    def __str__(self) -> str:
        if len(self.lines_cited) != 0:
            return str(self.theorem) + " with " + ", ".join(str(line_cited) for line_cited in self.lines_cited)
        else:
            return str(self.theorem)

    def latex(self) -> str:
        return (
            r"\by{$"
            + self.theorem.latex()
            + "$}{"
            + ", ".join(str(line_cited) for line_cited in self.lines_cited)
            + "}"
        )

    def verify(self, lines_cited_content: list[Expression], conclusion: Expression) -> bool:
        if len(lines_cited_content) != len(self.theorem.premises):
            return False

        proposition_matches = defaultdict(list)
        for index, premise in enumerate(self.theorem.premises):
            corresponding_line = lines_cited_content[index]
            premise_regex = make_regex_from_expr(premise)
            match_found = re.fullmatch(premise_regex, str(corresponding_line))

            if match_found is None:  # the premise isn't in the required form
                return False

            match_dict = match_found.groupdict()
            for (
                key,
                value,
            ) in match_dict.items():  # the key is a (meta) proposition and the value a match str found for it
                previous_matches = proposition_matches[key]
                for previous_match in previous_matches:
                    if Expression(value) != Expression(previous_match):  # one of the (meta) proposition doesn't match
                        return False
                proposition_matches[key].append(value)

        conclusion_regex = make_regex_from_expr(self.theorem.conclusion)
        match_found = re.fullmatch(conclusion_regex, str(conclusion))

        if match_found is None:
            return False

        # Same procedure as for the premises
        match_dict = match_found.groupdict()
        for key, value in match_dict.items():
            previous_matches = proposition_matches[key]
            for previous_match in previous_matches:
                if Expression(value) != Expression(previous_match):
                    return False
            proposition_matches[key].append(value)

        return True


"""test = TheoremApplication(
    theorem=Inference([Expression("A v B"), Expression("~A")], Expression("B")), lines_cited=[2, 3]
)

verif = test.verify(
    lines_cited_content=[Expression("(C & (D v G)) v (A -> B)"), Expression("~(C & (D v G))")],
    conclusion=Expression("A -> B"),
)

print(verif)"""  # to remove


justification_grammar = r"""
start: justification
LINE_NUM: INT
INFERENCE: /[^0-9]+/

justification: "R" LINE_NUM                                      -> reiteration
             | ("vI" | "∨I" | "|I") LINE_NUM                     -> or_intro
             | ("vE" | "∨E" | "|E") LINE_NUM "," LINE_NUM "-" LINE_NUM "," LINE_NUM "-" LINE_NUM         -> or_elim
             | ("&I" | "∧I") LINE_NUM "," LINE_NUM               -> and_intro
             | ("&E" | "∧E") LINE_NUM                            -> and_elim
             | ("->I" | "→I") LINE_NUM "-" LINE_NUM              -> if_intro
             | ("->E" | "→E") LINE_NUM "," LINE_NUM              -> if_elim
             | ("~I" | "¬I") LINE_NUM "-" LINE_NUM               -> neg_intro
             | ("~E" | "¬E") LINE_NUM "," LINE_NUM               -> neg_elim
             | ("<->I" | "↔I") LINE_NUM "-" LINE_NUM "," LINE_NUM "-" LINE_NUM  -> bicond_intro
             | ("<->E" | "↔E") LINE_NUM "," LINE_NUM             -> bicond_elim
             | ("DNE" | "~~E" | "¬¬E") LINE_NUM                  -> double_neg_elim
             | ("PR" | "Pr" | "Premise")                         -> premise
             | ("AS" | "As" | "Assumption")                      -> assumption
             | ("apply" | "Apply") INFERENCE LINE_NUM ("," LINE_NUM)+   -> apply_with_premises
             | ("apply" | "Apply") INFERENCE LINE_NUM            -> apply_with_premise
             | ("apply" | "Apply") INFERENCE                     -> apply_tautology


%import common.INT
%import common.WS
%ignore WS
"""

justification_parser = Lark(justification_grammar, lexer="dynamic_complete")


def parse_justification(tree: Tree) -> Rule:
    match tree.data:
        case "start":
            return parse_justification(tree.children[0])
        case "reiteration":
            justification_class = Reiteration
        case "or_intro":
            justification_class = DisjunctionIntro
        case "or_elim":
            justification_class = DisjunctionElim
        case "and_intro":
            justification_class = ConjunctionIntro
        case "and_elim":
            justification_class = ConjunctionElim
        case "if_intro":
            justification_class = ConditionalIntro
        case "if_elim":
            justification_class = ConditionalElim
        case "neg_intro":
            justification_class = NegationIntro
        case "neg_elim":
            justification_class = NegationElim
        case "bicond_elim":
            justification_class = BiConditionalElim
        case "bicond_intro":
            justification_class = BiConditionalIntro
        case "double_neg_elim":
            justification_class = DoubleNegationElim
        case "premise":
            justification_class = Premise
        case "assumption":
            justification_class = Assumption
        case "apply_tautology":
            return TheoremApplication(theorem=inference_from_str(tree.children[0]), lines_cited=[])
        case "apply_with_premise":
            return TheoremApplication(theorem=inference_from_str(tree.children[0]), lines_cited=[int(tree.children[1])])
        case "apply_with_premises":
            return TheoremApplication(
                theorem=inference_from_str(tree.children[0]), lines_cited=[int(child) for child in tree.children[1:]]
            )

    return justification_class(*[int(child) for child in tree.children])


def justification_from_str(justification: str) -> Rule:
    return parse_justification(tree=justification_parser.parse(justification))
