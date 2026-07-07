# From Optical Engineer to Software Engineer: The First Time I Understood Git Through Gitea

![Git mental model: Working Tree, Staging Area, Local Repository, and Remote Repository.](medium-assets/git-mental-model-01.png)

I used to be an optical engineer.

My software engineering journey started later, from learning Python on my own to building small tools, automation scripts, and eventually real development workflows.

At first, software development felt like a different operating system for my brain. I had to learn not only a programming language, but also Ubuntu, compilers, repositories, remotes, branches, merge conflicts, and the daily habits of engineering teams.

Git was one of the hardest parts.

I knew some commands:

```bash
git add
git commit
git push
git pull
```

But I did not understand what each command really changed.

I was mostly memorizing steps. When something worked, I moved on. When something failed, especially around merge conflicts or remote repositories, Git felt like a fragile black box.

That changed during a real project where I created a Gitea repository and pushed code into it. For the first time, I was not only typing commands. I was seeing the structure behind them.

This article is not a Git command cheat sheet. It is the story of how I moved from memorizing commands to understanding Git as a system for organizing software work.

## I Used To Think Git Was Just Saving Code

When I first learned Git, I thought its purpose was to save code.

That is not completely wrong, but it misses the real value.

If the only goal is to save files, I can create a zip file, copy a folder, or upload everything to cloud storage. But those approaches do not answer the questions that matter in software development:

- What changed?
- Why did it change?
- Which change introduced a bug?
- Which changes are ready to be committed?
- Which changes are only temporary experiments?
- How can teammates receive the same history?
- If a machine breaks, can the team restart work from a clean state?

Git preserves history that can be traced, shared, reviewed, restored, and continued by a team.

More precisely:

> Git preserves the team's ability to restart work.

That idea changed how I see Git. It turned Git from a storage tool into an engineering system.

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

Generated output is produced by tools or local environments:

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

`.gitignore` is not just a place to hide unimportant files. It defines the boundary of the project. It separates the files the team intentionally maintains from files produced by one machine, one run, or one tool.

## Key Idea 2: The Working Tree Is Not Git History

The next confusing part was the difference between the files in my folder and the history stored in Git.

The useful way to separate them is:

- Working Tree
- Staging Area
- Local Repository
- Remote Repository

The Working Tree is my current working scene.

It may contain finished changes, experiments, accidental edits, temporary files, or half-complete ideas. Just because something exists in the Working Tree does not mean it belongs in history.

This helped me understand `git status`.

`git status` is Git answering a practical question:

> What is currently in my working scene, and what has not yet been organized into the next piece of history?

## Key Idea 3: `git add` Does Not Mean "Add To Git"

I used to think `git add` meant "add this file to Git."

That wording is misleading.

A better explanation is:

> `git add` takes the version I choose from the Working Tree and places it into the Staging Area.

The Staging Area is the draft of the next commit.

I may have changed ten files in the Working Tree, but that does not mean all ten files should belong to the same commit. With `git add`, I am telling Git:

> This version of this change is what I want to include in the next commit.

Git does not only care that files changed. Git cares how I organize those changes into meaningful commits.

This also explains why I can run `git add`, then continue editing the same file. The Staging Area contains the version I staged at that moment. The Working Tree can continue changing afterward.

## Key Idea 4: `git commit` Is Not Uploading

I also used to confuse `git commit` with uploading.

Now I understand it differently:

> `git commit` writes the staged version into my local Git history.

A commit takes the content prepared in the Staging Area and turns it into a historical point in the Local Repository.

That historical point contains more than a file snapshot. It also includes:

- the content of the change
- the author
- the timestamp
- the commit message
- the relationship to previous history

This is why commit messages matter.

A commit message explains to my future self and my teammates:

> Why does this piece of history exist?

A good commit is not simply big or small. A good commit expresses a clear intention.

## Key Idea 5: `git push` Shares History With The Team

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

## A Merge Conflict Is Not A Disaster

I also went through a merge conflict during this learning process.

Before this, seeing a conflict made me feel like I had broken Git.

Now I see it differently:

> A merge conflict is Git honestly stopping because two histories changed the same place, and Git cannot decide the correct meaning for me.

Git is good at merging changes that do not conflict. But Git should not silently decide business logic, design intent, or team decisions.

When Git stops and asks a human to decide, that is not failure. That is version control respecting engineering meaning.

Resolving a conflict is not just deleting conflict markers. The real work is understanding both sides, deciding the final correct result, then committing that decision back into history.

## The Git Workflow I Finally Understand

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

## How ChatGPT And Codex Helped

This learning process was not just me reading documentation, and it was not AI simply typing commands for me.

I used ChatGPT more like a learning coach.

It helped me break down Git concepts, ask better questions, and turn vague confusion into a clearer structure. Instead of only saying "type this command," it helped me understand why each step existed.

I used Codex more like a technical lead.

Codex helped review the technical correctness of the article and reinforce the engineering details: `.gitignore`, the Source versus Generated boundary, the role of commits, the difference between local and remote repositories, and why merge conflicts are not just operational problems but moments where history needs human judgment.

This changed how I think about AI collaboration.

The most valuable use of AI is not replacing the engineer. It is helping the engineer build reusable technical judgment.

If I only copy commands from AI, I will panic again when the next unfamiliar Git situation appears. If AI helps me understand Working Tree, Staging Area, Local Repository, and Remote Repository, I can reason about new Git situations myself.

## From Memorizing Commands To Understanding Design

This experience moved me from memorizing Git commands to understanding Git's design.

I no longer see Git as a dangerous list of commands. I see it as a system for managing history, collaboration, and recoverability.

My current understanding can be summarized like this:

- The Working Tree is where I am currently working.
- The Staging Area is the draft of the next commit.
- The Local Repository is the history saved on my machine.
- The Remote Repository is the shared history for the team.
- `git add` selects the version I want to commit.
- `git commit` writes that version into local history.
- `git push` shares that history with the team.
- Git stores Source, not Generated output.
- Git's purpose is not just saving files. It preserves the team's ability to restart work.

Creating a Gitea project, pushing code, encountering conflicts, and understanding remote repositories helped me feel, for the first time, that I was not merely using Git.

I was understanding how Git supports software engineering work.

