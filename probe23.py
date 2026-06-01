"""Probe: classify every sdk CLI under cp1252 — CRASH (traceback) vs NEEDS-ARGS vs OK."""
import os, shutil, subprocess, sys
from pathlib import Path

ARCH = Path(r"C:\Users\thail\Arquitetura Cognitiva\cognitive-arch")
GEN  = Path(r"C:\Users\thail\Arquitetura Cognitiva\cognitive-arch-generic")
FIX  = Path(r"C:\Users\thail\Arquitetura Cognitiva\_fix23")

if FIX.exists():
    shutil.rmtree(FIX)
shutil.copytree(GEN, FIX)

env = dict(os.environ)
env["PYTHONIOENCODING"] = "cp1252"  # reproduce Windows console worst-case

SKIP = {"__init__.py", "conftest.py"}
tools = sorted(p for p in (ARCH / "sdk").glob("*.py")
               if p.name not in SKIP and not p.name.endswith("_schema.py"))

def run(tool, args):
    r = subprocess.run([sys.executable, str(tool)] + args,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=60, cwd=str(ARCH))
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out

crash_help, crash_run, needs_args, ok = [], [], [], []
print(f"Probing {len(tools)} tools (cp1252)\n")
for t in tools:
    # 1) --help should ALWAYS exit 0 with no traceback
    rc_h, out_h = run(t, ["--help"])
    if "Traceback" in out_h:
        err = [l for l in out_h.splitlines() if "Error" in l]
        crash_help.append((t.name, err[-1].strip()[:70] if err else "?"))
        print(f"  CRASH-on-help  {t.name:30} {(err[-1].strip()[:55]) if err else ''}")
        continue
    # 2) run against fixture
    rc_r, out_r = run(t, ["--arch-root", str(FIX)])
    if "Traceback" in out_r:
        err = [l for l in out_r.splitlines() if "Error" in l]
        crash_run.append((t.name, err[-1].strip()[:70] if err else "?"))
        print(f"  CRASH-on-run   {t.name:30} {(err[-1].strip()[:55]) if err else ''}")
    elif rc_r == 2:  # argparse usage error = needs subcommand/args
        needs_args.append(t.name)
    else:
        ok.append(t.name)

print(f"\n{'='*64}")
print(f"  CRASH on --help : {len(crash_help)}  -> {[n for n,_ in crash_help]}")
print(f"  CRASH on run    : {len(crash_run)}  -> {[n for n,_ in crash_run]}")
print(f"  needs-args (ok) : {len(needs_args)}")
print(f"  clean run       : {len(ok)}")
print(f"{'='*64}")
shutil.rmtree(FIX)
