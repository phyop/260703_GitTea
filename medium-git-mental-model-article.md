# From Optical Engineer to Software Engineer: The First Time I Understood Git Through Gitea

## Title Options

1. From Optical Engineer to Software Engineer: The First Time I Understood Git Through Gitea
2. Git Finally Made Sense When I Stopped Treating It Like a Save Button
3. The Git Mental Model That Helped Me Move From Commands to Engineering Judgment
4. Working Tree, Staging Area, Local, Remote: How I Finally Understood Git
5. What Gitea Taught Me About Git, History, and Restartable Software Work
6. Why Git Is Not Just Saving Code: A Practical Mental Model for New Engineers

## SEO

**Meta description:** A practical Git mental model for new software engineers, explained through a real Gitea learning journey from optical engineering to software development.

**SEO keywords:** Git mental model, Gitea tutorial, learn Git, Working Tree, Staging Area, Local Repository, Remote Repository, git add, git commit, git push, merge conflict, .gitignore, source versus generated output, software engineering workflow

## Tags

Git, Gitea, Software Engineering, Version Control, Developer Journey, Learning In Public, AI Assisted Learning, Career Change

![Git mental model: Working Tree, Staging Area, Local Repository, and Remote Repository.](medium-assets/git-mental-model-01.png)

I used to be an optical engineer.

That background trained me to care about systems, precision, root causes, and measurement. But when I started moving into software engineering, I realized that software had its own operating system of habits. I was not only learning Python. I was learning Ubuntu, compilers, package managers, repositories, branches, remotes, merge conflicts, and the daily rhythm of engineering work.

Git was one of the hardest parts.

At first, I knew the words:

```bash
git add
git commit
git push
git pull
```

But knowing the words was not the same as understanding the system. I could follow instructions, but I did not understand what each command really changed. When something worked, I moved on. When something failed, especially around remote repositories or merge conflicts, Git felt like a fragile black box.

That changed during a real project where I created a repository in Gitea and pushed code into it. For the first time, I was not only typing commands. I was seeing the structure behind them.

This article is not a Git command cheat sheet. It is the story of how I moved from memorizing commands to understanding Git as a system for organizing software work.

## Background: I Thought Git Was Just Saving Code

When I first learned Git, I thought its purpose was to save code.

That is not completely wrong, but it is too small.

If the only goal is to save files, I can create a zip file, copy a folder, or upload everything to cloud storage. Those approaches may preserve bytes, but they do not answer the engineering questions that matter during real development:

- What changed?
- Why did it change?
- Which change introduced a bug?
- Which changes are ready to be committed?
- Which changes are only temporary experiments?
- How can teammates receive the same history?
- If a machine breaks, can the team restart work from a clean state?

Git preserves history that can be traced, shared, reviewed, restored, and continued by a team. More precisely:

> Git preserves the team's ability to restart work.

That idea changed how I saw Git. It turned Git from a storage tool into an engineering system. The point was not only "I saved my latest files." The point was "the team can understand how this project reached its current state and can continue from a known point."

That is a much deeper promise.

## Process: Gitea Made The Remote Real

Before using Gitea, the word "remote" felt abstract. I knew commands referred to a remote repository, but I did not have a strong picture of what that meant.

Creating a Gitea repository gave the concept a physical shape in my mind. There was my working folder on my machine. There was a `.git` directory storing local history. Then there was a shared repository in Gitea that did not automatically change just because I edited a file locally.

That distinction mattered.

When I changed a file, the change existed in my Working Tree. When I staged it, I selected a version for the next commit. When I committed it, I wrote that selected version into my Local Repository. When I pushed it, I shared that local history with Gitea.

Suddenly the commands stopped feeling like magic words. They became movements between places.

## Key Idea 1: Git Stores Source, Not Generated Output

![Git stores Source, not Generated output: source code, config, docs, tests, and scripts belong in version control; build output and cache usually do not.](medium-assets/git-mental-model-02.png)

