 ---

# 🎬 JoshMovies Scraper & Downloader

A powerful and user-friendly command-line tool designed to simplify the process of getting content from `joshmovies.com`. This script intelligently handles the complex redirect chains and ad-link pages, allowing you to get the final, direct download link with just a few prompts.

It can handle both movies and TV series, automatically detecting the content type and adjusting its strategy accordingly.

 
*(This is a representative image of how the colorful command-line interface looks and feels.)*

---

## ✨ Features

*   **Smart Content Detection:** Automatically identifies whether a link is for a single movie or a full series and adapts its scraping workflow.
*   **User-Friendly Interface:** A clean, color-coded command-line interface guides you through every step of the process.
*   **Choice of Output:** You can choose to either directly download the video files or save the final links neatly into a Markdown (`.md`) file.
*   **Bulk Processing for Series:** When a series is detected, the tool fetches the complete episode list and allows you to download a specific range of episodes (e.g., episodes 5 through 10).
*   **Append, Don't Overwrite:** When saving links, the script adds new links to your file without overwriting the existing contents.
*   **Persistent Output Directory:** The tool remembers the output folder you used during a session, so you don't have to re-type it every time.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python 3.7** or newer.
*   **pip** (Python's package installer).

---

## 🚀 Getting Started

Follow these simple steps to set up and run the tool on your local machine.

### Step 1: Clone the Repository

First, clone this repository to your computer using Git. Open your terminal and run:

```bash
git clone [https://github.com/DCspare/Joshmovies-Scraper.git](https://github.com/DCspare/Joshmovies-Scraper.git)
cd Joshmovie-Scraper
```

### Step 2: Install Required Libraries

This project uses a few external Python libraries. You can install them all with a single command:

```bash
pip install requests beautifulsoup4 colorama
```

### Step 3: Run the Script

Once the setup is complete, you are ready to run the tool. Simply execute the script using Python:

```bash
python Scraper_V04.py
```

The script will launch, and from there you just need to follow the on-screen prompts. It will ask you for the URL, your preferred output (download or save link), and the destination folder.

---

## Act like a reasonable human, not a robot.**

*   **To Avoid Getting Blocked:**
    *   You can use the tool to download a movie or a full season without issue.
    *   After downloading a full season, **wait a few minutes** before starting another one.
    *   **Do not** run the script in a rapid, back-to-back loop for hours. This high-frequency activity is what gets your IP address blocked by websites.


## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. The content available on the target website is likely subject to copyright protection.

*   The developers of this tool do not host, nor are they affiliated with, any of the content made accessible through this script.
*   Users are solely responsible for their actions and for ensuring they are not violating any copyright laws in their country of residence.
*   Please use this tool responsibly. The developers assume no liability for any misuse of this software.
