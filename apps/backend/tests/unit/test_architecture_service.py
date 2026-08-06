from src.services.architecture_service import ArchitectureService


def test_extract_imports_simple():
    svc = ArchitectureService()
    code = """
import os
from collections import defaultdict
from mypkg import utils
"""
    tree = __import__('ast').parse(code)
    imports = svc._extract_imports(tree)
    assert "os" in imports
    assert "collections" in imports or "collections" in [i.split('.')[0] for i in imports]
