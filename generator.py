import json
import subprocess
from typing import Tuple, Union
from pytubefix import YouTube


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
    result = cmd("node youtube-token-generator.js")
    data = json.loads(result.stdout)
    print(f"Result: {data}")
    return data


def po_token_verifier() -> Union[Tuple[str, str]]:
    token_object = generate_youtube_token()
    return token_object["visitorData"], token_object["poToken"]

def download():
    yt = YouTube(
        url="https://www.youtube.com/watch?v=7GiDgP4F1j8",
        use_po_token= True,
        po_token_verifier=po_token_verifier,
    )
    test = yt.streams
    print(test)

download()