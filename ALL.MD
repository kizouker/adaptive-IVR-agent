# General rules for all agents
# Process
Follow `@.agents/process/PROCESS.MD`. It gives the order of the steps and points to one file per step.
Read @BLOCKED
 # Project rules for all agents 

Always respond to the human in Swedish; code, comments must be in English.

Always read state.json before starting. Update it when finishing.

Maximum 10 lines per response. Continue with Space.
End every reply with "Vad är nästa steg?" plus 1-3 items from your backlog.
When starting a new task, first restate all open threads so none get lost.

No ticket no work. A ticket is always a GitHub issue (Why, What, Done when), never a local file. Exception: basic file system maintenance (moving, renaming or tidying files and folders, and fixing the references to them) needs no ticket.
Every ticket carries test steps (Så testar du) for Rickard: added at creation, kept current on every change.