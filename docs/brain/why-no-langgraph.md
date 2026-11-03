# Why no LangGraph #decision

LangGraph = graph framework for orchestrating LLM agents
(nodes, edges, state, retries). We use it nowhere:

- Holdmate agent: scripted FSM + intent ladder (exact → heuristic →
  Meta model → abstain). Deterministic, testable, no graph needed.
- My workers: native subagents with tickets + branches, coordinated
  by me. No LLM-to-LLM handoff graph.
- When it would fit: multi-step LLM reasoning (planner → caller →
  checker) with retries. Parked — scripted beats clever before freeze.
