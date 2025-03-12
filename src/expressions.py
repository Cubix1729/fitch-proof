from lark import Lark, Tree


class Proposition:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if isinstance(other, Proposition):
            return self.name == other.name
        return False

    def latex(self) -> str:
        return self.name

    def propositions(self) -> set[str]:
        return {self.name}


class Top:
    def __str__(self) -> str:
        return "⊤"

    def __eq__(self, other):
        return isinstance(other, Top)

    def latex(self) -> str:
        return r"\top"

    def propositions(self) -> set[str]:
        return set()


class Bottom:
    def __str__(self) -> str:
        return "⊥"

    def __eq__(self, other):
        return isinstance(other, Bottom)

    def latex(self) -> str:
        return r"\bot"

    def propositions(self) -> set[str]:
        return set()


class Not:
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return f"¬{self.a}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Not):
            return self.a == other.a
        return False

    def latex(self) -> str:
        return r"\neg " + self.a.latex()

    def propositions(self) -> set[str]:
        return self.a.propositions()


class And:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self) -> str:
        return f"({self.a} ∧ {self.b})"

    def __eq__(self, other) -> bool:
        if isinstance(other, And):
            return self.a == other.a and self.b == other.b
        return False

    def latex(self) -> str:
        return "(" + self.a.latex() + r" \land " + self.b.latex() + ")"

    def propositions(self) -> set[str]:
        return self.a.propositions().union(self.b.propositions())


class Or:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self) -> str:
        return f"({self.a} ∨ {self.b})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Or):
            return self.a == other.a and self.b == other.b
        return False

    def latex(self) -> str:
        return "(" + self.a.latex() + r" \lor " + self.b.latex() + ")"

    def propositions(self) -> set[str]:
        return self.a.propositions().union(self.b.propositions())


class Conditional:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self) -> str:
        return f"({self.a} → {self.b})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Conditional):
            return self.a == other.a and self.b == other.b
        return False

    def latex(self) -> str:
        return "(" + self.a.latex() + r" \to " + self.b.latex() + ")"

    def propositions(self) -> set[str]:
        return self.a.propositions().union(self.b.propositions())


class BiConditional:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self) -> str:
        return f"({self.a} ↔ {self.b})"

    def __eq__(self, other) -> bool:
        if isinstance(other, BiConditional):
            return self.a == other.a and self.b == other.b
        return False

    def latex(self) -> str:
        return "(" + self.a.latex() + r" \leftrightarrow " + self.b.latex() + ")"

    def propositions(self) -> set[str]:
        return self.a.propositions().union(self.b.propositions())


def interpret_expr_tree(tree: Tree) -> Proposition | Not | Or | And | Conditional | BiConditional:
    match tree.data:
        case "start":
            return interpret_expr_tree(tree.children[0])
        case "proposition":
            return Proposition(str(tree.children[0]))
        case "top":
            return Top()
        case "bottom":
            return Bottom()
        case "not":
            return Not(interpret_expr_tree(tree.children[0]))
        case "or":
            return Or(interpret_expr_tree(tree.children[0]), interpret_expr_tree(tree.children[1]))
        case "and":
            return And(interpret_expr_tree(tree.children[0]), interpret_expr_tree(tree.children[1]))
        case "implies":
            return Conditional(interpret_expr_tree(tree.children[0]), interpret_expr_tree(tree.children[1]))
        case "iff":
            return BiConditional(interpret_expr_tree(tree.children[0]), interpret_expr_tree(tree.children[1]))
        case "formula":
            return interpret_expr_tree(tree.children[0])


class Expression:
    grammar = r"""
start: formula
PROP: UCASE_LETTER
TOP: "⊤" | "true" | "True" | "TRUE"
BOTTOM: "⊥" | "false" | "False" | "FALSE"

formula: PROP                              -> proposition
       | TOP                               -> top
       | BOTTOM                            -> bottom
       | formula ("→" | "->") formula      -> implies
       | formula ("↔" | "<->") formula     -> iff
       | formula ("∨" | "v" | "|") formula -> or
       | formula ("&" | "∧") formula       -> and
       | ("~" | "¬") formula         -> not
       | "(" formula ")"

%import common.UCASE_LETTER
%import common.WS
%ignore WS
"""
    parser = Lark(grammar)

    def __init__(self, expr: str):
        self.expr = interpret_expr_tree(self.parser.parse(expr))

    def __str__(self) -> str:
        string_representation = str(self.expr)
        if string_representation[0] == "(" and string_representation[-1] == ")":
            return string_representation[1:-1]  # without the outer parenthesis
        else:
            return string_representation

    def __eq__(self, other) -> bool:
        return self.expr == other.expr

    def __hash__(self) -> int:
        return hash(str(self))

    def latex(self) -> str:
        latex_expr = self.expr.latex()
        if latex_expr[0] == "(" and latex_expr[-1] == ")":
            return latex_expr[1:-1]  # without the outer parenthesis
        else:
            return latex_expr

    def is_negation(self):
        return isinstance(self.expr, Not)

    def is_conjunction(self):
        return isinstance(self.expr, And)

    def is_disjunction(self):
        return isinstance(self.expr, Or)

    def is_implication(self):
        return isinstance(self.expr, Conditional)

    def is_biconditional(self):
        return isinstance(self.expr, BiConditional)

    def propositions(self) -> set[str]:
        return self.expr.propositions()


class Inference:
    def __init__(self, premises: list[Expression], conclusion: Expression):
        self.premises = premises
        self.conclusion = conclusion

    def __str__(self) -> str:
        return f"{", ".join([str(premise) for premise in self.premises])} ⊢ {self.conclusion}"

    def __eq__(self, other) -> bool:
        return self.premises == other.premises and self.conclusion == other.conclusion

    def latex(self) -> str:
        return ", ".join([premise.latex() for premise in self.premises]) + r" \vdash " + self.conclusion.latex()


inference_grammar = r"""
start: inference

FORMULA: /[^","]+/

premise: FORMULA
conclusion: FORMULA
inference: ("|-" | "⊢") conclusion
         | premise ("|-" | "⊢") conclusion
         | (premise ("," premise)+) ("|-" | "⊢") conclusion
%import common.WS
%ignore WS
"""

inference_parser = Lark(inference_grammar, lexer="dynamic_complete")


def inference_from_str(inference_str: str) -> Inference:
    parsed_tree = inference_parser.parse(inference_str)
    working_tree = parsed_tree
    premises_found = []
    if working_tree.data == "start":
        working_tree = working_tree.children[0]
        if working_tree.data == "inference":
            working_tree = working_tree
            for leaf in working_tree.children:
                if leaf.data == "premise":
                    premises_found.append(Expression(str(leaf.children[0])))
                elif leaf.data == "conclusion":
                    conclusion_found = Expression(str(leaf.children[0]))

    return Inference(premises=premises_found, conclusion=conclusion_found)
