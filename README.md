# From Optical Engineer to Software Engineer

This repository contains the source material, diagrams, and Medium article draft for a real learning story:

**The First Time I Understood Git Through Gitea**

The article is not a command cheat sheet. It documents how I moved from memorizing Git commands to understanding the structure behind everyday software collaboration.

![Git mental model overview](medium-assets/git-mental-model-01.png)

## Core Idea

Git became easier to reason about after I separated it into four places:

- Working Tree: where current edits, experiments, and unfinished changes live
- Staging Area: the draft of the next commit
- Local Repository: the history saved on my machine
- Remote Repository: the shared history on Gitea, GitHub, or GitLab

That model changed the meaning of the commands:

```text
git add    -> select the version for the next commit
git commit -> write that selected version into local history
git push   -> share local history with the remote repository
```

## Source, Not Generated Output

![Source versus generated output](medium-assets/git-mental-model-02.png)

One of the most important lessons was that Git should preserve Source, not generated output.

Source includes code, configuration, documentation, tests, scripts, and required assets. Generated output usually includes build artifacts, caches, logs, temporary files, and machine-specific results.

The practical question became:

> If another engineer clones this repository, do they have enough Source to recreate the working capability?

## Workflow

![Git workflow](medium-assets/git-mental-model-03.png)

The workflow I finally understood is:

```bash
git status
git diff
git add <file>
git diff --staged
git commit -m "Describe the change"
git push
```

The value is not the command sequence alone. The value is knowing which part of the Git system each command changes.

## Medium Article

The article version is kept in:

- [medium-git-mental-model-article.md](medium-git-mental-model-article.md)

Published Medium article:

- [From Optical Engineer to Software Engineer: The First Time I Understood Git Through Gitea](https://medium.com/@seek1andfind2/from-optical-engineer-to-software-engineer-the-first-time-i-truly-understood-git-d80175b1b839)

## AI Collaboration

This project also records how I used AI as part of the learning process:

- ChatGPT helped explain the Git concepts and shape the learning path.
- Codex helped review the technical structure, repository hygiene, and project isolation.

The goal was not to let AI replace engineering judgment. The goal was to use AI to build better judgment.

## Project Isolation

This repository belongs only to the `260703_GitTea` project. Content from other projects should not be mixed into this folder or this Git history.
