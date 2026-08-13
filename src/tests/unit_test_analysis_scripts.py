"""Contract every analysis/plot CLI script must satisfy.

These scripts are run by hand, weeks apart, from run/*.sh -- so a broken import or
a default that only resolves from one directory stays invisible until someone
needs the number. Three real bugs of exactly that shape were shipped:

* ``plot/weighted_regression_analysis.py`` walked one directory up instead of
  three and raised FileNotFoundError on import;
* ``plot/eval_from_metrics_csv.py`` defaulted to ``../../data/outputs/...``,
  correct only when invoked from inside ``src/plot``;
* ``analyze.py`` asked for a dump by human name after the corpus was renamed to CAS.

The scripts are discovered, not listed, so a new one is covered the day it lands.
"""

import ast
import subprocess
import sys
import unittest
from pathlib import Path

from src.project_paths import REPO_ROOT, _load_relative_paths

SCRIPT_ROOTS = ("src/data_generation/analysis", "src/plot")
EXTRA_SCRIPTS = ("src/data_generation/analyze.py",)

# --help must not need these to exist; anything else is a genuine failure.
HELP_TIMEOUT_S = 120


def analysis_modules():
    """Every analysis/plot module, script or library."""
    found = []
    for root in SCRIPT_ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("*.py")):
            if "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            found.append(path)
    found.extend(REPO_ROOT / extra for extra in EXTRA_SCRIPTS
                 if (REPO_ROOT / extra).exists())
    return found


def discover_scripts():
    """The subset that builds an argparse parser, i.e. has a CLI to exercise.

    Not every analysis script has one: several ``src/plot`` modules do all their
    work at module level, which is why they need the static checks below rather
    than a --help probe.
    """
    return [p for p in analysis_modules()
            if "argparse.ArgumentParser(" in p.read_text(encoding="utf-8")]


class TestAnalysisScriptsAreDiscoverable(unittest.TestCase):
    def test_discovery_finds_every_family(self):
        """Both families are covered: argparse CLIs and module-level scripts."""
        names = {p.name for p in analysis_modules()}
        for expected in ("run_ceiling.py", "discriminate.py", "score_forward.py",
                         "cost_model.py", "analyze.py", "plot_ceiling.py",
                         "eval_from_metrics_csv.py", "weighted_regression_analysis.py",
                         "analyze_data_distribution.py", "plot_time_complexity.py"):
            with self.subTest(module=expected):
                self.assertIn(expected, names)

    def test_the_cli_subset_is_not_empty_or_everything(self):
        cli = {p.name for p in discover_scripts()}
        self.assertIn("run_ceiling.py", cli)
        # weighted_regression_analysis has no CLI; it must not be --help-probed.
        self.assertNotIn("weighted_regression_analysis.py", cli)


class TestNoModuleDerivesItsOwnRepoRoot(unittest.TestCase):
    """Repo root comes from project_paths, never from counting parent directories.

    ``weighted_regression_analysis.py`` used ``parents[0]`` where its siblings used
    ``parents[2]``, so ``CSV_PATH`` pointed at a file that has never existed and the
    module raised FileNotFoundError the moment anyone imported it. Counting parents
    is only ever right by coincidence, and silently wrong the moment a file moves.
    """

    def test_no_analysis_module_walks_parents_of_dunder_file(self):
        offenders = []
        for path in analysis_modules():
            rel = path.relative_to(REPO_ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                # Path(__file__).resolve().parent[s[N]]
                if (isinstance(node, ast.Name) and node.id == "__file__"):
                    offenders.append(f"{rel}:{node.lineno}: derives a root from __file__ "
                                     f"-- import REPO_ROOT/shared_path from project_paths")
        self.assertEqual([], offenders,
                         "hand-rolled repo roots:\n" + "\n".join(offenders))


class TestAnalysisScriptsRun(unittest.TestCase):
    """Each script must at least start: imports resolve and the parser builds."""

    def test_every_script_answers_help(self):
        failures = []
        for path in discover_scripts():
            rel = path.relative_to(REPO_ROOT).as_posix()
            proc = subprocess.run(
                [sys.executable, str(path), "--help"],
                cwd=str(REPO_ROOT), capture_output=True, text=True,
                timeout=HELP_TIMEOUT_S,
                env={"PYTHONPATH": str(REPO_ROOT), "PATH": "/usr/bin:/bin",
                     "MPLBACKEND": "Agg", "HOME": "/tmp"},
            )
            if proc.returncode != 0:
                tail = (proc.stderr or proc.stdout).strip().splitlines()
                failures.append(f"{rel}: exit {proc.returncode}: {tail[-1] if tail else '?'}")
        self.assertEqual([], failures, "scripts that cannot start:\n" + "\n".join(failures))

    def test_no_script_runs_work_at_import_time(self):
        """--help must be reachable, i.e. argparse comes before the heavy lifting.

        ``weighted_regression_analysis`` used to read a CSV at import; a script that
        computes before parsing cannot be introspected, and fails in odd places.
        """
        offenders = []
        for path in discover_scripts():
            rel = path.relative_to(REPO_ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            parser_line = next(
                (node.lineno for node in ast.walk(tree)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)
                 and node.func.attr == "ArgumentParser"),
                None,
            )
            if parser_line is None:
                continue
            for node in tree.body:
                # Module-level `open(...)` / `read_csv(...)` before the parser exists.
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                                     ast.AsyncFunctionDef, ast.ClassDef, ast.Assign,
                                     ast.AnnAssign, ast.Expr, ast.If)):
                    continue
                if node.lineno < parser_line:
                    offenders.append(f"{rel}:{node.lineno}")
        self.assertEqual([], offenders,
                         "work executed before the parser is built:\n" + "\n".join(offenders))


