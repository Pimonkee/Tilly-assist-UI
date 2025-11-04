import { NextRequest, NextResponse } from "next/server";
import { Octokit } from "@octokit/rest";

export async function POST(request: NextRequest) {
  try {
    const { repoName, owner, defaultBranch } = await request.json();

    if (!repoName || !owner) {
      return NextResponse.json(
        { error: "Repository name and owner are required" },
        { status: 400 }
      );
    }

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

    // Check if repository has GitHub Actions workflows
    try {
      const { data: workflows } = await octokit.actions.listRepoWorkflows({
        owner,
        repo: repoName,
      });

      if (workflows.total_count === 0) {
        return NextResponse.json({
          success: false,
          message: "No GitHub Actions workflows found in repository",
          workflows: [],
        });
      }

      // Trigger the first workflow found
      const workflow = workflows.workflows[0];
      const branch = defaultBranch || "main";
      
      try {
        await octokit.actions.createWorkflowDispatch({
          owner,
          repo: repoName,
          workflow_id: workflow.id,
          ref: branch,
        });

        return NextResponse.json({
          success: true,
          message: `Build triggered for ${repoName}`,
          workflow: workflow.name,
        });
      } catch (dispatchError) {
        console.error("Workflow dispatch error:", dispatchError);
        return NextResponse.json({
          success: false,
          message: `Workflow found but manual trigger not enabled: ${workflow.name}`,
          workflows: workflows.workflows.map((w) => ({
            name: w.name,
            path: w.path,
          })),
        });
      }
    } catch (workflowError: any) {
      if (workflowError.status === 404) {
        return NextResponse.json({
          success: false,
          message: "No GitHub Actions configured for this repository",
          suggestion: "Add a .github/workflows directory with workflow files to enable builds",
        });
      }
      throw workflowError;
    }
  } catch (error: any) {
    console.error("Error triggering build:", error);
    return NextResponse.json(
      { 
        error: "Failed to trigger build",
        message: error.message 
      },
      { status: 500 }
    );
  }
}
