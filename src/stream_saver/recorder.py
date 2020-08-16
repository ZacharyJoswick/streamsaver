import datetime
import enum
import logging
import os
import subprocess
import shutil
import time

import typer
import requests


class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchRecorder:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        streamer: str,
        quality: str,
        root_path: str,
        check_interval: int,
        ffmpeg_path: str = "ffmpeg",
        disable_ffmpeg: bool = False,
    ):
        # global configuration
        self.ffmpeg_path = ffmpeg_path
        self.disable_ffmpeg = disable_ffmpeg
        self.refresh = check_interval
        self.root_path = root_path

        # stream configuration
        self.username = streamer
        self.quality = quality

        # twitch configuration
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = (
            "https://id.twitch.tv/oauth2/token?client_id="
            + self.client_id
            + "&client_secret="
            + self.client_secret
            + "&grant_type=client_credentials"
        )
        self.url = "https://api.twitch.tv/helix/streams"
        self.access_token = self.fetch_access_token()

    def fetch_access_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

    def run(self):
        # path to recorded stream
        recorded_path = os.path.join(self.root_path, "recorded", self.username)
        # path to finished video, errors removed
        processed_path = os.path.join(self.root_path, "processed", self.username)

        # create directory for recordedPath and processedPath if not exist
        os.makedirs(recorded_path, exist_ok=True)
        os.makedirs(processed_path, exist_ok=True)

        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh < 15:
            self.log_and_print(
                "Check interval should not be lower than 15 seconds", level=logging.WARNING, color=typer.colors.YELLOW
            )
            self.refresh = 15
            self.log_and_print(
                "System set check interval to 15 seconds", level=logging.WARNING, color=typer.colors.YELLOW
            )

        # fix videos from previous recording session
        try:
            video_list = [f for f in os.listdir(recorded_path) if os.path.isfile(os.path.join(recorded_path, f))]
            if len(video_list) > 0:
                self.log_and_print(f"Processing {len(video_list)} previously recorded files", level=logging.INFO)
            for f in video_list:
                recorded_filename = os.path.join(recorded_path, f)
                processed_filename = os.path.join(processed_path, f)
                self.process_recorded_file(recorded_filename, processed_filename)
        except Exception as e:
            logging.error(e)

        self.log_and_print(
            f"Checking for {self.username} every {self.refresh} seconds, recording with {self.quality} quality",
            color=typer.colors.BLUE,
        )
        print("")
        self.loop_check(recorded_path, processed_path)

    def process_recorded_file(self, recorded_filename, processed_filename):
        if self.disable_ffmpeg:
            self.log_and_print(f"moving {recorded_filename} to {processed_filename}")
            shutil.move(recorded_filename, processed_filename)
        else:
            self.log_and_print(f"fixing {recorded_filename} and moving to {processed_filename}")
            self.ffmpeg_copy_and_fix_errors(recorded_filename, processed_filename)

    def ffmpeg_copy_and_fix_errors(self, recorded_filename, processed_filename):
        try:
            subprocess.call(
                [
                    self.ffmpeg_path,
                    "-err_detect",
                    "ignore_err",
                    "-i",
                    recorded_filename,
                    "-c",
                    "copy",
                    processed_filename,
                ]
            )
            os.remove(recorded_filename)
        except Exception as e:
            logging.error(e)

    def check_user(self):
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": self.client_id, "Authorization": "Bearer " + self.access_token}
            r = requests.get(self.url + "?user_login=" + self.username, headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

    def sleep_and_print_while_offline(self, sleep_time: int):

        for i in range(sleep_time, 0, -1):
            msg = f"User {self.username} currently offline, checking again in {i} seconds     "
            print(msg, end="\r")
            time.sleep(1.0)
        return

    def log_and_print(self, msg, level=logging.INFO, color=typer.colors.WHITE):
        if level == logging.ERROR:
            logging.error(msg)
        elif level == logging.WARNING:
            logging.warning(msg)
        elif level == logging.INFO:
            logging.info(msg)
        else:
            logging.debug(msg)

        typer.secho(msg, fg=color)

    def loop_check(self, recorded_path, processed_path):
        while True:
            status, info = self.check_user()
            if status == TwitchResponseStatus.NOT_FOUND:
                self.log_and_print(
                    f"Username {self.username} not found, invalid username or typo, exiting",
                    color=typer.colors.RED,
                    level=logging.WARNING,
                )
                raise typer.Exit(code=1)

            elif status == TwitchResponseStatus.ERROR:
                self.log_and_print(
                    "Got unexpected error. Will try again in 1 minute", color=typer.colors.RED, level=logging.WARNING,
                )
                time.sleep(60)
            elif status == TwitchResponseStatus.OFFLINE:

                logging.info(f"User {self.username} currently offline, checking again in {self.refresh} seconds")

                self.sleep_and_print_while_offline(self.refresh)
            elif status == TwitchResponseStatus.UNAUTHORIZED:
                self.log_and_print(
                    "Got unauthorized response, will attempt to log back in immediately",
                    level=logging.WARNING,
                    color=typer.colors.YELLOW,
                )
                self.access_token = self.fetch_access_token()
            elif status == TwitchResponseStatus.ONLINE:
                print("")
                self.log_and_print(
                    f"User {self.username} online, stream recording starting", color=typer.colors.GREEN,
                )
                start_time = time.time()

                channels = info["data"]
                channel = next(iter(channels), None)
                filename = (
                    self.username
                    + "-"
                    + datetime.datetime.now().strftime("%Y-%m-%d-%Hh%Mm%Ss")
                    + "-"
                    + channel.get("title")
                    + ".mp4"
                )

                # clean filename from unnecessary characters
                filename = "".join(x for x in filename if x.isalnum() or x in ["-", "_", "."])

                recorded_filename = os.path.join(recorded_path, filename)
                processed_filename = os.path.join(processed_path, filename)

                self.log_and_print(
                    f"Downloading to path {recorded_filename} at time {datetime.datetime.now().strftime('%Y-%m-%d-%Hh%Mm%Ss')}",
                    color=typer.colors.BLUE,
                )

                # start streamlink process
                subprocess.call(
                    [
                        "streamlink",
                        "--twitch-oauth-token",
                        self.access_token,
                        "twitch.tv/" + self.username,
                        self.quality,
                        "-o",
                        recorded_filename,
                    ]
                )
                end_time = time.time()
                total_time = end_time - start_time

                self.log_and_print(
                    f"Stream recording complete. Total duration was {round(total_time, 3)} seconds",
                    color=typer.colors.GREEN,
                )

                self.log_and_print("Starting video processing step", color=typer.colors.BLUE)

                if os.path.exists(recorded_filename) is True:
                    self.process_recorded_file(recorded_filename, processed_filename)
                else:
                    msg = f"File {recorded_filename} not found, skipping fixing"
                    logging.error(msg)
                    typer.secho(msg, fg=typer.colors.RED)

                self.log_and_print("Processing is done, resuming checking", color=typer.colors.BLUE)
                time.sleep(self.refresh)

