"""Guardrail for src/paths.env being the single source of truth for paths.

Rather than re-spelling the configured values (which only moves the duplication
into the test), this asserts the *invariants* the rest of the repo relies on, and
scans src/ and run/ for literals that duplicate a configured value.
"""

import ast
import re
import unittest
from pathlib import Path

from src.project_paths import (
    PATHS_FILE,
    REPO_ROOT,
    _load_relative_paths,
    repo_path,
    shared_name,
    shared_path,
)

# Files that are allowed to spell a configured path out literally, with the reason.
LITERAL_ALLOWLIST = {
    # Bootstrap: this is the file that locates the file defining SRC_DIR_REL.
    "src/project_paths.py",
    # This file quotes key values in order to assert on them.
    "src/tests/unit_test_project_paths.py",
    # Workflow scripts run without filesystem access and cannot parse paths.env;
    # test_mjs_mirror_matches_paths_env below asserts its copy stays in sync.
    "src/mechanisms/extract_pages.mjs",
}

# Keys whose values are too generic to scan for without drowning in false
# positives ("src", "run", "data" appear in prose, module paths and URLs).
UNSCANNABLE_KEYS = {"SRC_DIR_REL", "RUN_DIR_REL", "DATA_DIR_REL", "C_APP", "SIF_REL"}

SBATCH_RE = re.compile(r"^#SBATCH\s+--(?:output|error)=(\S+)")


def _scan_targets():
    for pattern in ("src/**/*.py", "src/**/*.mjs", "run/**/*.sh"):
        for path in sorted(REPO_ROOT.glob(pattern)):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in LITERAL_ALLOWLIST:
                continue
            yield path, rel


class TestPathsEnvIsWellFormed(unittest.TestCase):
    def test_every_key_resolves_and_is_fully_expanded(self):
        paths = _load_relative_paths()
        self.assertTrue(paths, "paths.env parsed as empty")
        for key, value in paths.items():
            with self.subTest(key=key):
                self.assertTrue(value, f"{key} is empty")
                self.assertNotIn("${", value, f"{key} has an unexpanded reference")

    def test_interpolation_composes_parents(self):
        self.assertEqual(shared_path("LOGS_DIR_REL"), shared_path("OUTPUTS_DIR_REL") / "logs")
        self.assertEqual(shared_path("FWD_DIR_REL"), shared_path("PROCESSED_DIR_REL") / "fwd")
        self.assertEqual(shared_path("DATA_DIR_REL").parent, REPO_ROOT)

    def test_relative_keys_stay_inside_the_repo(self):
        for key, value in _load_relative_paths().items():
            if key.startswith("C_"):
                continue
            with self.subTest(key=key):
                self.assertFalse(Path(value).is_absolute(), f"{key} must be repo-relative")
                self.assertEqual(shared_path(key), repo_path(value))

    def test_container_keys_mirror_their_host_counterpart(self):
        """Every --bind in run/ assumes C_X == /app + <host value>."""
        paths = _load_relative_paths()
        c_app = paths["C_APP"]
        mirrored = 0
        for key, value in paths.items():
            if not key.startswith("C_") or key == "C_APP":
                continue
            with self.subTest(key=key):
                self.assertTrue(value.startswith(c_app + "/"), f"{key} is not under {c_app}")
                host_value = value[len(c_app) + 1:]
                self.assertIn(
                    host_value,
                    set(paths.values()),
                    f"{key}={value} mirrors {host_value!r}, which is no host key's value",
                )
                mirrored += 1
        self.assertGreater(mirrored, 5, "container mirror looks unpopulated")

    def test_shared_name_returns_the_leaf(self):
        self.assertEqual(shared_name("FWD_DIR_REL"), "fwd")
        self.assertEqual(shared_name("BWD_DIR_REL"), "bwd")
        self.assertEqual(shared_name("CSV_PATH_REL"), "compounds.csv")

    def test_unknown_key_raises_a_helpful_error(self):
        with self.assertRaises(KeyError) as ctx:
            shared_path("NO_SUCH_KEY_REL")
        message = str(ctx.exception)
        self.assertIn("NO_SUCH_KEY_REL", message)
        self.assertIn("PROCESSED_DIR_REL", message, "error should list the valid keys")


