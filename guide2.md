 # Git Collaboration Guide for LibraryHub

This guide explains how to use Git for collaborating on our LibraryHub project.

## Initial Setup (First-time only)

1. **Clone the repository**
   ```
   git clone [repository-url]
   cd LibraryHub
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

## Daily Workflow

### 1. Before Starting Work

Always get the latest changes before you start working:

```
git pull origin main
```

### 2. Creating a Branch for Your Task

Create and switch to a new branch for your specific task:

```
git checkout -b feature/your-feature-name
```

Use descriptive branch names like `feature/add-search-functionality` or `bugfix/fix-login-issue`.

### 3. Making Changes

Work on your assigned task and make changes to the codebase.

### 4. Committing Your Changes

Check which files you've modified:

```
git status
```

Add your changes to be committed:

```
git add .                  # Add all changes
# OR
git add specific-file.py   # Add specific files
```

Commit your changes with a descriptive message:

```
git commit -m "Add clear description of your changes"
```

 commit message examples:
- "Add book search functionality"
- "Fix bug in login validation"
- "Update UI design for homepage"

### 5. Pushing Your Changes

Push your branch to the remote repository:

```
git push origin feature/your-feature-name
```

### 6. Creating a Pull Request

1. Go to our GitHub repository in your browser
2. Click on "Pull Requests" then "New Pull Request"
3. Select your branch to compare with main
4. Add a title and description for your changes
5. Request reviews from teammates
6. Click "Create Pull Request"

### 7. Handling Merge Conflicts

If Git indicates merge conflicts:

1. Pull the latest main branch
   ```
   git checkout main
   git pull origin main
   ```

2. Switch back to your branch and merge main
   ```
   git checkout feature/your-feature-name
   git merge main
   ```

3. Resolve the conflicts in your code editor (look for the conflict markers `<<<<<<<`, `=======`, and `>>>>>>>`)

4. After resolving all conflicts:
   ```
   git add .
   git commit -m "Resolve merge conflicts"
   git push origin feature/your-feature-name
   ```

## Useful Git Commands

- **Check repository status**: `git status`
- **View commit history**: `git log`
- **Discard local changes to a file**: `git checkout -- filename`
- **Create and switch to a new branch**: `git checkout -b branch-name`
- **Switch between branches**: `git checkout branch-name`
- **Update your local branch with changes from main**: `git pull origin main`

