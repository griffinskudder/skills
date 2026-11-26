"""Install Agent Skills from this checkout using only the standard library."""

import argparse
import shutil
from pathlib import Path


def install_skill(source: Path, destination: Path) -> None:
    # Reserve the destination before copying, so concurrent installs cannot merge.
    destination.mkdir()
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
    except (OSError, KeyboardInterrupt):
        shutil.rmtree(destination)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", metavar="SKILL", help="skill names to install")
    parser.add_argument(
        "--group", action="append", default=[], metavar="GROUP",
        help="include every skill in this group (repeatable)",
    )
    parser.add_argument(
        "--dir", type=Path, default=Path(".agents/skills"),
        help="destination skills directory (default: .agents/skills in the current directory)",
    )
    listing = parser.add_mutually_exclusive_group()
    listing.add_argument("--list", action="store_true", help="list skill names for the selection")
    listing.add_argument("--list-groups", action="store_true", help="list the available groups")
    args = parser.parse_args()

    groups_dir = Path(__file__).resolve().parent / "groups"
    available = {}
    groups = {}
    for path in sorted(groups_dir.glob("*/skills/*/SKILL.md")):
        if not path.is_file():
            continue
        name = path.parent.name
        group = path.parents[2].name
        if name in available:
            parser.error(f"duplicate skill name {name!r} in {available[name]} and {path.parent}")
        available[name] = path.parent
        groups.setdefault(group, []).append(name)

    if args.list_groups:
        for group in groups:
            print(group)
        return
    if not available:
        parser.error(f"no skills found in {groups_dir}")

    selected = list(args.skills)
    for name in selected:
        if name not in available:
            parser.error(f"unknown skill {name!r}. Use --list to see available skills.")
    for group in args.group:
        if group not in groups:
            parser.error(f"unknown group {group!r}. Use --list-groups to see available groups.")
        selected.extend(groups[group])

    names = list(dict.fromkeys(selected or available))
    if args.list:
        print(*names, sep="\n")
        return

    destination = args.dir.expanduser().resolve()
    for name in names:
        path = destination / name
        if available[name].resolve() in (path, *path.parents):
            parser.error(f"cannot install a skill into its source directory: {path}")
        if path.exists() or path.is_symlink():
            parser.error(f"destination already exists: {path}")

    try:
        destination.mkdir(parents=True, exist_ok=True)
        for name in names:
            path = destination / name
            install_skill(available[name], path)
            print(f"Installed {name} to {path}")
    except OSError as error:
        parser.exit(1, f"Installation failed: {error}\n")


if __name__ == "__main__":
    main()
