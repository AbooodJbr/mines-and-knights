import itertools


class Sentence:
    """Base type for all logical sentences."""

    def evaluate(self, model):
        """Evaluate the logical sentence against the given truth `model`."""
        raise Exception("nothing to evaluate")

    def formula(self):
        """Return a string representation suitable for display."""
        return ""

    def symbols(self):
        """Return a set of all symbols appearing in the sentence."""
        return set()

    @classmethod
    def validate(cls, sentence):
        """Ensure the value is a `Sentence`, raising on type mismatch."""
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        """Parenthesize an expression unless it is already balanced."""

        def balanced(s):
            """Return True when parentheses in `s` are balanced."""
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0

        if (
            not len(s)
            or s.isalpha()
            or (s[0] == "(" and s[-1] == ")" and balanced(s[1:-1]))
        ):
            return s
        else:
            return f"({s})"


class Symbol(Sentence):
    """Atomic proposition identified by name."""

    def __init__(self, name):
        """Store the symbol's `name`."""
        self.name = name

    def __eq__(self, other):
        """Compare by type and symbol name."""
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        """Hash based on the symbol identity."""
        return hash(("symbol", self.name))

    def __repr__(self):
        """Return debug-friendly representation."""
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}


class Not(Sentence):
    """Logical negation of a single operand."""

    def __init__(self, operand):
        """Create a negated sentence wrapping `operand`."""
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        """Check structural equality with another `Not`."""
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        """Hash using the operand's hash."""
        return hash(("not", hash(self.operand)))

    def __repr__(self):
        """Return debug string representation."""
        return f"Not({self.operand})"

    def evaluate(self, model):
        """Evaluate to the boolean negation of the operand."""
        return not self.operand.evaluate(model)

    def formula(self):
        """Return the printable negated formula."""
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        """Return symbols referenced by the operand."""
        return self.operand.symbols()


class And(Sentence):
    """Logical conjunction of one or more conjuncts."""

    def __init__(self, *conjuncts):
        """Create a conjunction from the provided `conjuncts`."""
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        """Check structural equality with another `And`."""
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        """Hash using the set of conjuncts."""
        return hash(("and", tuple(hash(conjunct) for conjunct in self.conjuncts)))

    def __repr__(self):
        """Return debug representation listing all conjuncts."""
        conjunctions = ", ".join([str(conjunct) for conjunct in self.conjuncts])
        return f"And({conjunctions})"

    def add(self, conjunct):
        """Append a new conjunct to the conjunction."""
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def evaluate(self, model):
        """Return True if all conjuncts evaluate to True in `model`."""
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        """Return a printable representation of the conjunction."""
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join(
            [Sentence.parenthesize(conjunct.formula()) for conjunct in self.conjuncts]
        )

    def symbols(self):
        """Return a union of symbols across all conjuncts."""
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])


class Or(Sentence):
    """Logical disjunction of one or more disjuncts."""

    def __init__(self, *disjuncts):
        """Create a disjunction from the provided `disjuncts`."""
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        """Check structural equality with another `Or`."""
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        """Hash using the set of disjuncts."""
        return hash(("or", tuple(hash(disjunct) for disjunct in self.disjuncts)))

    def __repr__(self):
        """Return debug representation listing all disjuncts."""
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"

    def evaluate(self, model):
        """Return True if any disjunct evaluates to True in `model`."""
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        """Return a printable representation of the disjunction."""
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨  ".join(
            [Sentence.parenthesize(disjunct.formula()) for disjunct in self.disjuncts]
        )

    def symbols(self):
        """Return a union of symbols across all disjuncts."""
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])


class Implication(Sentence):
    """Logical implication: antecedent implies consequent."""

    def __init__(self, antecedent, consequent):
        """Create an implication linking `antecedent` -> `consequent`."""
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        """Check structural equality with another `Implication`."""
        return (
            isinstance(other, Implication)
            and self.antecedent == other.antecedent
            and self.consequent == other.consequent
        )

    def __hash__(self):
        """Hash using the antecedent and consequent."""
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        """Return debug representation of the implication."""
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        """Return False only when antecedent is True and consequent False."""
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def formula(self):
        """Return a printable representation of the implication."""
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        """Return a union of symbols across antecedent and consequent."""
        return set.union(self.antecedent.symbols(), self.consequent.symbols())


class Biconditional(Sentence):
    """Logical biconditional where both sides share the same truth."""

    def __init__(self, left, right):
        """Create a biconditional connecting `left` and `right`."""
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        """Check structural equality with another `Biconditional`."""
        return (
            isinstance(other, Biconditional)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self):
        """Hash using both sides of the biconditional."""
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        """Return debug representation of the biconditional."""
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        """Return True when both sides share the same truth value."""
        return (self.left.evaluate(model) and self.right.evaluate(model)) or (
            not self.left.evaluate(model) and not self.right.evaluate(model)
        )

    def formula(self):
        """Return a printable representation of the biconditional."""
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        """Return a union of symbols across both sides."""
        return set.union(self.left.symbols(), self.right.symbols())


def model_check(knowledge, query):
    """Return True if the knowledge base logically entails the query."""

    def check_all(knowledge, query, symbols, model):
        """Recursively evaluate entailment under all symbol assignments."""

        # If model has an assignment for each symbol
        if not symbols:

            # If knowledge base is true in model, then query must also be true
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:

            # Choose one of the remaining unused symbols
            remaining = symbols.copy()
            p = remaining.pop()

            # Create a model where the symbol is true
            model_true = model.copy()
            model_true[p] = True

            # Create a model where the symbol is false
            model_false = model.copy()
            model_false[p] = False

            # Ensure entailment holds in both models
            return check_all(knowledge, query, remaining, model_true) and check_all(
                knowledge, query, remaining, model_false
            )

    # Get all symbols in both knowledge and query
    symbols = set.union(knowledge.symbols(), query.symbols())

    # Check that knowledge entails query
    return check_all(knowledge, query, symbols, dict())
