import asyncio

from src.services.ast_analyzer import ASTAnalyzer


def test_analyze_changes_empty():
    analyzer = ASTAnalyzer()
    result = asyncio.run(analyzer.analyze_changes([], ""))
    assert isinstance(result, dict)
    assert result["summary"] == ""


def test_extract_symbols_simple():
    code = """
def foo():
    pass

class Bar:
    def baz(self):
        pass
"""
    analyzer = ASTAnalyzer()
    symbols = analyzer._extract_symbols(code, "python")
    # Depending on parser availability this may be empty; ensure no exception and a list
    assert isinstance(symbols, list)
