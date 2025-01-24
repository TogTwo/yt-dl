import json
import subprocess
from typing import Tuple, Optional

def cmd(command, check=True, shell=True, capture_output=True, text=True):
    """
    Runs a command in a shell, and throws an exception if the return code is non-zero.
    :param command: any shell command.
    :return:
    """
    print(f" + {command}")
    try:
        return subprocess.run(command, check=check, shell=shell, capture_output=capture_output, text=text)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"\"{command}\" returned exit code {error.returncode}\n"
            f"Stdout: {error.stdout}\n"
            f"Stderr: {error.stderr}"
        )

def generate_youtube_token() -> dict:
    print("Generating YouTube token")
    result = cmd(".\\node-v22.13.1-win-x64\\node youtube-token-generator.js")
    data = json.loads(result.stdout)
    print(f"Result: {data}")
    return data


def po_token_verifier() -> Optional[Tuple[str, str]]:
    token_object = generate_youtube_token()
    return token_object["visitorData"], token_object["poToken"]

