"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

This script was inspired by "Automate the Boring Stuff with Python" by Al Sweigart,
and was developed with assistance from OpenAI's GPT-3.5.
"""

# TODO: Do not overwrite files
# TODO: Add menu to select which images to download.
# TODO: Add MOTD to this project.
# DONE: Added error handling for failed downloads and detailed logging.
# TODO: Add timestamps to log filename to avoid super long logs and make it easier to track different runs.
# TODO: Make the script more robust by checking for valid URLs and handling exceptions gracefully.
# TODO: Make num_images optional by checking for the last image number in the base URL and downloading until it fails. Without breaking the progress bar.
# DONE: Added support for multiple image formats (PNG, GIF, WEBP) and detection fallbacks.
# DONE: Fixed downloading of WEBP images; script now attempts common extensions and saves WEBP files.
# TODO: Add a flag to delete the downloaded images after creating the CBZ file to save disk space.

import requests
import os
import zipfile
import logging
from datetime import datetime
from settings import (
    base_url,
    num_images,
    output_folder,
    make_cbz,
    delete_images_after_cbz,
    cbz_filename,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename=f"download_images_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    if iteration == total:
        print()


class ImageDownloader:
    """A class to handle downloading of images from a specified base URL to a local folder."""

    def __init__(
        self, base_url, output_folder, num_images, make_cbz, delete_images_after_cbz
    ):
        """
        Initialize the downloader with the base URL and output directory.
        """
        self.base_url = base_url
        self.output_folder = output_folder
        self.num_images = num_images
        self.make_cbz = make_cbz
        self.delete_images_after_cbz = delete_images_after_cbz
        self.downloaded = 0
        self.failed_downloads = []

    def download_images(self):
        """Download images and save them locally."""
        # Ensure the output directory exists; if not, create it.
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            logging.info(f"Created directory {self.output_folder}")

        printProgressBar(
            0, self.num_images, prefix="Progress:", suffix="Complete", length=50
        )

        # Try common image extensions when the server may use different formats (jpg, webp, png, gif)
        candidate_exts = [".jpg", ".png", ".webp", ".gif"]
        for i in range(1, self.num_images + 1):
            found = False
            last_error = None
            for try_ext in candidate_exts:
                image_url = f"{self.base_url}{i}{try_ext}"
                logging.debug(f"Attempting {image_url}")
                try:
                    # Stream to inspect headers before downloading full body
                    response = requests.get(image_url, timeout=15, stream=True)
                except requests.RequestException as e:
                    logging.debug(f"Request exception for {image_url}: {e}")
                    last_error = e
                    continue

                # If resource not found, try next extension
                if response.status_code == 404:
                    logging.debug(f"Not found: {image_url} (404)")
                    continue

                # Read content only when status is OK or other non-404
                try:
                    content = response.content
                except Exception as e:
                    logging.error(f"Failed reading content from {image_url}: {e}")
                    last_error = e
                    continue

                content_type = response.headers.get("Content-Type", "")
                extension = self.get_file_extension(content_type, response.url, content)

                logging.debug(
                    f"Tried {image_url} -> {response.url} status={response.status_code} content-type={content_type!r} detected-ext={extension} bytes={len(content)}"
                )

                if not extension:
                    # Save a debug sample for inspection
                    try:
                        debug_path = os.path.join(
                            self.output_folder, f"debug_{str(i).zfill(3)}.bin"
                        )
                        if not os.path.exists(debug_path) and content:
                            with open(debug_path, "wb") as dbg:
                                dbg.write(content[:4096])
                            logging.info(
                                f"Saved debug sample for {image_url} -> {debug_path}"
                            )
                    except Exception as e:
                        logging.error(
                            f"Failed saving debug sample for {image_url}: {e}"
                        )

                    logging.error(
                        f"Unknown content for {image_url}: header={content_type!r} url={response.url}"
                    )
                    last_error = f"unknown content: {content_type}"
                    continue

                # Found a valid image
                image_path = os.path.join(
                    self.output_folder, f"{str(i).zfill(3)}{extension}"
                )
                if response.status_code == 200:
                    try:
                        with open(image_path, "wb") as f:
                            f.write(content)
                        logging.info(f"Image {image_path} saved successfully.")
                        self.downloaded += 1
                        found = True
                        break
                    except Exception as e:
                        logging.error(f"Failed to write file {image_path}: {e}")
                        last_error = e
                        break
                else:
                    logging.warning(
                        f"Unexpected status {response.status_code} for {image_url}"
                    )
                    last_error = f"status {response.status_code}"

            if not found:
                err_msg = last_error or "not found"
                self.failed_downloads.append(f"{str(i).zfill(3)} - {err_msg}")

            printProgressBar(
                i, self.num_images, prefix="Progress:", suffix="Complete", length=50
            )

    def get_file_extension(self, content_type, url="", content_bytes=None):
        """Return the file extension based on the MIME type, URL, or image bytes.

        Tries in order:
        - Normalize `Content-Type` header and match common types (including variants).
        - Inspect the final `response.url` for a known extension.
        - Fallback to `imghdr` on the bytes (if provided).
        Returns an empty string when no known extension can be determined.
        """
        if content_type:
            ct = content_type.split(";")[0].strip().lower()
            # Common exact mappings
            mapping = {
                "image/jpeg": ".jpg",
                "image/jpg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "image/webp": ".webp",
                "image/x-webp": ".webp",
            }
            if ct in mapping:
                return mapping[ct]
            # Handle loose matches like 'image/vnd.something+webp' or variants
            if "webp" in ct:
                return ".webp"
            if "jpeg" in ct or "jpg" in ct:
                return ".jpg"
            if "png" in ct:
                return ".png"
            if "gif" in ct:
                return ".gif"

        # Try to get extension from URL (after redirects)
        if url:
            try:
                _, ext = os.path.splitext(url.split("?")[0])
                ext = ext.lower()
                if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                    return ".jpg" if ext == ".jpeg" else ext
            except Exception:
                pass

        # Final fallback: detect from bytes using simple file signatures (no extra deps)
        if content_bytes:
            try:
                # PNG signature
                if content_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                    return ".png"
                # JPEG starts with FF D8
                if content_bytes.startswith(b"\xff\xd8"):
                    return ".jpg"
                # GIF (GIF87a or GIF89a)
                if content_bytes.startswith(b"GIF87a") or content_bytes.startswith(
                    b"GIF89a"
                ):
                    return ".gif"
                # WEBP: RIFF....WEBP
                if (
                    len(content_bytes) >= 12
                    and content_bytes[0:4] == b"RIFF"
                    and content_bytes[8:12] == b"WEBP"
                ):
                    return ".webp"
            except Exception:
                pass

        return ""

    def _request(self, url, timeout=15, stream=True):
        """Perform a requests.get and return the response or None on error."""
        try:
            return requests.get(url, timeout=timeout, stream=stream)
        except requests.RequestException as e:
            logging.debug(f"Request exception for {url}: {e}")
            return None

    def _save_file(self, image_path, content):
        """Write bytes to disk and return True on success."""
        try:
            with open(image_path, "wb") as f:
                f.write(content)
            logging.info(f"Image {image_path} saved successfully.")
            self.downloaded += 1
            return True
        except Exception as e:
            logging.error(f"Failed to write file {image_path}: {e}")
            return False

    def _save_debug_sample(self, i, content, image_url):
        """Save a small debug sample for inspection without overwriting existing samples."""
        try:
            debug_path = os.path.join(
                self.output_folder, f"debug_{str(i).zfill(3)}.bin"
            )
            if not os.path.exists(debug_path) and content:
                with open(debug_path, "wb") as dbg:
                    dbg.write(content[:4096])
                logging.info(f"Saved debug sample for {image_url} -> {debug_path}")
        except Exception as e:
            logging.error(f"Failed saving debug sample for {image_url}: {e}")

    def results(self):
        """Print results of the download process, including any failed downloads."""
        logging.info(
            f"{self.downloaded} of {self.num_images} images downloaded to {self.output_folder}."
        )
        if self.failed_downloads:
            logging.info("Failed downloads: " + ", ".join(self.failed_downloads))


class CBZCreator:
    """A class to create a CBZ file from all images in a specified folder."""

    def __init__(self, folder_path, output_file):
        """
        Initialize the CBZ creator with the folder containing images and the desired output file name.
        """
        self.folder_path = folder_path
        self.output_file = output_file

    def create_cbz(self):
        """Zip all images in the specified folder into a single CBZ file."""
        with zipfile.ZipFile(self.output_file, "w") as zipf:
            for root, dirs, files in os.walk(self.folder_path):
                for file in files:
                    if file.endswith((".png", ".jpg", ".jpeg", ".webp")):
                        zipf.write(os.path.join(root, file), file)
        logging.info(f"CBZ file created: {self.output_file}")


if __name__ == "__main__":
    downloader = ImageDownloader(
        base_url, output_folder, num_images, make_cbz, delete_images_after_cbz
    )
    downloader.download_images()
    downloader.results()

    if make_cbz:
        cbz_file_path = os.path.join(output_folder, f"{cbz_filename}.cbz")
        cbz_creator = CBZCreator(output_folder, cbz_file_path)
        cbz_creator.create_cbz()
        if delete_images_after_cbz:
            # Remove image files after creating CBZ
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    if (
                        file.endswith((".png", ".jpg", ".jpeg", ".webp"))
                        and file != f"{cbz_filename}.cbz"
                    ):
                        try:
                            os.remove(os.path.join(root, file))
                        except Exception as e:
                            logging.error(f"Failed to delete {file}: {e}")
