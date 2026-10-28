#!/usr/bin/env python3
"""Ingestão em volume com checkpoint/resume durável (issue #69).

Uso típico::

    PYTHONPATH=. python scripts/stress_ingest.py \\
        --corpus data/corpus --data data/stress-run/data \\
        --checkpoint data/stress-run/checkpoint.json \\
        --models models --porta 4395

Retoma automaticamente ficheiros já OK no checkpoint após kill/crash.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError as exc:  # pragma: no cover
    raise SystemExit("httpx é necessário: pip install httpx") from exc

SUPPORTED = {".txt", ".md", ".markdown", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def load_checkpoint(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "started_at": utc_now(),
        "done": {},
        "crashes": [],
        "restarts": 0,
        "server_pid": None,
    }


def save_checkpoint(path: Path, cp: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(cp, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def collect_files(corpus: Path, *, max_files: int, max_bytes: int) -> list[Path]:
    files: list[Path] = []
    for p in sorted(corpus.rglob("*")):
        if not p.is_file() or p.name == "SOURCES.md":
            continue
        if p.suffix.lower() not in SUPPORTED:
            continue
        if p.stat().st_size > max_bytes:
            continue
        files.append(p)
        if len(files) >= max_files:
            break
    return files


def kill_pg(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=12)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def start_server(
    *,
    root: Path,
    data: Path,
    models: Path,
    porta: int,
    python: Path,
    log_path: Path,
) -> subprocess.Popen:
    data.mkdir(parents=True, exist_ok=True)
    (data / "biblioteca").mkdir(exist_ok=True)
    (data / "miniaturas").mkdir(exist_ok=True)
    log = log_path.open("a", encoding="utf-8")
    log.write(f"\n===== start {utc_now()} =====\n")
    log.flush()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    env["PYTHONUNBUFFERED"] = "1"
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("OMP_NUM_THREADS", "1")
    proc = subprocess.Popen(
        [
            str(python),
            "-m",
            "engine.cli",
            "--porta",
            str(porta),
            "--raiz",
            str(root),
            "--data",
            str(data),
            "--models",
            str(models),
        ],
        cwd=str(root),
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    base = f"http://127.0.0.1:{porta}"
    deadline = time.time() + 180
    last = ""
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"servidor saiu cedo code={proc.returncode}")
        try:
            if httpx.get(f"{base}/health", timeout=2.0).status_code == 200:
                return proc
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
        time.sleep(0.4)
    raise RuntimeError(f"servidor sem health: {last}")


def ensure_alive(
    proc: subprocess.Popen | None,
    cp: dict,
    *,
    start_kwargs: dict,
    checkpoint: Path,
    max_restarts: int,
    base: str,
) -> subprocess.Popen:
    if proc is not None and proc.poll() is None:
        try:
            if httpx.get(f"{base}/health", timeout=2.0).status_code == 200:
                return proc
        except Exception:
            pass
    cp["crashes"].append({"at": utc_now()})
    cp["restarts"] = int(cp.get("restarts") or 0) + 1
    save_checkpoint(checkpoint, cp)
    print(f"!!! servidor em baixo — restart #{cp['restarts']}", flush=True)
    kill_pg(proc)
    if cp["restarts"] > max_restarts:
        raise RuntimeError(f"demasiados restarts ({max_restarts})")
    time.sleep(1.5)
    return start_server(**start_kwargs)


def ingest_one(
    client: httpx.Client, base: str, corpus: Path, path: Path, timeout: float
) -> dict:
    rel = str(path.relative_to(corpus))
    ext = path.suffix.lower()
    t0 = time.perf_counter()
    try:
        with path.open("rb") as fh:
            r = client.post(
                f"{base}/library/ingest",
                files={"ficheiro": (path.name, fh, "application/octet-stream")},
                timeout=timeout,
            )
        try:
            body: dict | str = r.json()
        except Exception:
            body = r.text[:400]
        return {
            "ok": r.status_code in {200, 202},
            "status": r.status_code,
            "ext": ext,
            "seconds": time.perf_counter() - t0,
            "path": rel,
            "error": None if r.status_code in {200, 202} else body,
            "at": utc_now(),
        }
    except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as exc:
        return {
            "ok": False,
            "status": 0,
            "ext": ext,
            "seconds": time.perf_counter() - t0,
            "path": rel,
            "error": {"exception": type(exc).__name__, "mensagem": str(exc)},
            "connection_lost": True,
            "at": utc_now(),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status": 0,
            "ext": ext,
            "seconds": time.perf_counter() - t0,
            "path": rel,
            "error": {"exception": type(exc).__name__, "mensagem": str(exc)},
            "at": utc_now(),
        }


def parse_args() -> argparse.Namespace:
    raiz = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raiz", type=Path, default=raiz)
    p.add_argument("--corpus", type=Path, default=raiz / "data" / "corpus")
    p.add_argument("--data", type=Path, default=raiz / "data" / "stress-run" / "data")
    p.add_argument(
        "--checkpoint",
        type=Path,
        default=raiz / "data" / "stress-run" / "checkpoint.json",
    )
    p.add_argument("--models", type=Path, default=raiz / "models")
    p.add_argument("--porta", type=int, default=4395)
    p.add_argument("--python", type=Path, default=Path(sys.executable))
    p.add_argument("--max-files", type=int, default=2000)
    p.add_argument("--max-bytes", type=int, default=1_500_000)
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--max-restarts", type=int, default=8)
    p.add_argument("--pause-every", type=int, default=50)
    p.add_argument(
        "--log",
        type=Path,
        default=raiz / "data" / "stress-run" / "stress_server.log",
    )
    p.add_argument("--no-server", action="store_true", help="Assume servidor já a correr")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.corpus.is_dir():
        print(f"corpus em falta: {args.corpus}", file=sys.stderr)
        return 2

    files = collect_files(args.corpus, max_files=args.max_files, max_bytes=args.max_bytes)
    cp = load_checkpoint(args.checkpoint)
    base = f"http://127.0.0.1:{args.porta}"
    print(
        f"files={len(files)} done={len(cp['done'])} porta={args.porta}",
        flush=True,
    )

    start_kwargs = {
        "root": args.raiz,
        "data": args.data,
        "models": args.models,
        "porta": args.porta,
        "python": args.python,
        "log_path": args.log,
    }
    proc: subprocess.Popen | None = None
    client = httpx.Client(timeout=args.timeout)
    t0 = time.perf_counter()
    try:
        if not args.no_server:
            proc = start_server(**start_kwargs)
            cp["server_pid"] = proc.pid
            save_checkpoint(args.checkpoint, cp)

        for i, path in enumerate(files, 1):
            rel = str(path.relative_to(args.corpus))
            if rel in cp["done"] and cp["done"][rel].get("ok"):
                continue

            if not args.no_server:
                proc = ensure_alive(
                    proc,
                    cp,
                    start_kwargs=start_kwargs,
                    checkpoint=args.checkpoint,
                    max_restarts=args.max_restarts,
                    base=base,
                )
                client.close()
                client = httpx.Client(timeout=args.timeout)

            res = ingest_one(client, base, args.corpus, path, args.timeout)
            if res.get("connection_lost") and not args.no_server:
                proc = ensure_alive(
                    proc,
                    cp,
                    start_kwargs=start_kwargs,
                    checkpoint=args.checkpoint,
                    max_restarts=args.max_restarts,
                    base=base,
                )
                client.close()
                client = httpx.Client(timeout=args.timeout)
                res = ingest_one(client, base, args.corpus, path, args.timeout)

            cp["done"][rel] = res
            if i % 10 == 0 or not res["ok"]:
                save_checkpoint(args.checkpoint, cp)
                status = "OK" if res["ok"] else "FAIL"
                print(
                    f"  [{i}/{len(files)}] {status} {res['ext']} "
                    f"{res['seconds']:.2f}s {path.name[:50]}",
                    flush=True,
                )
            if i % args.pause_every == 0:
                save_checkpoint(args.checkpoint, cp)

        save_checkpoint(args.checkpoint, cp)
        wall = time.perf_counter() - t0
        ok_n = sum(1 for r in cp["done"].values() if r.get("ok"))
        fail_n = sum(1 for r in cp["done"].values() if not r.get("ok"))
        by = defaultdict(lambda: {"ok": 0, "fail": 0})
        for r in cp["done"].values():
            by[r["ext"]]["ok" if r["ok"] else "fail"] += 1
        times = [r["seconds"] for r in cp["done"].values() if r.get("ok")]
        print(
            json.dumps(
                {
                    "ok": ok_n,
                    "fail": fail_n,
                    "wall_s": round(wall, 2),
                    "fps": round(ok_n / wall, 3) if wall else None,
                    "by_ext": dict(by),
                    "latency_mean": round(sum(times) / len(times), 3) if times else None,
                    "restarts": cp.get("restarts"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        return 0 if fail_n == 0 else 1
    finally:
        client.close()
        if not args.no_server:
            kill_pg(proc)


if __name__ == "__main__":
    raise SystemExit(main())
