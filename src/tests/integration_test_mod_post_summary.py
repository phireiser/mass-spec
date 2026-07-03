"""
Integration test: run the MØD post-processing pipeline end-to-end and check
that `mod_post` compiles a summary PDF.

This mirrors what src/data_generation/analyze.py does (print graphs/rules into
out/, flush the post commands, then invoke `mod_post`), but in a temporary
working directory so it does not touch outputs/mod_post. The MØD post-command
stream is process-global and rooted in the current working directory, so the
printing step runs in a subprocess with cwd set to the temp dir instead of
chdir-ing this test process.

Requires the container environment (mod, mod_post, LaTeX), so like the other
integration tests it is skipped unless explicitly enabled. Run it via
run/ci_cd/integration_test.sh.
"""

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

# Prints toluene and the ionization rules into out/, enables summary
# compilation, and flushes the commands mod_post will consume.
GENERATE_POST_COMMANDS = textwrap.dedent("""
    import mod
    from mod import post

    from src.data_generation import utils
    from src.data_generation.rules import ionization

    molecule = mod.Graph.fromSMILES("CC1=CC=CC=C1", "toluene")
    utils.print_grammar([molecule], ionization)

    post.enableCompileSummary()
    post.flushCommands()
""")


@unittest.skipUnless(
    os.environ.get("RUN_MOD_INTEGRATION_TESTS") == "1",
    "runs the real MOD engine; enable with RUN_MOD_INTEGRATION_TESTS=1 (see run/ci_cd/integration_test.sh)",
)
class TestModPostSummary(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory(prefix="mod_post_test_")
        cls.addClassCleanup(tmp.cleanup)
        cls.workdir = Path(tmp.name)

        # mod does not create out/ itself (see run/analysis/generated_fwd_dg.sh)
        (cls.workdir / "out").mkdir()

        cls._run([sys.executable, "-c", GENERATE_POST_COMMANDS], "post-command generation")
        cls._run(["mod_post"], "mod_post")

        cls.summary_pdf = cls.workdir / "summary" / "summary.pdf"

    @classmethod
    def _run(cls, cmd, label):
        result = subprocess.run(
            cmd, cwd=cls.workdir, capture_output=True, text=True, timeout=600
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"{label} failed with exit code {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )

    def test_post_commands_were_generated(self):
        out_files = list((self.workdir / "out").iterdir())
        self.assertTrue(out_files, "printing produced no files in out/")

    def test_summary_pdf_exists(self):
        self.assertTrue(
            self.summary_pdf.is_file(),
            f"mod_post did not produce {self.summary_pdf}",
        )

    def test_summary_pdf_is_valid_pdf(self):
        header = self.summary_pdf.read_bytes()[:5]
        self.assertEqual(header, b"%PDF-", f"summary.pdf has non-PDF header: {header!r}")

    def test_summary_pdf_is_not_empty(self):
        self.assertGreater(
            self.summary_pdf.stat().st_size, 1024,
            "summary.pdf is suspiciously small; LaTeX compilation likely failed",
        )


if __name__ == "__main__":
    unittest.main()
