import { NextResponse } from "next/server";
import { Octokit } from "@octokit/rest";

export async function GET() {
  try {
    const token = process.env.GITHUB_TOKEN;
    
    if (!token) {
      return NextResponse.json(
        { error: "GitHub token not configured. Please set GITHUB_TOKEN in environment variables." },
        { status: 500 }
      );
    }

    const octokit = new Octokit({
      auth: token,
    });

    const username = "Pimonkee";
    
    const { data: repos } = await octokit.repos.listForUser({
      username,
      type: "all",
      sort: "updated",
      per_page: 100,
    });

    const repoData = repos.map((repo) => ({
      id: repo.id,
      name: repo.name,
      full_name: repo.full_name,
      description: repo.description,
      language: repo.language,
      html_url: repo.html_url,
      clone_url: repo.clone_url,
      default_branch: repo.default_branch,
      updated_at: repo.updated_at,
      created_at: repo.created_at,
      stargazers_count: repo.stargazers_count,
      forks_count: repo.forks_count,
      open_issues_count: repo.open_issues_count,
    }));

    return NextResponse.json({ repositories: repoData });
  } catch (error) {
    console.error("Error fetching repositories:", error);
    return NextResponse.json(
      { error: "Failed to fetch repositories" },
      { status: 500 }
    );
  }
}
