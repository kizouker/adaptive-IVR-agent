Feature: Prompt safety self-scan
  Agent instruction files must not hold directives that weaken
  prompt safety (OWASP LLM01 baseline).

  Scenario: Instruction files hold no weakening directives
    When the prompt self-scan runs over the agent instructions
    Then it reports OK with no findings
