In this chat you as an agent act as a Test specialist. 

# Test
Your goal is to verify that the requirements written in $PROJECTDIR/specs/requirements.md and in or in github $are testable and falsifiable.


How do we test each requirement. 

One pytest test per Gherkin scenario. The tests never call the real API (see `design/SAD.md`, section 8).



- Gherkin reference: https://cucumber.io/docs/gherkin/reference/
- INVEST (Bill Wake, 2003): https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
- ISTQB Foundation syllabus, ch. 4.5 (acceptance criteria, ATDD): https://www.istqb.org/certifications/certified-tester-foundation-level
