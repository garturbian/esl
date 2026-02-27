# My Eleventy Site

A static website built with [Eleventy (11ty)](https://www.11ty.dev/).

## Getting Started

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Run locally with hot-reloading:**
    ```bash
    npm start
    ```

3.  **Build for production:**
    ```bash
    npm run build
    ```

## Deployment

This project is configured to deploy to GitHub Pages automatically via GitHub Actions whenever changes are pushed to the `main` branch.

### How to Publish

1.  Create a new repository on GitHub.
2.  Initialize git locally:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    ```
3.  Link your local repo to GitHub:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git branch -M main
    git push -u origin main
    ```
4.  In your GitHub repository settings, go to **Pages** and ensure the **Source** is set to **GitHub Actions**.