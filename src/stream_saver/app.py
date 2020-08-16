import typer

from stream_saver.config import get_config, get_ffmpeg
from stream_saver.recorder import TwitchRecorder

# For setting the user agent
try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata


app = typer.Typer()


@app.callback()
def docs():
    f"""
    Stream Saver v{metadata.version("stream_saver")}

    Waits until a streamer starts streaming and downloads the stream live. 
    Intended to be used to circumvent twitch vod muting and simplify the archive process. 
    """


def quality_callback(value: str):
    valid_qualities = [
        "160p",
        "360p",
        "480p",
        "720p",
        "720p60",
        "1080p",
        "1080p60",
        "best",
        "worst",
    ]

    if value not in valid_qualities:
        raise typer.BadParameter(f"Invalid quality {value} provided, must be one of {', '.join(valid_qualities)}")
    return value


@app.command()
def download(
    streamer: str = typer.Argument(..., help="The username of the streamer to download"),
    quality: str = typer.Option(
        "best", help="Quality of the stream to download, defaults to best", callback=quality_callback,
    ),
    interval: int = typer.Option(15, help="Number of seconds between stream checks. Don't go lower than 15"),
):
    """
    Wait until a user is online then save their stream
    """

    config = get_config()["STREAM_SAVER"]

    recorder = TwitchRecorder(
        config["client_id"], config["client_secret"], streamer, quality, config["download_dir"], interval, get_ffmpeg()
    )

    recorder.run()


@app.command()
def debug():
    """
    Prints debug info
    """
    import platform
    import glob
    from pathlib import Path
    import os

    typer.secho(
        "Printing stream saver cli debug info. Please copy and paste from this line to the end of the output when asking for support",
        fg=typer.colors.YELLOW,
    )

    typer.echo("Platform info:")
    uname = platform.uname()
    typer.echo(f"System: {uname.system}")
    typer.echo(f"Node Name: {uname.node}")
    typer.echo(f"Release: {uname.release}")
    typer.echo(f"Version: {uname.version}")
    typer.echo(f"Machine: {uname.machine}")
    typer.echo(f"Processor: {uname.processor}")
    typer.echo("")

    typer.echo("Config is:")
    typer.echo({section: dict(get_config()[section]) for section in get_config().sections()})
    typer.echo("")

    crash_files = glob.glob(os.path.join(str(Path.home()), "stream_saver_debug/*.crash.log"))

    if len(crash_files) > 0:
        typer.echo(f"Found {len(crash_files)} crash logs\n")

        for c_file in crash_files:
            with open(c_file) as f:
                typer.echo(f"{'='*11} File {c_file} contents start {'='*11}")
                typer.echo(f.read())
                typer.echo(f"{'='*11} File {c_file} contents end {'='*11}\n\n")
    else:
        typer.echo("Did not find any crash logs, exiting")


def run():
    try:
        app()
    except Exception as e:
        typer.secho(
            "Caught exception. Generating crash report. Contact the author and run 'stream_saver debug` for more info",
            fg=typer.colors.RED,
        )
        import platform
        import os
        from datetime import datetime
        from pathlib import Path
        import traceback

        debug_file = os.path.join(
            str(Path.home()), "stream_saver_debug", f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.crash.log",
        )
        os.makedirs(os.path.dirname(debug_file), exist_ok=True)

        with open(debug_file, "w") as f:
            f.write(f"Got an exception in infra cli at {datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}\n")
            f.write("Platform info:\n")
            uname = platform.uname()
            f.write(f"System: {uname.system}\n")
            f.write(f"Node Name: {uname.node}\n")
            f.write(f"Release: {uname.release}\n")
            f.write(f"Version: {uname.version}\n")
            f.write(f"Machine: {uname.machine}\n")
            f.write(f"Processor: {uname.processor}\n\n")
            f.write("Exception was:\n")
            f.write(str(e))
            f.write("\n\n")
            f.write("Stack trace was:\n")
            f.write(traceback.format_exc())
            f.write("\n")
