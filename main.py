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
# TODO: Add MOTD to this projekt.
# TODO: Make a list that adds what images failed to be saved.

import requests
import os
import zipfile
from settings import base_url, num_images, output_folder, make_cbz, cbz_filename


class ImageDownloader:
    """A class to handle downloading of images from a specified base URL to a local folder."""

    def __init__(self, base_url, output_folder):
        """
        Initialize the downloader with the base URL and output directory.

        Args:
        base_url (str): The URL where the images are located.
        output_folder (str): The local directory where images will be saved.
        """
        self.base_url = base_url
        self.output_folder = output_folder
        self.downloaded = 0
        self.failed_downloads = []

    def download_images(self, num_images):
        """Download a specified number of images and save them locally."""
        # Ensure the output directory exists; if not, create it.
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for i in range(1, num_images + 1):
            image_url = f"{self.base_url}{i}"
            response = requests.get(image_url)
            content_type = response.headers["Content-Type"]
            extension = self.get_file_extension(content_type)
            image_path = os.path.join(
                self.output_folder, f"{str(i).zfill(3)}{extension}"
            )

            if response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(response.content)
                print(f"Image {image_path} saved successfully.")
                self.downloaded += 1
            else:
                print(f"Failed to fetch image {image_path}")
                self.failed_downloads.append(f"{str(i).zfill(3)}{extension}")

    def get_file_extension(self, content_type):
        """Return the file extension based on the MIME type."""
        if "image/jpeg" in content_type:
            return ".jpg"
        elif "image/png" in content_type:
            return ".png"
        elif "image/gif" in content_type:
            return ".gif"
        else:
            return ""  # Default, if unknown or unsupported type

    def results(self):
        """Print results of the download process, including any failed downloads."""
        print(
            f"{self.downloaded} of {num_images} images downloaded to {self.output_folder}."
        )
        if self.failed_downloads:
            print("Failed downloads:", self.failed_downloads)


class CBZCreator:
    """A class to create a CBZ file from all images in a specified folder."""

    def __init__(self, folder_path, output_file):
        """
        Initialize the CBZ creator with the folder containing images and the desired output file name.

        Args:
        folder_path (str): Path to the folder containing images.
        output_file (str): Filename for the output CBZ file.
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
        print(f"CBZ file created: {self.output_file}")


if __name__ == "__main__":
    downloader = ImageDownloader(base_url, output_folder)
    downloader.download_images(num_images)
    downloader.results()

    # Optionally create a CBZ file if the setting is enabled
    if make_cbz:
        cbz_creator = CBZCreator(output_folder, f"{cbz_filename}.cbz")
        cbz_creator.create_cbz()
