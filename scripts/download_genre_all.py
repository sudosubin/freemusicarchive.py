import argparse
import json
import logging
import logging.config
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from lxml import html

logger = logging.getLogger("default")


class Command:
    def __init__(self) -> None:
        with open(Path(__file__).parent.parent / "conf.d/logging.json") as f:
            logging.config.dictConfig(json.load(f))

        self.args = self.get_arguments()
        self.client = httpx.Client()
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.paths = set()

    def get_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Download all music")
        parser.add_argument("--genre", type=str, help="Genre", required=True)
        parser.add_argument("--session", type=str, help="Session", required=True)
        return parser.parse_args()

    def handle(self) -> None:
        audios_dir = Path(__file__).parent.parent / "audios"
        if not audios_dir.exists():
            logger.info("creating audios directory")
            audios_dir.mkdir(parents=True, exist_ok=True)

        index_url = f"https://freemusicarchive.org/genre/{self.args.genre}/"
        logger.info(f"using {index_url}")

        max_page = self.get_max_page_from_index_html(index_url)

        for page in range(1, max_page + 1):
            for music_item in self.get_page_music_items(index_url, page):
                logger.info(f"- {music_item['artistName']} - {music_item['title']}")
                download_path = audios_dir / (
                    f"{music_item['title']} by {music_item['artistName']}".replace(
                        ".mp3.mp3", ".mp3"
                    ).replace("/", "-")
                )

                if download_path in self.paths:
                    logger.info(f"- skipping {download_path}")
                    continue

                self.paths.add(download_path)
                self.executor.submit(
                    self.download_music, music_item["downloadUrl"], download_path
                )

        self.executor.shutdown()

    def get_max_page_from_index_html(self, index_url: str) -> int:
        logger.info(f"fetching {index_url}, page 1")
        response = self.client.get(index_url, params={"pageSize": 200, "page": 1})
        tree = html.fromstring(response.text)
        pagination_div = tree.find_class("pagination-full")[0]
        page_numbers = pagination_div.xpath(".//a/text()")

        return max(int(page) for page in page_numbers if page.isdigit())

    def get_page_music_items(
        self, index_url: str, page: int
    ) -> typing.Generator[dict, None, None]:
        logger.info(f"fetching {index_url}, page {page}")
        response = self.client.get(index_url, params={"pageSize": 200, "page": page})
        tree = html.fromstring(response.text)

        for play_item in tree.find_class("play-item"):
            data_track_info = json.loads(play_item.get("data-track-info"))
            yield data_track_info

    def download_music(self, download_url: str, download_path: Path) -> None:
        with open(f"{download_path}.mp3", "wb") as f:
            with httpx.stream(
                "GET",
                download_url,
                cookies={"free_music_archive_session": self.args.session},
                follow_redirects=True,
            ) as r:
                for chunk in r.iter_bytes():
                    f.write(chunk)


if __name__ == "__main__":
    command = Command()
    command.handle()
