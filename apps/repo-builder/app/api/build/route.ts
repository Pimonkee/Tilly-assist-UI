import { NextRequest, NextResponse } from "next/server";
import { Octokit } from "@octokit/rest";

export async function POST(request: NextRequest) {
  try {
    const { repoName, owner } = await request.json();

    if (!repoName || !owner) {
      return NextResponse.json(
        { error: "Repository name and owner are required" },
        { status: 400 }
      );
    }

    const octokit = new Octokit({
      auth: process.env.GITHUB_TOKEN,
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
      
      try {
        await octokit.actions.createWorkflowDispatch({
          owner,
          repo: repoName,
          workflow_id: workflow.id,
          ref: "main", // or "master" depending on default branch
        });

        return NextResponse.json({
          success: true,
          message: `Build triggered for ${repoName}`,
          workflow: workflow.name,
        });
      } catch (dispatchError: any) {
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
