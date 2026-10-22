#!/usr/bin/env python3
"""Send teleoperation commands over UDP without a camera (firmware bench test)."""

from __future__ import annotations

import argparse
import socket
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="UDP gesture-command simulator")
    parser.add_argument("--host", required=True, help="ESP32 IP address")
    parser.add_argument("--port", type=int, default=8266)
    parser.add_argument(
        "--command",
        default="B",
        help="Command letter A–I (default: B)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="Number of datagrams to send (default: 5, matches robust confirm)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Seconds between datagrams",
    )
    parser.add_argument(
        "--suffix",
        default="100,0,0,0",
        help="Trailing CSV fields for DataParser compatibility",
    )
    args = parser.parse_args()

    payload = f"{args.command},{args.suffix}".encode("utf-8")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (args.host, args.port)

    for i in range(args.repeat):
        sock.sendto(payload, addr)
        print(f"[{i + 1}/{args.repeat}] sent {payload!r} → {addr}")
        time.sleep(args.interval)

    sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
