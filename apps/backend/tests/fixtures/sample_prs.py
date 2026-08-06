# ============================================================
# CodeWhisper PR - Sample PR Fixtures
# ============================================================

SAMPLE_PR_DIFF = """
diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,5 @@
 import os
-from typing import List
+from typing import List, Optional

 def process_data(data: List[str]) -> List[str]:
-    return [x.upper() for x in data]
+    return [x.strip().upper() for x in data if x]

 def main():
-    data = ["hello", "world"]
+    data = ["hello", "world", ""]
     result = process_data(data)
     print(result)
"""

SAMPLE_PR_FILES = [
    {
        "path": "src/main.py",
        "content": "import os\nfrom typing import List, Optional\n\ndef process_data(data: List[str]) -> List[str]:\n    return [x.strip().upper() for x in data if x]\n\ndef main():\n    data = [\"hello\", \"world\", \"\"]\n    result = process_data(data)\n    print(result)\n",
        "changes": [
            {
                "type": "modified",
                "lines": [2, 5, 8],
                "old_content": "from typing import List",
                "new_content": "from typing import List, Optional"
            }
        ]
    }
]
