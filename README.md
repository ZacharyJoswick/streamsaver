Stream Saver
============

A tool to automatically download streams live and avoid muted VODs

Goals

 - Easy to use twitch (and other stream) downloader system
 - Leverage streamlink and ffmpeg
 - Cross platform for windows and linux (maybe arm / bsd / others)
 - Able to be used both on a local system or on a remote server
 - Config file or environment variable config
    - Config overwritable by environment variables
 - Optional web ui for management
 - Command line arguments for one off simple things
 - Sqlite db for config / stream records

Code goals
 - Type hints on all the things
 - Simple install
 - Unit tested
 - Cross platform tests
 
Furture things
 - Integration with youtube to automatically upload videos
 - Other streaming platforms
 - Automatic (or tirggered) updates
 - Crash / error reporting