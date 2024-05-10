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
# TODO: Add MOTD to this project.
# TODO: Make a list that adds what images failed to be saved.

import requests
import os
import zipfile
import logging
from settings import base_url, num_images, output_folder, make_cbz, cbz_filename

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="download_images.log",
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

    def __init__(self, base_url, output_folder, num_images, make_cbz):
        """
        Initialize the downloader with the base URL and output directory.
        """
        self.base_url = base_url
        self.output_folder = output_folder
        self.num_images = num_images
        self.make_cbz = make_cbz
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

        for i in range(1, self.num_images + 1):
            image_url = f"{self.base_url}{i}.jpg"
            response = requests.get(image_url)
            content_type = response.headers.get("Content-Type", "")
            extension = self.get_file_extension(content_type)

            if extension:
                image_path = os.path.join(
                    self.output_folder, f"{str(i).zfill(3)}{extension}"
                )
                if response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    logging.info(f"Image {image_path} saved successfully.")
                    self.downloaded += 1
                else:
                    logging.warning(f"Failed to fetch image {image_url}")
                    self.failed_downloads.append(f"{str(i).zfill(3)}{extension}")
            else:
                logging.error(
                    f"Unexpected content type for URL {image_url}: {content_type}"
                )

            printProgressBar(
                i, self.num_images, prefix="Progress:", suffix="Complete", length=50
            )

    def get_file_extension(self, content_type):
        """Return the file extension based on the MIME type."""
        mapping = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif"}
        return mapping.get(content_type.split(";")[0], "")  # Split to ignore charset

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
                    if file.endswith((".png", ".jpg", ".jpeg")):
                        zipf.write(os.path.join(root, file), file)
        logging.info(f"CBZ file created: {self.output_file}")


if __name__ == "__main__":
    downloader = ImageDownloader(base_url, output_folder, num_images, make_cbz)
    downloader.download_images()
    downloader.results()

    # Optionally create a CBZ file if the setting is enabled
    if make_cbz:
        # Ensure the CBZ file is saved in the output folder by combining the folder path and file name
        cbz_file_path = os.path.join(output_folder, f"{cbz_filename}.cbz")
        cbz_creator = CBZCreator(output_folder, cbz_file_path)
        cbz_creator.create_cbz()
