# Process
Follow `docs/process/PROCESS.MD`. It gives the order of the steps and points to one file per step.



## 🌅 Morning: The Alignment
Before starting work, conduct a sync to define the day's boundaries:
2. **Prioritization:** Define exactly one **Priority 1** and one **Priority 2**.
3. **Autonomy Check:** Determine exactly what the agent needs from the user (decisions, access, info) to work independently while the user is offline (e.g., during a run).
4. **Goal Setting:** Define what "done" looks like for the day.

## 🌙 Evening: The Save Game & Retro
Before ending the session, prevent context loss and mental residue:
1. **Technical Save:** Update `state.json` and `tickets/BACKLOG.md`. Record the exact last thought and the immediate next micro-step.
2. **Personal Retro:** Reflect on "What went well?" and "What can be better tomorrow?". Log this at the top of `RETRO_LOG.MD`.
3. **Mental Shutdown:** Confirm that the "game is saved" so the user can disconnect completely without anxiety.

 # Project rules for all agents 

Always respond to the human in Swedish; code, comments must be in English.
Always read state.json before starting. Update it when finishing.
Maximum 10 lines per response. Continue with Space.
Show Token usage; this week; this session etc in the window
