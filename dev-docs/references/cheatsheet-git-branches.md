# Git Branches Cheat Sheet

This quick reference covers the most common Git commands you’ll use when working with branches in the **Betting‑Markets** project (or any repo).

---

## 1️⃣ Create & Switch Branches
| Command | Description |
|---------|-------------|
| `git checkout -b <branch>` | Create a new branch **and** switch to it. |
| `git switch -c <branch>` | Same as above, using the newer `switch` command. |
| `git checkout <branch>` | Switch to an existing branch. |
| `git switch <branch>` | Switch to an existing branch (preferred). |

---

## 2️⃣ Rename Branches
| Command | Description |
|---------|-------------|
| `git branch -m <new-name>` | Rename the **current** branch. |
| `git branch -M <new-name>` | Force‑rename (useful when the new name already exists on remote). |
| `git branch -m <old> <new>` | Rename a **different** local branch. |

---

## 3️⃣ Delete Branches
| Command | Description |
|---------|-------------|
| `git branch -d <branch>` | Delete a local branch that has been fully merged. |
| `git branch -D <branch>` | Force‑delete a local branch (use with caution). |
| `git push origin --delete <branch>` | Delete a remote branch. |

---

## 4️⃣ List Branches
| Command | Description |
|---------|-------------|
| `git branch` | List local branches, `*` marks the current one. |
| `git branch -r` | List remote‑tracking branches. |
| `git branch -a` | List both local and remote branches. |

---

## 5️⃣ Push / Pull Branches
| Command | Description |
|---------|-------------|
| `git push -u origin <branch>` | Push a new local branch to remote **and** set upstream tracking. |
| `git push` | Push the current branch (if upstream is set). |
| `git pull` | Pull changes for the current branch (fetch + merge). |
| `git fetch --all` | Retrieve all remote branches without merging. |

---

## 6️⃣ Common Workflow (what we use in this repo)
1. **Start a feature**
   ```bash
   git checkout main          # ensure you are on the latest main
   git pull                   # sync with remote
   git switch -c feature/foo  # create and switch to a new branch
   ```
2. **Do work**, commit often.
3. **Push for review**
   ```bash
   git push -u origin feature/foo
   ```
4. **Open a Pull Request** on GitHub.
5. **After merge**
   ```bash
   git checkout main
   git pull
   git branch -d feature/foo   # delete the local branch
   git push origin --delete feature/foo   # optional: delete remote branch
   ```

---

## 7️⃣ Tips & Gotchas
- Always **pull** `main` before creating a new branch to avoid merge conflicts later.
- Use `git status` frequently to see which branch you’re on and what’s staged.
- The `-u` flag on `git push` sets the upstream, so future `git push`/`git pull` commands are shorter.
- If you accidentally commit on the wrong branch, you can move the commit with `git cherry-pick` or `git reset --hard` (be careful with shared branches).

---

*Keep this file handy while you’re learning Git – it covers the essentials for branch management.*
