# Guide to Upload LibraryHub to GitHub

This guide provides step-by-step instructions for uploading your entire LibraryHub project to GitHub.

## Prerequisites

- GitHub account (create one at [github.com](https://github.com) if you don't have one)
- Git installed on your computer (download from [git-scm.com](https://git-scm.com/downloads))

## Step 1: Create a New GitHub Repository

1. **Login to GitHub** at [github.com](https://github.com)
2. **Click the "+" icon** in the top right corner
3. **Select "New repository"**
4. **Enter repository details**:
   - Name: "LibraryHub" (or your preferred name)
   - Description: "A simple library management system built with Flask"
   - Visibility: Public or Private (your choice)
   - Do NOT initialize with README, .gitignore, or license (we'll push your existing files)
5. **Click "Create repository"**

## Step 2: Prepare Your Local Project

1. **Open a terminal or command prompt**
2. **Navigate to your project folder**:
   ```
   cd path/to/LibraryHub
   ```

3. **Initialize Git** (if not already done):
   ```
   git init
   ```

4. **Create a .gitignore file** to exclude unnecessary files:
   ```
   # Create .gitignore file
   touch .gitignore
   ```

5. **Add the following content to .gitignore** (open in a text editor and paste):
   ```
   # Virtual Environment
   venv/
   env/
   ENV/
   
   # Python cache files
   __pycache__/
   *.py[cod]
   *$py.class
   
   # Distribution / packaging
   dist/
   build/
   *.egg-info/
   
   # Local environment variables
   .env
   
   # IDE specific files
   .idea/
   .vscode/
   *.swp
   *.swo
   
   # OS specific files
   .DS_Store
   Thumbs.db
   ```

## Step 3: Add and Commit Files

1. **Stage all files** (add them to be committed):
   ```
   git add .
   ```

2. **Commit the files** with a descriptive message:
   ```
   git commit -m "Initial commit of LibraryHub project"
   ```

## Step 4: Link and Push to GitHub

1. **Link your local repository to GitHub** (replace with your GitHub username and repository name):
   ```
   git remote add origin https://github.com/YOUR_USERNAME/LibraryHub.git
   ```

2. **Push your files to GitHub**:
   ```
   git push -u origin main
   ```
   
   Note: If your default branch is named "master" instead of "main", use this command:
   ```
   git push -u origin master
   ```

3. **If prompted**, enter your GitHub username and password or token
   - If you have two-factor authentication enabled, you'll need to use a personal access token instead of a password
   - To create a personal access token: GitHub > Settings > Developer settings > Personal access tokens

## Step 5: Verify the Upload

1. **Refresh your GitHub repository page** in your browser
2. **You should see all your files** listed in the repository
3. **Check that important files** like app.py, schema.sql, and requirements.txt are present

## Step 6: Add Collaborators (Optional)

1. **Go to your repository** on GitHub
2. **Click "Settings"**
3. **Select "Manage access"** from the left sidebar
4. **Click "Invite a collaborator"**
5. **Enter GitHub usernames or email addresses** of your team members
6. **Set permission levels** and send invitations

## Troubleshooting Common Issues

### "Fatal: remote origin already exists"
```
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/LibraryHub.git
```

### "Failed to push some refs"
```
git pull --rebase origin main
git push origin main
```

### Large files rejected
GitHub has a file size limit (100MB). If you have large files:
1. Add them to .gitignore
2. Consider using Git LFS for large files
3. Or remove them from the repository:
   ```
   git rm --cached LARGE_FILE_NAME
   git commit -m "Remove large file"
   git push origin main
   ```

### Authentication Issues
If you're having trouble authenticating:
1. Try using a personal access token instead of your password
2. Or set up SSH keys for more secure authentication 