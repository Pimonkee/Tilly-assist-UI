"use client";

import { useState } from "react";

interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  html_url: string;
  clone_url: string;
  default_branch: string;
  updated_at: string;
  created_at: string;
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
}

interface BuildStatus {
  [key: string]: {
    status: "idle" | "building" | "success" | "error";
    message: string;
  };
}

export function RepositoryList() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [buildStatus, setBuildStatus] = useState<BuildStatus>({});

  const fetchRepositories = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/repositories");
      if (!response.ok) {
        throw new Error("Failed to fetch repositories");
      }
      const data = await response.json();
      setRepositories(data.repositories);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const triggerBuild = async (repoName: string, owner: string, defaultBranch: string) => {
    setBuildStatus((prev) => ({
      ...prev,
      [repoName]: { status: "building", message: "Triggering build..." },
    }));

    try {
      const response = await fetch("/api/build", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ repoName, owner, defaultBranch }),
      });

      const data = await response.json();

      if (data.success) {
        setBuildStatus((prev) => ({
          ...prev,
          [repoName]: {
            status: "success",
            message: data.message || "Build triggered successfully",
          },
        }));
      } else {
        setBuildStatus((prev) => ({
          ...prev,
          [repoName]: {
            status: "error",
            message: data.message || data.error || "Failed to trigger build",
          },
        }));
      }
    } catch (err) {
      setBuildStatus((prev) => ({
        ...prev,
        [repoName]: {
          status: "error",
          message: err instanceof Error ? err.message : "An error occurred",
        },
      }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 to-neutral-100 p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8">
          <h1 className="mb-2 text-4xl font-bold text-zinc-900">
            Tilly Repository Builder
          </h1>
          <p className="text-lg text-zinc-600">
            Build and compile all repositories under the Pimonkee profile
          </p>
        </div>

        <button
          onClick={fetchRepositories}
          disabled={loading}
          className="mb-8 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Fetch Repositories"}
        </button>

        {error && (
          <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-700">
            Error: {error}
          </div>
        )}

        {repositories.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {repositories.map((repo) => (
              <div
                key={repo.id}
                className="rounded-xl bg-white p-6 shadow-md transition-shadow hover:shadow-lg"
              >
                <div className="mb-4">
                  <h3 className="mb-2 text-xl font-bold text-zinc-900">
                    {repo.name}
                  </h3>
                  {repo.description && (
                    <p className="mb-3 text-sm text-zinc-600">
                      {repo.description}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {repo.language && (
                      <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-800">
                        {repo.language}
                      </span>
                    )}
                    <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-800">
                      ⭐ {repo.stargazers_count}
                    </span>
                  </div>
                </div>

                <div className="mb-4 flex gap-2">
                  <a
                    href={repo.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 rounded-lg bg-gray-200 px-4 py-2 text-center text-sm font-medium text-gray-800 transition-colors hover:bg-gray-300"
                  >
                    View on GitHub
                  </a>
                </div>

                <button
                  onClick={() => {
                    const [owner, repoName] = repo.full_name.split("/");
                    triggerBuild(repoName, owner, repo.default_branch);
                  }}
                  disabled={buildStatus[repo.name]?.status === "building"}
                  className="w-full rounded-lg bg-green-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-green-700 disabled:opacity-50"
                >
                  {buildStatus[repo.name]?.status === "building"
                    ? "Building..."
                    : "Trigger Build"}
                </button>

                {buildStatus[repo.name] && (
                  <div
                    className={`mt-3 rounded-lg p-3 text-sm ${
                      buildStatus[repo.name].status === "success"
                        ? "bg-green-50 text-green-700"
                        : buildStatus[repo.name].status === "error"
                          ? "bg-red-50 text-red-700"
                          : "bg-blue-50 text-blue-700"
                    }`}
                  >
                    {buildStatus[repo.name].message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {repositories.length === 0 && !loading && !error && (
          <div className="rounded-lg bg-white p-8 text-center shadow-md">
            <p className="text-zinc-600">
              Click &quot;Fetch Repositories&quot; to load repositories from the Pimonkee
              profile
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
