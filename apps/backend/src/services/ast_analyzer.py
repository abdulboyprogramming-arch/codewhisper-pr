# ============================================================
# CodeWhisper PR - AST Analyzer Service
# ============================================================

import re
from typing import Dict, Any, List, Optional
from loguru import logger

try:
    from tree_sitter import Language
    from tree_sitter_languages import get_parser
    _TREE_SITTER_AVAILABLE = True
except ImportError:
    _TREE_SITTER_AVAILABLE = False
    logger.warning("Tree-sitter not available, AST analysis will be limited")


class ASTAnalyzer:
    """Service for analyzing code using AST parsing."""

    def __init__(self):
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
        }

        self.parsers = {}
        if _TREE_SITTER_AVAILABLE:
            for lang in ['python', 'javascript', 'typescript', 'go', 'rust', 'java', 'cpp']:
                try:
                    self.parsers[lang] = get_parser(lang)
                except Exception as e:
                    logger.warning(f"Could not load parser for {lang}: {str(e)}")

    async def analyze_changes(
        self,
        affected_files: List[Dict[str, Any]],
        diff_content: str,
    ) -> Dict[str, Any]:
        """Analyze code changes using AST parsing."""
        analysis = {
            "summary": "",
            "affected_symbols": [],
            "important_changes": [],
            "file_stats": {},
            "language_stats": {},
        }

        if not affected_files:
            return analysis

        all_symbols = []
        all_changes = []
        file_stats = {}
        language_stats = {}

        for file_info in affected_files:
            file_path = file_info.get('path', '')
            content = file_info.get('content', '')

            if not content:
                continue

            extension = self._get_extension(file_path)
            language = self.language_map.get(extension, 'python')
            language_stats[language] = language_stats.get(language, 0) + 1

            file_stats[file_path] = {
                'lines': len(content.splitlines()),
                'changes': len(file_info.get('changes', [])),
                'language': language,
            }

            if language in self.parsers:
                symbols = self._extract_symbols(content, language)
                all_symbols.extend(symbols)

                for change in file_info.get('changes', []):
                    changed_symbols = self._find_changed_symbols(content, change, symbols, language)
                    if changed_symbols:
                        all_changes.extend(changed_symbols)

        analysis["affected_symbols"] = all_symbols[:20]
        analysis["important_changes"] = all_changes[:20]
        analysis["file_stats"] = file_stats
        analysis["language_stats"] = language_stats

        summary_parts = [
            f"Affected {len(affected_files)} files",
            f"Across {len(language_stats)} languages",
        ]

        if all_symbols:
            summary_parts.append(f"Found {len(all_symbols)} affected symbols")

        analysis["summary"] = ". ".join(summary_parts)

        return analysis

    def _get_extension(self, file_path: str) -> str:
        import os
        return os.path.splitext(file_path)[1].lower()

    def _extract_symbols(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract symbols from code using AST."""
        symbols = []

        try:
            parser = self.parsers.get(language)
            if not parser:
                return symbols

            tree = parser.parse(bytes(content, 'utf-8'))
            root_node = tree.root_node

            symbol_types = {
                'python': ['function_definition', 'class_definition'],
                'javascript': ['function_declaration', 'class_declaration'],
                'typescript': ['function_declaration', 'class_declaration', 'interface_declaration'],
                'go': ['function_declaration', 'method_declaration', 'type_declaration'],
                'rust': ['function_item', 'struct_item', 'impl_item'],
            }

            node_types = symbol_types.get(language, ['function_definition', 'class_definition'])
            self._traverse_tree(root_node, node_types, symbols, content)

        except Exception as e:
            logger.warning(f"AST extraction failed for {language}: {str(e)}")

        return symbols

    def _traverse_tree(self, node, node_types: List[str], symbols: List[Dict[str, Any]], content: str):
        """Traverse AST tree to find symbols."""
        if node.type in node_types:
            name = self._get_node_name(node, content)
            if name:
                symbol = {
                    'name': name,
                    'type': node.type,
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'text': content[node.start_byte:node.end_byte][:100],
                }
                symbols.append(symbol)

        for child in node.children:
            self._traverse_tree(child, node_types, symbols, content)

    def _get_node_name(self, node, content: str) -> Optional[str]:
        """Extract symbol name from AST node."""
        try:
            text = content[node.start_byte:node.end_byte]
            name_match = re.search(r'(def|class|function|struct)\s+([a-zA-Z_][a-zA-Z0-9_]*)', text)
            if name_match:
                return name_match.group(2)
        except Exception:
            pass
        return None

    def _find_changed_symbols(
        self, content: str, change: Dict[str, Any], symbols: List[Dict[str, Any]], language: str
    ) -> List[Dict[str, Any]]:
        """Find symbols affected by a change."""
        affected = []

        for symbol in symbols:
            if change.get('lines') and symbol.get('start_line'):
                for line in change['lines']:
                    start = symbol['start_line']
                    end = symbol.get('end_line', float('inf'))
                    if start <= line <= end:
                        affected.append(symbol)
                        break

        return affected
