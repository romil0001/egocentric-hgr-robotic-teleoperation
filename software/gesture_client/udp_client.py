"""UDP client for sending gesture teleoperation commands to the ESP32 arm."""

from __future__ import annotations

import socket
from collections import deque
from typing import Deque, Optional, Tuple


class RobustUdpClient:
    """Send a command only after it is confirmed for ``confirm_frames`` consecutive frames."""

    def __init__(
        self,
        address: Tuple[str, int],
        confirm_frames: int = 5,
        payload_suffix: str = "100,0,0,0",
    ) -> None:
        self.address = address
        self.confirm_frames = max(1, int(confirm_frames))
        self.payload_suffix = payload_suffix
        self._history: Deque[str] = deque(maxlen=self.confirm_frames)
        self._sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.last_sent: Optional[str] = None

    def observe(self, command: str) -> bool:
        """
        Record a classified command. Returns True if a UDP datagram was sent.

        Protocol: ``"<CMD>,100,0,0,0"`` (comma-separated; ESP32 DataParser reads field 0).
        """
        self._history.append(command)
        if len(self._history) < self.confirm_frames:
            return False
        if self._history.count(command) != self.confirm_frames:
            return False

        message = f"{command},{self.payload_suffix}"
        self._sock.sendto(message.encode("utf-8"), self.address)
        self.last_sent = command
        return True

    def close(self) -> None:
        self._sock.close()
