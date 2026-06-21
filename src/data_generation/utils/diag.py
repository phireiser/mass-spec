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
]
