"""Test fresh dependency checkouts, ignoring any sibling repositories."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


APP = Path(__file__).resolve().parents[1]
PACKAGES = ("sqlerrors", "sqlscope", "sqlchecker", "sqlexercise")


def main() -> int:
    try:
        with TemporaryDirectory(prefix="lensql-dependency-tests-") as directory:
            suites = [Path(directory) / name for name in PACKAGES]
            for path in suites:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--recurse-submodules",
                     f"https://github.com/DavidePonzini/{path.name}.git", str(path)],
                    check=True,
                )

            # Install regular distributions so removing the checkouts is safe.
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade",
                 "-r", str(APP / "requirements-test.txt"),
                 *(str(path) for path in suites)],
                check=True,
            )

            failed = []
            for path in suites:
                print(f"\n=== {path.name} ===", flush=True)
                if not (path / "tests").is_dir():
                    print(f"Missing test suite: {path}", file=sys.stderr)
                    failed.append(path.name)
                    continue
                # Separate processes and working directories preserve fixture paths.
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests", *sys.argv[1:]], cwd=path,
                )
                if result.returncode:
                    failed.append(path.name)

            if failed:
                print("\nFailed suites: " + ", ".join(failed), file=sys.stderr)
                return 1
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Dependency tests failed: {error}", file=sys.stderr)
        return 1
    print("\nAll LensQL dependency suites passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
