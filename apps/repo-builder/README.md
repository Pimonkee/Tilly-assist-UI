# Tilly Repository Builder

A web application to view, build, and compile all repositories under the Pimonkee GitHub profile.

## Features

- **View Repositories**: Fetch and display all repositories from the Pimonkee GitHub profile
- **Repository Details**: See descriptions, languages, stars, and other metadata
- **Build Trigger**: Trigger GitHub Actions workflows for each repository
- **Build Status**: Monitor build status for each repository
- **Direct Links**: Quick access to view repositories on GitHub

## Setup

1. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

2. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo` and `workflow`
   - Copy the token and add it to `.env.local`:
     ```
     GITHUB_TOKEN=your_token_here
     ```

3. Install dependencies (from the repository root):
   ```bash
   pnpm install
   ```

4. Run the development server:
   ```bash
   pnpm --filter=@assistant-ui/repo-builder dev
   ```

5. Open http://localhost:3020 in your browser

## Usage

1. Click "Fetch Repositories" to load all repositories from the Pimonkee profile
2. Browse through the repository cards to see details
3. Click "Trigger Build" on any repository to start a build (if GitHub Actions workflows are configured)
4. Monitor build status messages displayed on each card

## Requirements

- Node.js 18+
- pnpm package manager
- GitHub Personal Access Token with `repo` and `workflow` scopes

## Build for Production

```bash
pnpm --filter=@assistant-ui/repo-builder build
```

## Technologies

- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Octokit**: GitHub API client
- **React 19**: Latest React version

## Notes

- Repositories must have GitHub Actions workflows configured to enable builds
- The build trigger uses the `workflow_dispatch` event, which must be configured in workflow files
- Build status is tracked in the UI but does not poll for real-time updates