The first important idea I learned was this:

> Git stores Source, not Generated output.

Source is what humans intentionally maintain:

- source code
- configuration files
- documentation
- tests
- build scripts
- required assets
- anything needed to recreate the working system

Generated output is produced by tools, commands, builds, caches, or local environments:

- compiled binaries
- cache files
- logs
- temporary files
- build output
- Python `__pycache__`
- Node.js `node_modules`

Before I understood this, my question was simple: "Should I upload this file too?"

Now the better question is:

> If another engineer clones this repository, will they have enough Source to recreate the same working capability?

That is how I began to understand `.gitignore`.

`.gitignore` is not only a place to hide unimportant files. It defines the boundary of the project. It separates the files the team intentionally maintains from files produced by one machine, one run, or one tool.

This was a major mental shift. Git is not a backup bucket for every file that appears in a folder. Git is a record of the meaningful Source needed to rebuild, review, and continue the project.

## Solution: The Four Places In Git

The model that finally made Git understandable was separating it into four places:

- Working Tree
- Staging Area
- Local Repository
- Remote Repository

The Working Tree is my current working scene. It may contain finished changes, experiments, accidental edits, temporary files, or half-complete ideas. Just because something exists in the Working Tree does not mean it belongs in history.

This helped me understand `git status`.

`git status` is Git answering a practical question:

> What is currently in my working scene, and what has not yet been organized into the next piece of history?

The Staging Area is the draft of the next commit. It is not the same thing as the Working Tree. I may have changed ten files, but maybe only two belong in the next commit. With staging, I can select the exact version that belongs together.

The Local Repository is the history saved on my machine. A commit lives there before it is shared. This means `git commit` is not uploading anything. It is writing a point in local history.

The Remote Repository is the shared history in Gitea, GitHub, GitLab, or another Git host. It is what teammates can clone, review, deploy from, or continue working from.

Once these four places were clear, the commands became much less mysterious:

```text
git add    -> select the version for the next commit
git commit -> write that selected version into local history
git push   -> share local history with the remote repository
```

## `git add` Does Not Mean "Add To Git"

I used to think `git add` meant "add this file to Git."

That wording is misleading. A better explanation is:

> `git add` takes the version I choose from the Working Tree and places it into the Staging Area.

This also explains why I can run `git add`, then continue editing the same file. The Staging Area contains the version I staged at that moment. The Working Tree can keep changing afterward.

That detail helped me understand why Git sometimes says there are both staged and unstaged changes in the same file. Git is tracking two different versions: the version selected for the next commit and the version currently sitting in my working folder.

The Staging Area gave me a new question to ask:

> Is this version of this change what I want to include in the next commit?

Git does not only care that files changed. Git cares how I organize those changes into meaningful commits.

## `git commit` Is Not Uploading

I also used to confuse `git commit` with uploading.

Now I understand it differently:

> `git commit` writes the staged version into my local Git history.

A commit takes the content prepared in the Staging Area and turns it into a historical point in the Local Repository. That historical point contains more than a file snapshot. It also includes:

- the content of the change
- the author
- the timestamp
- the commit message
- the relationship to previous history

This is why commit messages matter. A commit message explains to my future self and my teammates:

> Why does this piece of history exist?

A good commit is not simply big or small. A good commit expresses a clear intention. It groups related changes together so the project history can be understood later.

## `git push` Shares History With The Team

![Git workflow: from editing and selecting changes to committing and pushing shared history.](medium-assets/git-mental-model-03.png)

After I understood `git commit`, `git push` became clear.

> `git push` sends my local Git history to the Remote Repository.

In my project, the Remote Repository was Gitea.

Gitea is not the `.git` folder on my machine. It is the shared repository that the team can access. After I create a commit locally, that history still exists only in my Local Repository. Only after `git push` does that history appear in Gitea, where teammates can see it, review it, clone it, deploy from it, or continue working from it.

