# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))