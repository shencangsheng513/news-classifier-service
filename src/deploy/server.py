"""服务启动入口：deploy-serve。端口/worker 数全部走 DEPLOY_ 环境变量，命令行只做临时覆盖。"""

import argparse

import uvicorn

from .config import get_settings


def main(argv: list[str] | None = None) -> None:
    s = get_settings()
    ap = argparse.ArgumentParser(prog="deploy-serve", description="run the inference service")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=s.port)
    ap.add_argument("--workers", type=int, default=s.workers)
    args = ap.parse_args(argv)
    uvicorn.run("deploy.service:app", host=args.host, port=args.port, workers=args.workers)


if __name__ == "__main__":
    main()