class TestAnalysisScriptPathDefaults(unittest.TestCase):
    """Path defaults must be repo-anchored, not relative to the caller's cwd."""

    def _path_like_string_defaults(self, path: Path):
        """(lineno, flag, literal) for every add_argument(default="...path...")."""
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add_argument"):
                continue
            flag = next((a.value for a in node.args
                         if isinstance(a, ast.Constant) and isinstance(a.value, str)), "?")
            for kw in node.keywords:
                if kw.arg != "default":
                    continue
                # Only bare string literals are a problem; shared_path(...) is a Call.
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    yield node.lineno, flag, kw.value.value
                # Path("literal") is equally cwd-relative.
                elif (isinstance(kw.value, ast.Call)
                      and getattr(kw.value.func, "id", None) == "Path"
                      and kw.value.args
                      and isinstance(kw.value.args[0], ast.Constant)
                      and isinstance(kw.value.args[0].value, str)):
                    yield node.lineno, flag, kw.value.args[0].value

    def test_no_cwd_relative_path_defaults(self):
        offenders = []
        for path in analysis_modules():
            rel = path.relative_to(REPO_ROOT).as_posix()
            for lineno, flag, literal in self._path_like_string_defaults(path):
                if not literal or literal.startswith("/"):
                    continue
                looks_like_path = "/" in literal or literal.endswith(
                    (".csv", ".json", ".txt", ".parquet", ".yaml", ".pt"))
                if looks_like_path:
                    offenders.append(
                        f"{rel}:{lineno}: {flag} default {literal!r} is cwd-relative "
                        f"-- use shared_path(...)")
        self.assertEqual([], offenders,
                         "cwd-relative path defaults:\n" + "\n".join(offenders))

    def test_scripts_resolve_paths_through_paths_env(self):
        """Any script with a path default must source it from project_paths."""
        configured = {v for k, v in _load_relative_paths().items()
                      if k not in {"SRC_DIR_REL", "RUN_DIR_REL", "DATA_DIR_REL", "C_APP"}}
        offenders = []
        for path in analysis_modules():
            rel = path.relative_to(REPO_ROOT).as_posix()
            source = path.read_text(encoding="utf-8")
            uses_paths_env = "project_paths" in source
            has_path_default = any(
                "/" in literal for _l, _f, literal in self._path_like_string_defaults(path))
            if has_path_default and not uses_paths_env:
                offenders.append(f"{rel}: has a path default but never imports project_paths")
            # And no script may spell a configured value out by hand.
            tree = ast.parse(source, filename=str(path))
            prose = {n.value for n in ast.walk(tree)
                     if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                     and isinstance(n.value.value, str)}
            for node in ast.walk(tree):
                if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                        and node not in prose):
                    for value in configured:
                        if value in node.value:
                            offenders.append(
                                f"{rel}:{node.lineno}: hardcodes {value!r}")
                            break
        self.assertEqual([], offenders, "path handling:\n" + "\n".join(offenders))


class TestDumpReadersUseCasResolution(unittest.TestCase):
    """Scripts that load a dump must resolve the stem, never assume the name."""

    def test_no_script_loads_a_dump_by_raw_name(self):
        offenders = []
        for path in analysis_modules() + [REPO_ROOT / "src/machine_learning/main.py"]:
            rel = path.relative_to(REPO_ROOT).as_posix()
            source = path.read_text(encoding="utf-8")
            if "load_derivation_graph" not in source and "dump_is_complete" not in source:
                continue
            resolves = any(token in source for token in
                           ("resolve_dump_stem", "dump_stem_candidates", "cas_all"))
            if not resolves:
                offenders.append(f"{rel}: reads dumps without CAS-first resolution")
        self.assertEqual([], offenders,
                         "dump readers still keyed on the human name:\n" + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
