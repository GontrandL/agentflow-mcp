"""
Project Scanner - APC Project Structure Awareness

This module implements project scanning and indexing for APC:
1. Scans entire project directory structure
2. Indexes files by type (code, tests, docs, UI, configs)
3. Detects dependencies and imports
4. Generates architecture map
5. Creates project_index.json for fast queries

**Use Case Example:**
Worker Agent: "I need to create a new validation module"
APC Query: "What validation patterns exist in the project?"
APC Response: "3 validators found: quality_evaluator.py, hybrid_orchestrator.py (validation loop),
              apc_agentflow_bridge.py (validation scoring). Follow pattern: class + _validate_output method"
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import ast
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FileMetadata:
    """
    Metadata for a single file in the project.

    Attributes:
        path: Relative path from project root
        type: File type (code, test, doc, config, ui, other)
        language: Programming language (python, javascript, typescript, markdown, etc.)
        size_bytes: File size in bytes
        lines: Total line count
        last_modified: Last modification timestamp
        imports: List of import statements (for code files)
        exports: List of exported classes/functions (for code files)
        tests: List of test files that test this file
        dependencies: List of files this file depends on
        description: First docstring or comment
    """
    path: str
    type: str
    language: str
    size_bytes: int
    lines: int
    last_modified: str
    imports: List[str]
    exports: List[str]
    tests: List[str]
    dependencies: List[str]
    description: Optional[str] = None


@dataclass
class ProjectIndex:
    """
    Complete project index with file metadata and structure.

    Attributes:
        scanned_at: Timestamp of scan
        project_root: Absolute path to project root
        total_files: Total number of files indexed
        structure: Directory structure with file counts
        files: List of FileMetadata for all indexed files
        dependency_graph: Graph of file dependencies
        patterns: Detected coding patterns
    """
    scanned_at: str
    project_root: str
    total_files: int
    structure: Dict[str, Any]
    files: List[Dict[str, Any]]
    dependency_graph: Dict[str, List[str]]
    patterns: Dict[str, Any]


class ProjectScanner:
    """
    Project Scanner for APC Project Structure Awareness.

    This class scans the project directory and creates a comprehensive index
    of all files, dependencies, and patterns for APC to use as project memory.
    """

    # File type mappings
    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.cpp', '.c', '.h'}
    TEST_PATTERNS = {'test_', '_test.', 'spec.', '.test.', '.spec.'}
    DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.adoc'}
    CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg'}
    UI_EXTENSIONS = {'.tsx', '.jsx', '.vue', '.html', '.css', '.scss', '.sass'}

    def __init__(
        self,
        project_root: str,
        scan_depth: int = 5,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize Project Scanner.

        Args:
            project_root: Absolute path to project root
            scan_depth: Maximum depth to scan (default: 5)
            include_patterns: Glob patterns to include (default: all code files)
            exclude_patterns: Glob patterns to exclude (default: node_modules, .venv, etc.)
        """
        self.project_root = Path(project_root).resolve()
        self.scan_depth = scan_depth
        self.include_patterns = include_patterns or ['**/*.py', '**/*.js', '**/*.ts', '**/*.md']
        self.exclude_patterns = exclude_patterns or [
            '**/node_modules/**',
            '**/.venv/**',
            '**/venv/**',
            '**/__pycache__/**',
            '**/dist/**',
            '**/build/**',
            '**/.git/**',
            '**/.apc/**'  # Don't scan APC's own directory
        ]

        logger.info(
            "project_scanner_initialized",
            project_root=str(self.project_root),
            scan_depth=scan_depth
        )

    def scan_project(self) -> ProjectIndex:
        """
        Scan entire project and create comprehensive index.

        Returns:
            ProjectIndex with all file metadata and structure
        """
        logger.info("project_scan_started")
        start_time = datetime.now()

        # STEP 1: Collect all files
        all_files = self._collect_files()
        logger.info("files_collected", total=len(all_files))

        # STEP 2: Analyze each file
        file_metadata_list = []
        for file_path in all_files:
            try:
                metadata = self._analyze_file(file_path)
                file_metadata_list.append(metadata)
            except Exception as e:
                logger.warning("file_analysis_failed", file=str(file_path), error=str(e))

        logger.info("files_analyzed", total=len(file_metadata_list))

        # STEP 3: Build dependency graph
        dependency_graph = self._build_dependency_graph(file_metadata_list)
        logger.info("dependency_graph_built", edges=sum(len(deps) for deps in dependency_graph.values()))

        # STEP 4: Detect patterns
        patterns = self._detect_patterns(file_metadata_list)
        logger.info("patterns_detected", total=len(patterns))

        # STEP 5: Build directory structure
        structure = self._build_structure(file_metadata_list)

        # Create index
        project_index = ProjectIndex(
            scanned_at=datetime.now().isoformat(),
            project_root=str(self.project_root),
            total_files=len(file_metadata_list),
            structure=structure,
            files=[asdict(fm) for fm in file_metadata_list],
            dependency_graph=dependency_graph,
            patterns=patterns
        )

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            "project_scan_complete",
            total_files=len(file_metadata_list),
            duration_seconds=duration
        )

        return project_index

    def _collect_files(self) -> List[Path]:
        """
        Collect all files matching include patterns and not matching exclude patterns.

        Returns:
            List of Path objects for files to analyze
        """
        all_files = []

        for pattern in self.include_patterns:
            for file_path in self.project_root.glob(pattern):
                if not file_path.is_file():
                    continue

                # Check if excluded
                relative_path = file_path.relative_to(self.project_root)
                if self._is_excluded(str(relative_path)):
                    continue

                all_files.append(file_path)

        return list(set(all_files))  # Deduplicate

    def _is_excluded(self, relative_path: str) -> bool:
        """Check if path matches any exclude pattern."""
        from fnmatch import fnmatch
        for pattern in self.exclude_patterns:
            if fnmatch(relative_path, pattern):
                return True
        return False

    def _analyze_file(self, file_path: Path) -> FileMetadata:
        """
        Analyze a single file and extract metadata.

        Args:
            file_path: Absolute path to file

        Returns:
            FileMetadata with all extracted information
        """
        relative_path = str(file_path.relative_to(self.project_root))

        # Basic metadata
        stat = file_path.stat()
        size_bytes = stat.st_size
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.warning("file_read_failed", file=relative_path, error=str(e))
            content = ""

        lines = len(content.splitlines())

        # Determine file type and language
        file_type = self._determine_file_type(file_path)
        language = self._determine_language(file_path)

        # Extract imports and exports (code files only)
        imports = []
        exports = []
        description = None

        if file_type == 'code':
            imports = self._extract_imports(content, language)
            exports = self._extract_exports(content, language)
            description = self._extract_description(content, language)

        # Find test files
        tests = self._find_test_files(relative_path)

        # Dependencies (resolved later in dependency graph)
        dependencies = []

        return FileMetadata(
            path=relative_path,
            type=file_type,
            language=language,
            size_bytes=size_bytes,
            lines=lines,
            last_modified=last_modified,
            imports=imports,
            exports=exports,
            tests=tests,
            dependencies=dependencies,
            description=description
        )

    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type (code, test, doc, config, ui)."""
        name = file_path.name.lower()
        ext = file_path.suffix.lower()

        # Test files
        if any(pattern in name for pattern in self.TEST_PATTERNS):
            return 'test'

        # Documentation
        if ext in self.DOC_EXTENSIONS:
            return 'doc'

        # Configuration
        if ext in self.CONFIG_EXTENSIONS:
            return 'config'

        # UI files
        if ext in self.UI_EXTENSIONS:
            return 'ui'

        # Code files
        if ext in self.CODE_EXTENSIONS:
            return 'code'

        return 'other'

    def _determine_language(self, file_path: Path) -> str:
        """Determine programming language from extension."""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml'
        }
        return language_map.get(ext, 'unknown')

    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements from code."""
        imports = []

        if language == 'python':
            # Match: import foo, from foo import bar
            import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+([\w.,\s]+)'
            for line in content.splitlines():
                line = line.strip()
                match = re.match(import_pattern, line)
                if match:
                    imports.append(line)

        elif language in ['javascript', 'typescript']:
            # Match: import { foo } from 'bar', const foo = require('bar')
            import_patterns = [
                r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            for pattern in import_patterns:
                imports.extend(re.findall(pattern, content))

        return imports[:50]  # Limit to 50 imports

    def _extract_exports(self, content: str, language: str) -> List[str]:
        """Extract exported classes/functions from code."""
        exports = []

        if language == 'python':
            # Parse AST to find classes and functions
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        exports.append(f"class {node.name}")
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):  # Public functions only
                            exports.append(f"def {node.name}")
            except SyntaxError:
                pass

        elif language in ['javascript', 'typescript']:
            # Match: export class Foo, export function bar, export const baz
            export_patterns = [
                r'export\s+class\s+(\w+)',
                r'export\s+function\s+(\w+)',
                r'export\s+const\s+(\w+)',
                r'export\s+default\s+(\w+)'
            ]
            for pattern in export_patterns:
                matches = re.findall(pattern, content)
                exports.extend(matches)

        return exports[:50]  # Limit to 50 exports

    def _extract_description(self, content: str, language: str) -> Optional[str]:
        """Extract first docstring or comment as description."""
        if language == 'python':
            # Extract module docstring
            try:
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)
                if docstring:
                    # Return first line only
                    return docstring.split('\n')[0].strip()
            except SyntaxError:
                pass

        elif language in ['javascript', 'typescript']:
            # Extract first multi-line comment
            match = re.search(r'/\*\*?\s*([^\*]+)\*/', content)
            if match:
                return match.group(1).strip().split('\n')[0].strip()

        return None

    def _find_test_files(self, file_path: str) -> List[str]:
        """Find test files that test this file."""
        tests = []

        # Convert module path to test path patterns
        # e.g., agentflow/core/context_generator.py → tests/test_context_generator.py
        base_name = Path(file_path).stem

        # Common test patterns
        test_patterns = [
            f"tests/test_{base_name}.py",
            f"test_{base_name}.py",
            f"{base_name}_test.py",
            f"tests/{base_name}_test.py"
        ]

        for pattern in test_patterns:
            test_file = self.project_root / pattern
            if test_file.exists():
                tests.append(str(Path(pattern)))

        return tests

    def _build_dependency_graph(self, files: List[FileMetadata]) -> Dict[str, List[str]]:
        """
        Build dependency graph from file imports.

        Returns:
            Dict mapping file paths to list of files they depend on
        """
        graph = {}

        # Create path lookup
        path_to_file = {f.path: f for f in files}

        for file_metadata in files:
            dependencies = []

            # Resolve imports to file paths
            for import_stmt in file_metadata.imports:
                # Try to resolve import to actual file
                resolved = self._resolve_import(import_stmt, file_metadata.path, path_to_file)
                if resolved:
                    dependencies.append(resolved)

            file_metadata.dependencies = dependencies
            graph[file_metadata.path] = dependencies

        return graph

    def _resolve_import(
        self,
        import_stmt: str,
        current_file: str,
        path_lookup: Dict[str, FileMetadata]
    ) -> Optional[str]:
        """
        Resolve import statement to actual file path.

        Returns:
            Resolved file path or None if not found
        """
        # Python: from agentflow.core.context_generator import ContextGenerator
        if import_stmt.startswith('from ') or import_stmt.startswith('import '):
            # Extract module path
            match = re.search(r'(?:from\s+)?([\w.]+)', import_stmt)
            if match:
                module_path = match.group(1)
                # Convert module path to file path
                file_path = module_path.replace('.', '/') + '.py'
                if file_path in path_lookup:
                    return file_path

        return None

    def _detect_patterns(self, files: List[FileMetadata]) -> Dict[str, Any]:
        """
        Detect coding patterns in the project.

        Returns:
            Dict with detected patterns (naming conventions, architecture patterns, etc.)
        """
        patterns = {
            'naming_conventions': {},
            'architecture_patterns': [],
            'test_patterns': [],
            'common_exports': []
        }

        # Detect naming conventions
        class_names = []
        function_names = []

        for file_metadata in files:
            if file_metadata.type != 'code':
                continue

            for export in file_metadata.exports:
                if export.startswith('class '):
                    class_names.append(export.replace('class ', ''))
                elif export.startswith('def '):
                    function_names.append(export.replace('def ', ''))

        # Analyze naming patterns
        if class_names:
            patterns['naming_conventions']['classes'] = {
                'total': len(class_names),
                'examples': class_names[:10],
                'pattern': 'PascalCase'  # Could detect actual pattern
            }

        if function_names:
            patterns['naming_conventions']['functions'] = {
                'total': len(function_names),
                'examples': function_names[:10],
                'pattern': 'snake_case'  # Could detect actual pattern
            }

        # Detect architecture patterns
        if any('orchestrator' in f.path.lower() for f in files):
            patterns['architecture_patterns'].append('Orchestration Pattern')

        if any('bridge' in f.path.lower() for f in files):
            patterns['architecture_patterns'].append('Bridge Pattern')

        if any('factory' in f.path.lower() for f in files):
            patterns['architecture_patterns'].append('Factory Pattern')

        # Detect test patterns
        test_files = [f for f in files if f.type == 'test']
        if test_files:
            patterns['test_patterns'].append(f"{len(test_files)} test files found")
            if any('mock' in ' '.join(f.imports).lower() for f in test_files):
                patterns['test_patterns'].append('Mock-based testing')
            if any('pytest' in ' '.join(f.imports).lower() for f in test_files):
                patterns['test_patterns'].append('pytest framework')

        # Common exports (most frequently exported classes/functions)
        all_exports = []
        for file_metadata in files:
            all_exports.extend(file_metadata.exports)

        from collections import Counter
        common = Counter(all_exports).most_common(10)
        patterns['common_exports'] = [{'name': name, 'count': count} for name, count in common]

        return patterns

    def _build_structure(self, files: List[FileMetadata]) -> Dict[str, Any]:
        """
        Build directory structure with file counts.

        Returns:
            Nested dict representing directory structure
        """
        structure = {}

        for file_metadata in files:
            parts = Path(file_metadata.path).parts
            current = structure

            # Navigate/create directory structure
            for i, part in enumerate(parts[:-1]):  # Exclude filename
                if part not in current:
                    current[part] = {'_files': 0, '_subdirs': {}}
                current = current[part]['_subdirs']

            # Count file in parent directory
            parent = structure
            for part in parts[:-1]:
                parent = parent[part]['_subdirs']

            parent_dir = parts[-2] if len(parts) > 1 else '.'
            if parent_dir in structure:
                structure[parent_dir]['_files'] += 1

        return structure

    def save_index(self, project_index: ProjectIndex, output_path: Optional[Path] = None) -> Path:
        """
        Save project index to JSON file.

        Args:
            project_index: ProjectIndex to save
            output_path: Path to save JSON (default: .apc/project_index.json)

        Returns:
            Path where index was saved
        """
        if output_path is None:
            apc_dir = self.project_root / '.apc'
            apc_dir.mkdir(exist_ok=True)
            output_path = apc_dir / 'project_index.json'

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(project_index), f, indent=2)

        logger.info("project_index_saved", output_path=str(output_path))
        return output_path


def scan_and_save(
    project_root: str,
    output_path: Optional[str] = None,
    **kwargs
) -> Tuple[ProjectIndex, Path]:
    """
    Convenience function to scan project and save index.

    Args:
        project_root: Absolute path to project root
        output_path: Optional path to save index JSON
        **kwargs: Additional arguments for ProjectScanner

    Returns:
        Tuple of (ProjectIndex, Path where saved)
    """
    scanner = ProjectScanner(project_root, **kwargs)
    project_index = scanner.scan_project()

    output = Path(output_path) if output_path else None
    saved_path = scanner.save_index(project_index, output)

    return project_index, saved_path
