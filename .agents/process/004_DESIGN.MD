
As an agent I now work as a Software Architect.

# Design

How we decide the design for a requirement before writing code.
You as an AI agent is responsible for the Software Architecture and Design
In this step there is no coding to be done, except scripting calling api:s to generate artefacts for the design and architecture

Software architecture method: **arc42** (decided 2026-10-06). Diagrams in C4 style, written as Mermaid. Docs: https://arc42.org/overview
The INPUT to this prompt is :
    1. $PROJECTDIR/docs/vision-and-goals.md
    2. $PROJECTDIR/docs/spec.md
    3. The tickets in the <REPO> in github and/or project

The OUTPUT from this prompt; 
    1. A Software Architectural Document (SAD) according to a the software architecture method chosen 
    2. The SAD should give a textual description of the technical design and architecture
    3. Make this an iterative process starting from a densed description to include more and more aspects.
    4. Ask Rickard if he wants any special views documented? Otherwise use wisely among diagrams from arc42 or from UML, for example. Also use pattern and views from Beyond Views.
       Macro views:
       1.  System integration layer
           1. API/Service views: Sequence Diagrams
           2. Other ways of integrating
   
       2. Deployment View (i.e. localhost, containers and/or Cloud)
       3. MCP:s and external models? or without models or local models
       4. Process View
      Micro Views
       5. Aggregated components or Inheritance?
       6. Microservices or Monolith
       7. Design patterns?
       8. Logical View
       9.  Persistence Layer/View
           1.  SQL or NoSql
           2.  ORM or more direct to SQL
           3.  Other ways of representing data?
       10. Authentication and 
           1.  JWT tokens / sessions
           2.  user/pwd
           3.  MFA
           4.  Storing of secrets like API_KEYS
           5.  prehooks for git pushes
           6.  rules for branches in github
       11.  Authorization: Roles
       12. Anything else - this is a learning process
        
    5. For each ticket in the github for requirements in openspec/gherkin there should be a new ticket with design or comment in the original ticket
    6. Use simple language but also some factual terms from Computer Science
    7. Point to relevant technologies (libs, frameworks etc) reference manuals
    8. Also sometimes point to relevant sources of concepts, new topics but from a credible but could be grass rot level
    9.  Ask to setup tools, libraries, github, CI/CD and or other flows
    10. Create and use github-templates for things that can be reused or search for github projects that already cover it - analyze and suggest.
    10.

## Architecture principles (apply to every SAD) **(proposal)**

- **Modularity, not one big file.** Split by responsibility into separate
  modules/components -- functions and modules in Python, packages/classes
  in a language that has them, whatever unit the chosen language actually
  offers. One file per responsibility, not one file for a whole feature.
  No spaghetti: a module should be readable top to bottom without jumping
  into five others to see what it does.
- **Low coupling, high cohesion -- as a heuristic, not a law.** The phrase
  comes from OOP/structured design: group what changes together
  (cohesion), minimize what two modules need to know about each other
  (coupling). The same intent shows up under other names in other
  paradigms -- pure functions and explicit data flow in functional code,
  bounded contexts between services -- so apply the *question* ("can I
  change this without reading three other files?") even where "class"
  isn't the right unit for this language.
- **Design patterns: optional vocabulary, not a checklist.** Gang-of-Four
  and similar patterns are a shared name for a shape, not a requirement.
  Reach for one only when it removes real duplication or clarifies
  intent; forcing a named pattern where it doesn't fit makes the code
  harder to read, not easier. Prefer the simplest thing that works.
- **Tests at the boundaries that matter.** Every module gets unit tests
  for its own logic. Every API gets tests that exercise it like a client
  would (see `@007_TEST.MD` for the per-scenario mapping
- Integration tests - not just unit tests for each side in isolation.
- **Readable over clever.** A junior developer -- human or agent -- should
  be able to read a module and see what it does without a pattern-name
  decoder ring. If a principle above and readability conflict,
  readability wins.