This gave me a clean separation:

- `git add`: prepare the next commit
- `git commit`: write the prepared change into local history
- `git push`: share local history with the remote repository

These are three different stages in Git's design.

## Pitfall: A Merge Conflict Is Not A Disaster

I also went through a merge conflict during this learning process.

Before this, seeing a conflict made me feel like I had broken Git. Now I see it differently:

> A merge conflict is Git honestly stopping because two histories changed the same place, and Git cannot decide the correct meaning for me.

Git is good at merging changes that do not conflict. But Git should not silently decide business logic, design intent, or team decisions.

When Git stops and asks a human to decide, that is not failure. That is version control respecting engineering meaning.

Resolving a conflict is not just deleting conflict markers. The real work is understanding both sides, deciding the final correct result, then committing that decision back into history.

That changed how I felt during conflict resolution. Instead of "Git is broken," the better thought is "Git found a place where human judgment is required."

## The Workflow I Finally Understand

After this project, the workflow in my head became:

```bash
# 1. Check the current working state
git status

# 2. Inspect what actually changed
git diff

# 3. Select the version I want in the next commit
git add <file>

# 4. Confirm what the next commit will contain
git diff --staged

# 5. Write the staged version into local history
git commit -m "Describe the change"

# 6. Share the local history with the remote repository
git push
```

I had seen these commands before. The difference is that now I understand what each step is doing.

`git status` shows the current relationship between the Working Tree, Staging Area, and local history. `git diff` lets me inspect what changed before I choose it. `git add` selects the version I want in the next commit. `git diff --staged` checks that draft commit before I record it. `git commit` writes the staged version into local history. `git push` shares that history with the remote repository.

The command sequence matters, but the mental model matters more.

## How ChatGPT And Codex Helped

This learning process was not just me reading documentation, and it was not AI simply typing commands for me.

I used ChatGPT more like a learning coach. It helped me break down Git concepts, ask better questions, and turn vague confusion into a clearer structure. Instead of only saying "type this command," it helped me understand why each step existed.

I used Codex more like a technical lead. Codex helped review the technical correctness of the article and reinforce the engineering details: `.gitignore`, the Source versus Generated boundary, the role of commits, the difference between local and remote repositories, and why merge conflicts are not just operational problems but moments where history needs human judgment.

This changed how I think about AI collaboration.

The most valuable use of AI is not replacing the engineer. It is helping the engineer build reusable technical judgment.

If I only copy commands from AI, I will panic again when the next unfamiliar Git situation appears. If AI helps me understand Working Tree, Staging Area, Local Repository, and Remote Repository, I can reason about new Git situations myself.

## Lessons Learned

This experience moved me from memorizing Git commands to understanding Git's design.

My current understanding can be summarized like this:

- The Working Tree is where I am currently working.
- The Staging Area is the draft of the next commit.
- The Local Repository is the history saved on my machine.
- The Remote Repository is the shared history for the team.
- `git add` selects the version I want to commit.
- `git commit` writes that version into local history.
- `git push` shares that history with the team.
- Git stores Source, not Generated output.
- `.gitignore` documents the boundary between maintained Source and local generated output.
- A merge conflict is Git asking for human judgment, not proof that Git failed.
- Git's purpose is not just saving files. It preserves the team's ability to restart work.

## Conclusion: From Commands To Engineering Judgment

Creating a Gitea project, pushing code, encountering conflicts, and understanding remote repositories helped me feel, for the first time, that I was not merely using Git.

I was understanding how Git supports software engineering work.

That matters because software engineering is not only writing code. It is creating systems that other people, and future versions of ourselves, can understand and continue.

Git supports that by making work traceable, reviewable, recoverable, and shareable.

I no longer see Git as a dangerous list of commands. I see it as a design for managing history.

The commands did not change. My mental model did.

