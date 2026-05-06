from __future__ import annotations

import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_PROJECT_DIR = REPO_ROOT / "local_uav_bev_project"

_DATASET_DIR_CANDIDATES = (
    REPO_ROOT / "UAV_benchmark_M",
    REPO_ROOT / "UAV-benchmark-M",
    REPO_ROOT.parent / "UAV_benchmark_M",
    REPO_ROOT.parent / "UAV-benchmark-M",
    DEFAULT_PROJECT_DIR / "raw" / "UAV_benchmark_M",
    DEFAULT_PROJECT_DIR / "raw" / "UAV-benchmark-M",
)

_GT_CANDIDATES = (
    ("GT",),
    ("annotations",),
    ("raw", "UAV-benchmark-MOTD_v1.0", "GT"),
    ("raw", "UAV_benchmark_MOTD_v1.0", "GT"),
)


def _first_existing(paths: list[Path] | tuple[Path, ...]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def resolve_project_dir(project_dir: str | os.PathLike[str] | None = None) -> Path:
    raw_value = project_dir or os.environ.get("DRONE3D_PROJECT_DIR")
    root = Path(raw_value).expanduser() if raw_value else DEFAULT_PROJECT_DIR
    root.mkdir(parents=True, exist_ok=True)
    for name in ("raw", "work", "indexes", "GT", "annotations"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root.resolve()


def find_uavdt_root(
    project_dir: str | os.PathLike[str] | None = None,
    dataset_dir: str | os.PathLike[str] | None = None,
) -> Path | None:
    explicit = dataset_dir or os.environ.get("UAVDT_DATASET_DIR") or os.environ.get("DRONE3D_UAVDT_DIR")
    if explicit:
        path = Path(explicit).expanduser()
        return path.resolve() if path.exists() else path

    project = resolve_project_dir(project_dir)
    candidates = list(_DATASET_DIR_CANDIDATES) + [
        project.parent / "UAV_benchmark_M",
        project.parent / "UAV-benchmark-M",
        project / "raw" / "UAV_benchmark_M",
        project / "raw" / "UAV-benchmark-M",
    ]
    found = _first_existing(candidates)
    return found.resolve() if found else None


def find_sequence_dir(
    sequence_name: str = "M1401",
    project_dir: str | os.PathLike[str] | None = None,
    dataset_dir: str | os.PathLike[str] | None = None,
) -> Path:
    root = find_uavdt_root(project_dir=project_dir, dataset_dir=dataset_dir)
    if root is None:
        project = resolve_project_dir(project_dir)
        return project / "raw" / "UAV_benchmark_M" / sequence_name
    return root / sequence_name


def default_gt_path(
    filename: str = "M1401_gt_whole.txt",
    project_dir: str | os.PathLike[str] | None = None,
) -> Path:
    project = resolve_project_dir(project_dir)
    candidates = [project.joinpath(*parts, filename) for parts in _GT_CANDIDATES]
    found = _first_existing(candidates)
    return found.resolve() if found else (project / "GT" / filename)


def print_local_setup(project_dir: Path, dataset_dir: Path | None = None) -> None:
    print("PROJECT_DIR:", project_dir)
    print("DATASET_DIR:", dataset_dir if dataset_dir is not None else "not found")
    print("Set DRONE3D_PROJECT_DIR and UAVDT_DATASET_DIR to override these defaults.")
