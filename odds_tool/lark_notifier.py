import subprocess


class LarkNotifier:
    def __init__(self, binary: str = "lark-cli"):
        self.binary = binary

    def send_text(self, target: str, text: str) -> None:
        command = [
            self.binary,
            "im",
            "+messages-send",
            "--chat-id",
            target,
            "--text",
            text,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "飞书消息发送失败")
