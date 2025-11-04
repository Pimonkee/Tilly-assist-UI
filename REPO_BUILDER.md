# Tilly Repository Builder

This repository has been enhanced with a **Repository Builder UI** that allows you to view, manage, and build all repositories under the Pimonkee GitHub profile through a unified web interface.

## New Application: Repo Builder

Located in `apps/repo-builder/`, this Next.js application provides:

### Features

✅ **Repository Dashboard** - View all repositories from the Pimonkee GitHub profile
- Repository names, descriptions, and metadata
- Programming language tags
- Star counts and repository stats
- Direct links to GitHub

✅ **Build Automation** - Trigger builds for repositories with GitHub Actions
- One-click build triggers
- Real-time build status feedback
- Workflow detection and execution

✅ **Modern UI** - Clean, responsive interface built with:
- Next.js 16 with App Router
- React 19
- TypeScript
- Tailwind CSS
- GitHub Octokit API client

### Quick Start

1. **Navigate to the repo-builder app:**
   ```bash
   cd apps/repo-builder
   ```

2. **Set up GitHub authentication:**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` and add your GitHub Personal Access Token:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```
   
   Create a token at: https://github.com/settings/tokens
   - Required scopes: `repo`, `workflow`

3. **Install dependencies (from repository root):**
   ```bash
   pnpm install
   ```

4. **Run the development server:**
   ```bash
   pnpm --filter=@assistant-ui/repo-builder dev
   ```

5. **Open in browser:**
   ```
   http://localhost:3020
   ```

### Usage

1. **Fetch Repositories** - Click the button to load all repositories from the Pimonkee profile
2. **Browse** - Scroll through repository cards to see details
3. **View on GitHub** - Click to open any repository on GitHub
4. **Trigger Builds** - Click "Trigger Build" to run GitHub Actions workflows (if configured)

### Screenshots

**Initial View:**
![Initial UI](https://github.com/user-attachments/assets/7229cff8-ce73-476e-9e75-1bf34f043276)

**Error Handling:**
![Error State](https://github.com/user-attachments/assets/47c7da76-d865-4ab0-a171-408315923a7d)

### Requirements

- **GitHub Personal Access Token** with `repo` and `workflow` scopes
- **Node.js 18+**
- **pnpm** package manager

### Repository Structure

```
apps/repo-builder/
├── app/
│   ├── api/
│   │   ├── repositories/     # Fetch repositories from GitHub
│   │   │   └── route.ts
│   │   └── build/           # Trigger repository builds
│   │       └── route.ts
│   ├── layout.tsx           # App layout
│   ├── page.tsx             # Main page
│   └── globals.css          # Global styles
├── components/
│   └── RepositoryList.tsx   # Main UI component
├── package.json
├── README.md
└── .env.example
```

### API Endpoints

- `GET /api/repositories` - Fetches all repositories from the Pimonkee profile
- `POST /api/build` - Triggers a build for a specific repository

### Building for Production

```bash
pnpm --filter=@assistant-ui/repo-builder build
```

### Notes

- Repositories must have GitHub Actions workflows configured to enable build triggers
- Build triggers use the `workflow_dispatch` event
- The app displays build status but doesn't poll for real-time updates
- All API calls go through the Next.js backend to keep the GitHub token secure

### Future Enhancements

Potential improvements:
- Real-time build status polling
- Build logs viewer
- Multiple workflow support
- Batch build operations
- Build history tracking
- Webhook integration for automatic updates

## Original Assistant UI

This repository is a fork of [assistant-ui](https://github.com/assistant-ui/assistant-ui), a library for building AI chat interfaces in React. The original functionality remains intact in the `packages/`, `examples/`, and other `apps/` directories.

For documentation on the original assistant-ui library, see the [main README](./README.md).
