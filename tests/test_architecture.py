"""Architecture rules (T-051): module boundaries, checked on every run."""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "adaptive_ivr_agent"
PACKAGE = "adaptive_ivr_agent"


def module_graph():
    """Sibling imports per module: {module: {imported siblings}}."""
    graph = {}
    for path in sorted(SRC.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        siblings = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                head, _, rest = node.module.partition(".")
                if head == PACKAGE and rest:
                    siblings.add(rest.split(".")[0])
        graph[path.stem] = siblings
    return graph


def test_no_circular_imports():
    graph = module_graph()
    visiting, done = set(), set()

    def visit(name, stack):
        assert name not in visiting, f"import cycle: {' -> '.join([*stack, name])}"
        if name in done:
            return
        visiting.add(name)
        for child in graph.get(name, set()):
            visit(child, [*stack, name])
        visiting.discard(name)
        done.add(name)

    for module in graph:
        visit(module, [])


def test_no_module_imports_tests():
    for path in SRC.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "import tests" not in text and "from tests" not in text, path.name


def test_sibling_imports_resolve_to_real_modules():
    graph = module_graph()
    for module, siblings in graph.items():
        for sibling in siblings:
            assert sibling in graph, f"{module} imports unknown {sibling}"
