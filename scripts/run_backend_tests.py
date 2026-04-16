from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from backend_smoke import run_smoke_suite, wait_for_health


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULES = [
    "tests.test_45_metrics",
    "tests.test_oo_estimate_metrics",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="SmartMetric 后端自动化测试入口")
    parser.add_argument(
        "--suite",
        choices=("unit", "smoke", "all"),
        default="all",
        help="unit=单元测试，smoke=接口冒烟测试，all=全部",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:5000", help="已启动后端时的访问地址")
    parser.add_argument("--start-server", action="store_true", help="测试前自动启动本地后端服务")
    parser.add_argument("--host", default="127.0.0.1", help="自动启动服务时绑定的 host")
    parser.add_argument("--port", type=int, default=5000, help="自动启动服务时绑定的 port")
    args = parser.parse_args()

    exit_code = 0
    server_process: subprocess.Popen[str] | None = None

    try:
        if args.start_server:
            server_process = start_server(args.host, args.port)
            wait_for_health(args.base_url if not args.base_url.endswith("/") else args.base_url[:-1])

        if args.suite in ("unit", "all"):
            run_unit_tests()

        if args.suite in ("smoke", "all"):
            steps = run_smoke_suite(args.base_url.rstrip("/"))
            print("Smoke checks:")
            for step in steps:
                print(f"  - {step}")
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        exit_code = 1
    finally:
        if server_process is not None:
            stop_server(server_process)

    if exit_code == 0:
        print("[OK] 后端自动化测试完成")
    return exit_code


def run_unit_tests() -> None:
    cmd = [sys.executable, "-m", "unittest", *DEFAULT_MODULES]
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError("单元测试失败")


def start_server(host: str, port: int) -> subprocess.Popen[str]:
    cmd = [sys.executable, str(ROOT / "backend" / "cli.py"), "serve", "--host", host, "--port", str(port)]
    return subprocess.Popen(
        cmd,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def stop_server(process: subprocess.Popen[str]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:  # pragma: no cover - safety net
        process.kill()
        process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
