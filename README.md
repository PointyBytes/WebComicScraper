# Image Downloader Script

This repository hosts an image downloader script designed to download a series of images from specified URLs. It is an ongoing project, and the current version is an early iteration with plans for further expansion and feature enhancements.


## Inspiration

The creation of this script was inspired by the book *Automate the Boring Stuff with Python* by Al Sweigart. The project also utilized OpenAI's GPT-3.5 to assist with coding challenges.

- **Author's Personal Web Page:** [Al Sweigart](https://alsweigart.com/)
- **Author's GitHub:** [asweigart](https://github.com/asweigart/)
- **Book Website:** [Automate the Boring Stuff](https://automatetheboringstuff.com/)
- **Print Version of the Book:** [No Starch Press](https://nostarch.com/automatestuff2) - Note: A 3rd edition is upcoming.


## Getting Started

### Prerequisites
Ensure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).

### Installation
Clone or download this repository to your local machine:

```bash
git clone https://github.com/PointyBytes/WebComicScraper.git
```

Navigate into the project directory:
```bash
cd WebComicScraper
```

All the necessary libraries are listed in the [*requirements.txt*](requirements.txt) file.
Before running the script, install the required Python libraries by running the following command in your terminal:

```bash
pip install -r requirements.txt
```

This will ensure all dependencies are installed as per the requirements listed.

### Configuration
Modify the the name and `settings_example.py` file with the necessary parameters:

#### To use this script:
1. Clone or download this repository to your local machine.
2. Create a copy of the `settings_example.py` file and rename it to `settings.py`.
3. Adjust the `settings.py` file with the correct `BASE_URL`, `NUM_IMAGES`, and `OUTPUT_FOLDER` before running the script.

```python
# Example settings.py configuration
base_url = "https://example.com/images/"
num_images = 50
output_folder = "./Downloads/"
make_cbz = False
cbz_filename = "Name of the Comic"
```

### Running the Script
Execute the script from your command line:

```bach
python main.py
```

This will start the process of downloading the specified number of images into the designated output folder.


## Contribution

Contributions are welcome! If you have ideas for features or have found a bug, please open an issue or a pull request.


## Note

This is an early version of the script, and I plan to expand it with more features and possibly GUI support in the future. Stay tuned!


## License

This project is open source and available under the **GNU GPL v3.0 or later**. You can find the full license text in the [LICENSE](LICENSE) file within this repository.
