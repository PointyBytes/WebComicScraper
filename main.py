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
# TODO: Add MOTD to this projekt.

import requests
import os
import settings

base_url = settings.BASE_URL  # Base URL where the images can be found
num_images = settings.NUM_IMAGES  # Number of images to download
output_folder = settings.OUTPUT_FOLDER  # Name of the folder to save images
num_downloaded = 0
failed_downloads = []


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

# TODO: Make a list that adds what images failed to saved.
print(f"{num_downloaded} of {num_images} images downloaded to {output_folder}.")
