import configparser
import os
from pathlib import Path
import typer
from enum import Enum

config_path = os.path.join(str(Path.home()), "stream_saver.ini")


class Platform(Enum):
    WINDOWS = (0,)
    LINUX = 1


def get_platform() -> Platform:
    if os.name == "nt":
        return Platform.WINDOWS
    else:
        return Platform.LINUX


def get_config():
    if not os.path.isfile(config_path):
        # Config does not exist, create it
        create_default_config()

    config = configparser.ConfigParser()
    config.read(config_path)

    return config


def get_ffmpeg():
    src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if get_platform() == Platform.WINDOWS:
        return os.path.join(src_dir, "binaries", "ffmpeg-4.3.1-win64/ffmpeg.exe")
    else:
        return os.path.join(src_dir, "binaries", "ffmpeg-4.3.1-linux/ffmpeg")


def create_default_config():
    typer.echo(
        "It looks like this is your first run of the stream saver. The following questions will set up your config"
    )

    typer.echo(
        "This script requires you to create a twitch developer application. The instructions for doing so are located in the readme"
    )
    typer.echo("Please complete those steps before continuing")

    confirm = typer.prompt("When you are ready press Y")
    if confirm.upper() != "Y":
        typer.secho("Exiting", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config = configparser.ConfigParser()
    config["STREAM_SAVER"] = {}

    # Get client ID
    config["STREAM_SAVER"]["client_id"] = typer.prompt("What is the client ID from the twitch developer site?")

    # Get client secret
    config["STREAM_SAVER"]["client_secret"] = typer.prompt("What is the client secret from the twitch developer site?")

    # Get username
    config["STREAM_SAVER"]["username"] = typer.prompt("What is your twitch username?")

    # Get download filepath
    tmp_download_dir = os.path.join(str(Path.home()), "Downloads", "twitch-downloads")

    config["STREAM_SAVER"]["download_dir"] = typer.prompt(
        "Where do you want downloads to go?", default=tmp_download_dir
    )
    # Set default download directory and create it if it does not exist
    if not os.path.exists(config["STREAM_SAVER"]["download_dir"]):
        os.makedirs(config["STREAM_SAVER"]["download_dir"])

    # Write out config file
    with open(config_path, "w") as configfile:
        config.write(configfile)
