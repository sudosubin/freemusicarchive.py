# freemusicarchive.py

This project is a script that batch downloads music files of a specific genre from [freemusicarchive.org](https://freemusicarchive.org/).

## Getting Started

You must install Python dependencies through Nix flakes, or install them manually.

```sh
# Install through Nix flakes
$ nix develop

# Install manually
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install httpx lxml
```

And you can run the script with the command below. To get the `free_music_archive_session` value, you must first access [freemusicarchive.org](https://freemusicarchive.org/), log in, and extract it directly through the cookie value.

```sh
$ python3 scripts/download_genre_all.py --genre piano --session "<free_music_archive_session>"
usage: download_genre_all.py [-h] --genre GENRE --session SESSION
```

## License

`freemusicarchive.py` is [MIT Licensed](./LICENSE).
