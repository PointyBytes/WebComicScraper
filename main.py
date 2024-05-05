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

# TODO: Refaktor adding funktions and classes.
# TODO: Do not overrite files
# TODO: Add MOTD to this projekt.

import requests
import os
import zipfile
import settings

base_url = settings.base_url  # Base URL where the images can be found
num_images = settings.num_images  # Number of images to download
output_folder = settings.output_folder  # Name of the folder to save images
make_cbz = settings.make_cbz
cbz_filename = f"{settings.cbz_filename}.cbz"
num_downloaded = 0
failed_downloads = []


def zip_images(folder_path, output_file):
    """
    Zip all images in a specified folder into a single CBZ file.

    Args:
    folder_path (str): Path to the folder containing images.
    output_file (str): Filename for the output CBZ file.
    """
    with zipfile.ZipFile(output_file, "w") as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith((".png", ".jpg", ".jpeg")):
                    zipf.write(os.path.join(root, file), file)
    print(f"CBZ file created: {output_file}")


# Create the folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for i in range(1, num_images + 1):
    image_url = f"{base_url}{i}.jpg"
    response = requests.get(image_url)
    # Using str.zfill() to ensure the filename always has three digits
    image_path = os.path.join(
        output_folder, f"{str(i).zfill(3)}.jpg"
    )  # Complete path to the image including the folder name

    if response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Image {image_path} saved successfully.")
        num_downloaded += 1
    else:
        print(f"Failed to fetch image {image_path}")
        failed_downloads.append(f"{str(i).zfill(3)}.jpg")

# Will create a CBZ file of all saved files if make_cbz is True
if make_cbz:
    zip_images(output_folder, cbz_filename)

# TODO: Make a list that adds what images failed to saved.
print(f"{num_downloaded} of {num_images} images downloaded to {output_folder}.")
print(failed_downloads)
