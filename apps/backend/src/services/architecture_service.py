# ============================================================
# CodeWhisper PR - Architecture Analysis Service
# ============================================================

import os
import ast
from typing import Dict, List, Tuple
from loguru import logger

from src.services.git_service import GitService


class ArchitectureService:
    def __init__(self):
        self.git = GitService()

    def analyze_repository(self, repo_url: str, branch: str = "main") -> Dict:
        repo_path = self.git.clone_repository(repo_url, branch)
        module_map = {}  # path -> set(imported modules)

        for root, dirs, files in os.walk(repo_path):
            for f in files:
                if not f.endswith(".py"):
                    continue
                full = os.path.join(root, f)
                rel = os.path.relpath(full, repo_path)
                try:
                    with open(full, "r", encoding="utf-8") as fh:
                        src = fh.read()
                    tree = ast.parse(src)
                    imports = self._extract_imports(tree)
                    module_map[rel] = imports
                except Exception as e:
                    logger.warning(f"Failed to parse {rel}: {e}")

        summary = self._analyze_graph(module_map)
        summary["repo_path"] = repo_path
        return summary

    def _extract_imports(self, tree) -> List[str]:
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return list(imports)

    def _analyze_graph(self, module_map: Dict[str, List[str]]) -> Dict:
        nodes = list(module_map.keys())
        in_degree = {n: 0 for n in nodes}
        out_degree = {n: len(module_map.get(n, [])) for n in nodes}

        # naive mapping of imports to files by name
        name_to_files = {}
        for f in nodes:
            name = os.path.splitext(os.path.basename(f))[0]
            name_to_files.setdefault(name, []).append(f)

        adjacency = {n: [] for n in nodes}
        for f, imports in module_map.items():
            for imp in imports:
                targets = name_to_files.get(imp, [])
                for t in targets:
                    adjacency[f].append(t)
                    in_degree[t] = in_degree.get(t, 0) + 1

        # detect simple cycles using DFS
        cycles = []
        visited = set()
        stack = []

        def dfs(node, path):
            visited.add(node)
            path.append(node)
            for nbr in adjacency.get(node, []):
                if nbr in path:
                    idx = path.index(nbr)
                    cycles.append(path[idx:] + [nbr])
                elif nbr not in visited:
                    dfs(nbr, path.copy())

        for n in nodes:
            if n not in visited:
                dfs(n, [])

        top_in = sorted(in_degree.items(), key=lambda x: -x[1])[:10]
        top_out = sorted(out_degree.items(), key=lambda x: -x[1])[:10]

        return {
            "files_analyzed": len(nodes),
            "top_in_degree": top_in,
            "top_out_degree": top_out,
            "cycles": cycles,
            "adjacency_sample": {k: adjacency[k][:5] for k in list(adjacency)[:20]},
        }
