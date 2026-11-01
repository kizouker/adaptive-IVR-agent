"""Loop-free routing to a target state (FN-REQ-IVR-010)."""
from adaptive_ivr_agent.menu_map import MenuMap


def find_route(shown: MenuMap, target: str) -> list[str] | None:
    """Depth-first path from the current state that never repeats a state."""
    goal: list[str] | None = None

    def visit(state_id: str, path: list[str]) -> None:
        nonlocal goal
        if goal is not None:
            return
        if state_id == target:
            goal = path
            return
        for edge in shown.edges:
            if edge.source == state_id and edge.target not in path:
                visit(edge.target, [*path, edge.target])

    if shown.current:
        visit(shown.current, [shown.current])
    return goal
