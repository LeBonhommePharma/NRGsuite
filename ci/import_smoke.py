"""Import every NRGsuite module under a real PyMOL, the way the plugin loads.

PyMOL is not stubbed. Install conda-forge ``pymol-open-source`` and run:

    python ci/import_smoke.py

The script launches PyMOL headless (``-cq``) when it is not already running,
points ``NRGSUITE_INSTALLATION`` at the repository root, executes
``Plugin/NRGsuite.py``, then imports every other plugin module by the bare
name PyMOL puts on ``sys.path``.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Directories Plugin/NRGsuite.py adds to sys.path. Module names are unique
# across these directories; a new collision should fail this check.
MODULE_DIRS = (
    ROOT,
    ROOT / "Plugin",
    ROOT / "Project",
    ROOT / "FlexAID",
    ROOT / "GetCleft",
    ROOT / "About",
)


def plugin_modules():
    found = {}
    for directory in MODULE_DIRS:
        for path in sorted(directory.glob("*.py")):
            name = path.stem
            if name in found:
                raise RuntimeError(
                    "duplicate plugin module name %s (%s and %s)"
                    % (name, found[name], path)
                )
            found[name] = path.resolve()
    covered = set(found.values())
    extras = []
    for path in ROOT.rglob("*.py"):
        resolved = path.resolve()
        if resolved in covered:
            continue
        if any(part in path.parts for part in (".git", ".github", "ci")):
            continue
        extras.append(resolved)
    if extras:
        raise RuntimeError(
            "Python files are not covered by the import smoke test: "
            + ", ".join(str(path.relative_to(ROOT)) for path in extras)
        )
    return found


def ensure_pymol():
    """Start headless PyMOL in this process. Fail if it is not installed."""
    os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        import pymol
    except ImportError as exc:
        raise RuntimeError(
            "PyMOL is not installed. CI installs conda-forge pymol-open-source; "
            "this smoke test does not stub it."
        ) from exc

    from pymol import cmd

    try:
        version = cmd.get_version()
    except Exception:
        version = None
    if not version:
        pymol.pymol_argv = ["pymol", "-cq"]
        pymol.finish_launching()
        version = cmd.get_version()
    if not version or not str(version[0])[:1].isdigit():
        raise RuntimeError("unexpected cmd.get_version() result: %r" % (version,))
    # Same indexing the plugin performs at import: int(cmd.get_version()[0][0]).
    int(str(version[0])[0])
    return version


def disarm_error_dialogs():
    """Turn the plugin's install-time error popups into exceptions.

    The success path never calls showerror. A missing install directory would
    otherwise open a modal dialog and hang a headless runner.
    """
    import tkinter.messagebox as messagebox

    def showerror(title, message, *args, **kwargs):
        raise RuntimeError("plugin error dialog: %s: %s" % (title, message))

    messagebox.showerror = showerror


def load_plugin():
    os.environ["NRGSUITE_INSTALLATION"] = str(ROOT)
    plugin_file = ROOT / "Plugin" / "NRGsuite.py"
    spec = importlib.util.spec_from_file_location("NRGsuite", plugin_file)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load %s" % plugin_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules["NRGsuite"] = module
    spec.loader.exec_module(module)
    return module


def import_all(modules):
    failures = []
    for name in sorted(modules):
        expected = modules[name]
        try:
            module = importlib.import_module(name)
        except Exception:
            failures.append((name, expected, traceback.format_exc()))
            continue
        actual = getattr(module, "__file__", None)
        if actual is None:
            failures.append(
                (
                    name,
                    expected,
                    "imported %s with no __file__ (namespace package?)" % name,
                )
            )
            continue
        if Path(actual).resolve() != expected:
            failures.append(
                (
                    name,
                    expected,
                    "imported %s from %s, expected %s" % (name, actual, expected),
                )
            )
            continue
        print("ok %s" % expected.relative_to(ROOT))
    return failures


def main():
    modules = plugin_modules()
    version = ensure_pymol()
    print("PyMOL %s" % (version[0],))
    disarm_error_dialogs()
    try:
        load_plugin()
    except Exception:
        traceback.print_exc()
        return 1
    failures = import_all(modules)
    if failures:
        for name, expected, detail in failures:
            print(
                "FAIL %s (%s)\n%s" % (name, expected.relative_to(ROOT), detail),
                file=sys.stderr,
            )
        print("%d module import(s) failed" % len(failures), file=sys.stderr)
        return 1
    print("imported %d modules" % len(modules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
