---
name: git-whereami
description: Show current branch, ahead/behind origin, dirty files and last commit, compactly in chat.
---

# Where Am I

Use when Rickard asks where he is ("var är jag", "vilken branch",
"what branch are you on").

Run exactly this and paste the compact result:

```sh
git status -sb | head -12 && git log --oneline -3
```

Then add one line in plain words: branch name, how many commits ahead of
or behind origin, and whether uncommitted work exists. Never commit, push,
stash, or switch branches from this view without his explicit word; this
skill only reads.