class TestNoHardcodedPaths(unittest.TestCase):
    """Fail on literals in src/ and run/ that duplicate a paths.env value."""

    def _configured_values(self):
        paths = _load_relative_paths()
        return sorted(
            ((k, v) for k, v in paths.items() if k not in UNSCANNABLE_KEYS),
            key=lambda kv: -len(kv[1]),
        )

    def test_python_string_literals(self):
        values = self._configured_values()
        offenders = []
        for path, rel in _scan_targets():
            if path.suffix != ".py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            # Any string used as a bare expression statement is prose, not a value:
            # docstrings, and also the module blurbs that sit after `from __future__
            # import ...` (which Python does not treat as __doc__ at all).
            docstrings = {
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            }
            for node in ast.walk(tree):
                if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                    continue
                if node in docstrings:
                    continue
                for key, value in values:
                    if value in node.value:
                        offenders.append(f"{rel}:{node.lineno}: {value!r} -> use shared_path({key!r})")
                        break
        self.assertEqual([], offenders, "hardcoded paths found:\n" + "\n".join(offenders))

    def test_shell_code_lines(self):
        values = self._configured_values()
        offenders = []
        for path, rel in _scan_targets():
            if path.suffix != ".sh":
                continue
            for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                line = raw.strip()
                # `#SBATCH --output=` is checked separately: SLURM parses it before
                # the shell runs, so it cannot interpolate a variable.
                if line.startswith("#"):
                    continue
                # The bootstrap `source .../src/paths.env` cannot use a key either.
                if "paths.env" in line:
                    continue
                for key, value in values:
                    if value in line:
                        offenders.append(f"{rel}:{lineno}: {value!r} -> use ${key}")
                        break
        self.assertEqual([], offenders, "hardcoded paths found:\n" + "\n".join(offenders))

    def test_sbatch_directives_match_their_key(self):
        """The unavoidable #SBATCH literal must agree with the configured log dir."""
        expected = {
            "run/hpc/data_gen.sh": _load_relative_paths()["DATAGEN_LOG_DIR_REL"],
            "run/hpc/ml_train.sh": _load_relative_paths()["TRAIN_LOG_DIR_REL"],
            "run/hpc/ml_optimize.sh": _load_relative_paths()["OPTIM_LOG_DIR_REL"],
        }
        for rel, log_dir in expected.items():
            directives = [
                m.group(1)
                for line in (REPO_ROOT / rel).read_text(encoding="utf-8").splitlines()
                if (m := SBATCH_RE.match(line.strip()))
            ]
            with self.subTest(script=rel):
                self.assertTrue(directives, f"{rel} has no #SBATCH --output/--error")
                for target in directives:
                    self.assertTrue(
                        target.startswith(log_dir + "/"),
                        f"{rel}: #SBATCH target {target!r} is not under {log_dir!r}",
                    )

    def test_mjs_mirror_matches_paths_env(self):
        """extract_pages.mjs cannot read paths.env, so verify its copy agrees."""
        source = (REPO_ROOT / "src/mechanisms/extract_pages.mjs").read_text(encoding="utf-8")
        paths = _load_relative_paths()
        found = dict(re.findall(r"^const ([A-Z0-9_]+_REL) = '([^']+)'$", source, re.M))
        self.assertTrue(found, "no mirrored *_REL constants found in extract_pages.mjs")
        for key, value in found.items():
            with self.subTest(key=key):
                self.assertIn(key, paths, f"{key} is mirrored but not defined in paths.env")
                self.assertEqual(paths[key], value, f"{key} has drifted from paths.env")

    def test_every_key_is_used_somewhere(self):
        """Dead keys surface instead of accumulating.

        A key counts as used if code references it, or if another key derives from
        it (e.g. TESTS_DIR_REL exists to build C_TESTS).
        """
        sources = [
            path
            for path in list(REPO_ROOT.glob("src/**/*.py"))
            + list(REPO_ROOT.glob("src/**/*.mjs"))
            + list(REPO_ROOT.glob("run/**/*.sh"))
            if "__pycache__" not in path.parts
        ]
        blob = "\n".join(p.read_text(encoding="utf-8") for p in sources)
        derived_from = set(
            re.findall(r"\$\{([A-Z0-9_]+)\}", PATHS_FILE.read_text(encoding="utf-8"))
        )
        unused = [
            key
            for key in _load_relative_paths()
            if key not in blob and key not in derived_from
        ]
        self.assertEqual([], unused, f"keys defined in {PATHS_FILE} but never used: {unused}")


if __name__ == "__main__":
    unittest.main()
