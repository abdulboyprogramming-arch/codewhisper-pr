# ============================================================
# CodeWhisper PR - Git Service
# ============================================================

import tempfile
import os
from typing import Dict, List, Optional, Tuple
from loguru import logger

from src.core.exceptions import GitError


class GitService:
    """Service for handling Git operations."""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="codewhisper-")
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Git temporary directory: {self.temp_dir}")

    def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """Clone a repository to a temporary directory."""
        try:
            from git import Repo, GitCommandError
        except ImportError:
            logger.warning("GitPython not installed. Using fallback clone.")
            return self._clone_with_subprocess(repo_url, branch)

        try:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.temp_dir, repo_name)

            if os.path.exists(repo_path):
                logger.info(f"Updating existing repository: {repo_path}")
                repo = Repo(repo_path)
                repo.git.fetch()
                repo.git.checkout(branch)
                repo.git.pull()
            else:
                logger.info(f"Cloning repository: {repo_url}")
                Repo.clone_from(repo_url, repo_path, branch=branch)

            return repo_path

        except Exception as e:
            logger.error(f"Git clone failed: {str(e)}")
            return self._clone_with_subprocess(repo_url, branch)

    def _clone_with_subprocess(self, repo_url: str, branch: str = "main") -> str:
        """Fallback clone using git command."""
        try:
            import subprocess
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_path = os.path.join(self.temp_dir, repo_name)

            if os.path.exists(repo_path):
                subprocess.run(["git", "-C", repo_path, "fetch"], check=True)
                subprocess.run(["git", "-C", repo_path, "checkout", branch], check=True)
                subprocess.run(["git", "-C", repo_path, "pull"], check=True)
            else:
                subprocess.run(
                    ["git", "clone", "-b", branch, repo_url, repo_path],
                    check=True,
                    capture_output=True,
                )

            return repo_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Git subprocess clone failed: {str(e)}")
            raise GitError(f"Failed to clone repository: {e.stderr.decode() if e.stderr else str(e)}")

    def get_pull_request_diff(
        self, repo_path: str, pr_number: int
    ) -> Tuple[str, List[Dict]]:
        """Get the diff and affected files for a PR."""
        try:
            import subprocess

            # Fetch PR
            try:
                subprocess.run(
                    ["git", "-C", repo_path, "fetch", "origin", f"pull/{pr_number}/head:pr/{pr_number}"],
                    check=True, capture_output=True
                )
                subprocess.run(
                    ["git", "-C", repo_path, "checkout", f"pr/{pr_number}"],
                    check=True, capture_output=True
                )
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["git", "-C", repo_path, "fetch", "origin"],
                    check=True, capture_output=True
                )

            # Get merge base
            try:
                result = subprocess.run(
                    ["git", "-C", repo_path, "merge-base", "HEAD", "origin/main"],
                    check=True, capture_output=True, text=True
                )
                base = result.stdout.strip()
            except subprocess.CalledProcessError:
                try:
                    result = subprocess.run(
                        ["git", "-C", repo_path, "merge-base", "HEAD", "origin/master"],
                        check=True, capture_output=True, text=True
                    )
                    base = result.stdout.strip()
                except subprocess.CalledProcessError:
                    base = "HEAD~1"

            # Get diff
            diff_result = subprocess.run(
                ["git", "-C", repo_path, "diff", base, "HEAD"],
                check=True, capture_output=True, text=True
            )
            diff_content = diff_result.stdout

            # Get changed files
            files_result = subprocess.run(
                ["git", "-C", repo_path, "diff", "--name-only", base, "HEAD"],
                check=True, capture_output=True, text=True
            )
            changed_files = [f.strip() for f in files_result.stdout.strip().splitlines() if f.strip()]

            files = []
            for f in changed_files:
                content = self._get_file_content(repo_path, f)
                files.append({
                    "path": f,
                    "content": content,
                    "changes": [{"type": "modified", "lines": []}]
                })

            return diff_content, files

        except Exception as e:
            logger.error(f"Failed to get PR diff: {str(e)}")
            return "", []

    def _get_file_content(self, repo_path: str, file_path: str) -> Optional[str]:
        """Get content of a specific file at HEAD."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "-C", repo_path, "show", f"HEAD:{file_path}"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None

    def cleanup(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()
