"""
Diagnostics toggles and counters extracted from rule_extention.
E.g. is the saturated path cap being hit,
    how often is the BFS collection cap being hit
"""
import atexit

SUBGROUP_DIAG: bool = False
_diag_counters = {
    "collect_bfs_cap": 0,
    "saturated_path_cap": 0,
}

def enable_subgroup_diag(enabled: bool) -> None:
    global SUBGROUP_DIAG
    SUBGROUP_DIAG = bool(enabled)


# --------------------------------------------------------------------------- #
# Per-derivation memory instrumentation ("mem-diag").
#
# The forward-build 32G OOMs live in MØD's C++ per-derivation matching on a
# single pathological derivation, unreachable from the Python layer. To *localise*
# that derivation we sample the process peak-RSS high-water-mark (VmHWM from
# /proc/self/status -- it never decreases, so it captures a transient spike even
# between samples) once per derivation from the `sub_group` predicate, and write a
# row ONLY when VmHWM grows. Each growth row names the rule + reactant mass/charge
# + embedding fan-out that pushed the peak up, so scanning the log for the big
# jumps points straight at the exploding (rule, reactant). Gated by --mem-diag;
# off (and zero-overhead) otherwise.
MEM_DIAG: bool = False
_mem_file = None
_mem_i: int = 0
_mem_last_hwm: int = -1


def enable_mem_diag(path: str) -> None:
    """Enable per-derivation memory logging to ``path`` (CSV)."""
    global MEM_DIAG, _mem_file
    MEM_DIAG = True
    _mem_file = open(path, "w", buffering=1)  # line-buffered so a kill still leaves the log
    _mem_file.write("i,phase,vmhwm_kb,vmrss_kb,rule,reactant_mass,reactant_charge,n_matches\n")


def _read_hwm_rss() -> "tuple[int, int]":
    """(VmHWM, VmRSS) in kB from /proc/self/status; (-1,-1) if unavailable."""
    hwm = rss = -1
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    hwm = int(line.split()[1])
                elif line.startswith("VmRSS:"):
                    rss = int(line.split()[1])
                    break  # VmRSS follows VmHWM; stop once both are read
    except OSError:
        pass
    return hwm, rss


def mem_grown() -> "tuple[int, int, int] | None":
    """Sample the peak-RSS watermark once. Returns ``(i, vmhwm, vmrss)`` if the peak
    GREW since the last call (a growth event worth attributing), else ``None``.
    Cheap enough to call per derivation; returns ``None`` immediately when disabled.
    """
    global _mem_i, _mem_last_hwm
    if not MEM_DIAG:
        return None
    _mem_i += 1
    hwm, rss = _read_hwm_rss()
    if hwm > _mem_last_hwm:
        _mem_last_hwm = hwm
        return (_mem_i, hwm, rss)
    return None


def mem_write(sample, phase: str, rule: str, mass, charge, n_matches: int) -> None:
    """Write one growth-event row. ``sample`` is the tuple from :func:`mem_grown`."""
    if _mem_file is None or sample is None:
        return
    i, hwm, rss = sample
    rule = str(rule).replace(",", ";")
    _mem_file.write(f"{i},{phase},{hwm},{rss},{rule},{mass},{charge},{n_matches}\n")


def _diag_log(msg: str) -> None:
    if SUBGROUP_DIAG:
        print(msg)


def _diag_inc(key: str) -> None:
    if key in _diag_counters:
        _diag_counters[key] += 1


@atexit.register
def _diag_summary() -> None:
    if not SUBGROUP_DIAG:
        return
    total = sum(_diag_counters.values())
    if total == 0:
        return
    print(
        f"[subgroup-summary] caps hit: collect_bfs={_diag_counters['collect_bfs_cap']}, "
        f"saturated_path={_diag_counters['saturated_path_cap']}"
    )


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "enable_subgroup_diag",
    "enable_mem_diag",
    "mem_grown",
    "mem_write",
]
