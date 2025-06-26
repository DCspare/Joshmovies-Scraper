import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import json
from urllib.parse import urljoin
from colorama import init, Fore, Style

# --- Colorama and Config Initialization ---
init(autoreset=True)
CONFIG_FILE = 'josh_scraper_config.json'

# --- Helper and Configuration Functions ---

def c_print(color, text):
    print(color + text)

def load_config():
    """Loads settings from the config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return defaults if file doesn't exist or is empty/corrupt
        return {'output_folder': None, 'md_filename': 'download_links.md'}

def save_config(config_data):
    """Saves settings to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def get_soup(url):
    """Makes a GET request and returns a BeautifulSoup object."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        c_print(Fore.RED, f"  [Error] Could not fetch URL {url}: {e}")
        return None

def download_file(url, folder, filename):
    filepath = os.path.normpath(os.path.join(folder, filename))
    c_print(Fore.YELLOW, f"  Starting download: {filename}")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f: [f.write(chunk) for chunk in r.iter_content(chunk_size=8192)]
        c_print(Fore.GREEN, f"  Successfully downloaded to: {filepath}")
    except requests.exceptions.RequestException as e:
        c_print(Fore.RED, f"  [Error] Download failed for {url}: {e}")

def save_link_to_file(link, folder, filename, content_title):
    filepath = os.path.normpath(os.path.join(folder, filename))
    md_entry = f"### {content_title}\n[Direct Download Link]({link})\n\n"
    try:
        with open(filepath, "a", encoding="utf-8") as f: f.write(md_entry)
        c_print(Fore.GREEN, f"  Successfully saved link to: {filepath}")
    except IOError as e:
        c_print(Fore.RED, f"  [Error] Could not write to file {filepath}: {e}")

# --- Core Scraping Chain ---

def get_options_from_main_page(url):
    c_print(Fore.CYAN, "[Step 1] Finding all options on the main page...")
    soup = get_soup(url)
    if not soup: return None, {}
    page_title = soup.find('title').text.strip()
    options = {}
    all_buttons = soup.find_all('a', class_='maxbutton')
    for button in all_buttons:
        header_tag = button.find_parent('p').find_previous(['h2', 'h3', 'h4'])
        if header_tag:
            header_text = header_tag.text.strip().replace('\n', ' ')
            options[header_text] = urljoin(url, button['href'])
            c_print(Style.DIM, f"  > Found '{header_text}'")
    if not options: c_print(Fore.RED, "  [Error] No downloadable options could be found.")
    return page_title, options

def get_links_from_series_page(url):
    c_print(Fore.CYAN, "[Step 2 - Series] Finding all episodes from the list page...")
    soup = get_soup(url)
    if not soup: return {}
    episode_links = {}
    all_episodes = soup.find_all('h3')
    for episode_tag in all_episodes:
        link_tag = episode_tag.find('a')
        if link_tag and link_tag.get('href'):
            ep_name = link_tag.text.strip()
            episode_links[ep_name] = urljoin(url, link_tag['href'])
    if not episode_links: c_print(Fore.RED, "  [Error] Could not find any episode links.")
    return episode_links

def process_download_chain(initial_url, is_movie=False):
    # This function now correctly handles both movie and series links from step 2 onwards.
    hshare_url = initial_url
    if is_movie:
        c_print(Fore.CYAN, "[Step 2 - Movie] Looking for 'Get Links' button...")
        soup = get_soup(initial_url)
        if not soup: return None
        get_links_button = soup.select_one("a.get-link-btn, a.btn, button.btn")
        if not get_links_button:
            c_print(Fore.RED, "  [Error] Could not find 'Get Links' button.")
            return None
        hshare_url = urljoin(initial_url, get_links_button['href'])
    
    c_print(Fore.CYAN, "[Step 3] Navigating to hshare...")
    soup = get_soup(hshare_url)
    if not soup: return None
    hpage_button = soup.find("a", string="HPage")
    if not hpage_button:
        c_print(Fore.RED, "  [Error] Could not find 'HPage' button.")
        return None
    hcloud_url = urljoin(hshare_url, hpage_button['href'])
    
    c_print(Fore.CYAN, "[Step 4] Navigating to hcloud...")
    soup = get_soup(hcloud_url)
    if not soup: return None
    server_button = soup.find("a", string="Server 1")
    if not server_button:
        c_print(Fore.RED, "  [Error] Could not find 'Server 1' button.")
        return None
        
    c_print(Fore.GREEN, "[Success] Final download link extracted!")
    return server_button['href']

# --- Main Application ---
def run_session(config):
    """Runs a single, complete scraping session with robust input and looping."""
    c_print(Style.BRIGHT + Fore.WHITE, "\n--- New Scraping Session ---")

    # --- 1. Get User Input (with validation loops) ---
    url = input(Fore.YELLOW + "Enter the JoshMovies URL to scrape: " + Style.RESET_ALL)

    while True:
        content_type = input(Fore.YELLOW + "Is this a [1] Movie or [2] Series/Anime?: " + Style.RESET_ALL)
        if content_type in ['1', '2']: break
        c_print(Fore.RED, "  Invalid input. Please enter 1 or 2.")

    # Get and validate output folder
    if config.get('output_folder') and os.path.isdir(config.get('output_folder')):
        if input(Fore.YELLOW + f"Use saved directory '{config['output_folder']}'? [Y/n]: " + Style.RESET_ALL).lower() == 'n':
            config['output_folder'] = None
    if not config.get('output_folder') or not os.path.isdir(config.get('output_folder')):
        while True:
            folder_path = input(Fore.YELLOW + "Enter the full path for your output folder: " + Style.RESET_ALL)
            if os.path.isdir(folder_path):
                config['output_folder'] = folder_path
                break
            c_print(Fore.RED, "  That is not a valid directory. Please try again.")

    # Get output mode and filename
    while True:
        output_mode = input(Fore.YELLOW + "Choose action: [1] Download Files  [2] Save Links to .md file: " + Style.RESET_ALL)
        if output_mode in ['1', '2']: break
        c_print(Fore.RED, "  Invalid input. Please enter 1 or 2.")
        
    if output_mode == '2':
        if input(Fore.YELLOW + f"Save to '{config['md_filename']}'? [Y/n]: " + Style.RESET_ALL).lower() == 'n':
            config['md_filename'] = input(Fore.YELLOW + "Enter new filename for links: " + Style.RESET_ALL)
    
    save_config(config)

    # --- 2. Scrape Main Page & Prepare ---
    page_title, options = get_options_from_main_page(url)
    if not options: return config
    page_title_clean = re.sub(r'Download|[|] JoshMovies', '', page_title).strip()

    # --- 3. Main Decision Logic ---
    if content_type == '2': # SERIES WORKFLOW (with "next quality" loop)
        remaining_options = options.copy()
        while remaining_options:
            print("\n" + Fore.WHITE + Style.BRIGHT + "Please choose one of the available series/seasons:")
            [print(f"  - {key}") for key in remaining_options]
            
            while True: # Input validation loop for choice
                choice_key = input(Fore.YELLOW + "\nType your choice exactly as it appears above: " + Style.RESET_ALL)
                if choice_key in remaining_options: break
                c_print(Fore.RED, "  Invalid choice. Please try again.")
            
            # Process the chosen quality
            episode_links = get_links_from_series_page(remaining_options[choice_key])
            if episode_links:
                num_episodes = len(episode_links)
                while True: # Input validation loop for range
                    range_input = input(Fore.YELLOW + f"Found {num_episodes} eps. Enter range (e.g., 1-5) or 'A' for All: " + Style.RESET_ALL).lower()
                    if range_input == 'a': start, end = 1, num_episodes; break
                    try:
                        start, end = map(int, range_input.split('-'))
                        if 1 <= start <= end <= num_episodes: break
                        else: c_print(Fore.RED, "  Range is invalid. Please ensure start <= end and within bounds.")
                    except ValueError: c_print(Fore.RED, "  Invalid format. Please use '1-5' or 'a'.")
                
                for i, (ep_name, url) in enumerate(list(episode_links.items())):
                    if start <= i + 1 <= end:
                        c_print(Style.BRIGHT, f"\n--- Processing '{ep_name}' ---")
                        final_link = process_download_chain(url, is_movie=False)
                        if final_link:
                            title = f"{page_title_clean} - {choice_key} - {ep_name}"
                            if output_mode == '1': download_file(final_link, config['output_folder'], f"{re.sub(r'[^a-zA-Z0-9 ._-]', '', title)}.mp4")
                            else: save_link_to_file(final_link, config['output_folder'], config['md_filename'], title)
            
            del remaining_options[choice_key] # Remove processed option
            if not remaining_options:
                c_print(Fore.GREEN, "\nAll available qualities for this series have been processed.")
                break
            if input(Fore.YELLOW + "\nProcess another quality for this series? [Y/n]: " + Style.RESET_ALL).lower() != 'y':
                break

    else: # MOVIE WORKFLOW
        while True: # Input validation loop for choice
            print("\n" + Fore.WHITE + Style.BRIGHT + "Please choose one of the following movie versions:")
            [print(f"  - {key}") for key in options]
            choice_input = input(Fore.YELLOW + "\nType your choice exactly, or 'A' for All: " + Style.RESET_ALL)
            
            tasks_to_process = []
            if choice_input.lower() == 'a':
                tasks_to_process = list(options.keys())
                c_print(Fore.GREEN, f"\nUser selected 'All'. Preparing to process {len(tasks_to_process)} links.")
                break
            elif choice_input in options:
                tasks_to_process.append(choice_input)
                break
            else:
                c_print(Fore.RED, "  Invalid choice. Please try again.")

        for task_key in tasks_to_process:
            c_print(Style.BRIGHT, f"\n--- Processing '{task_key}' ---")
            final_link = process_download_chain(options[task_key], is_movie=True)
            if final_link:
                title = task_key
                if output_mode == '1': download_file(final_link, config['output_folder'], f"{re.sub(r'[^a-zA-Z0-9 ._-]', '', title)}.mp4")
                else: save_link_to_file(final_link, config['output_folder'], config['md_filename'], title)
            
    return config

if __name__ == "__main__":
    c_print(Fore.GREEN + Style.BRIGHT, "############################################\n#      JoshMovies Scraper & Downloader     #\n############################################")
    
    app_config = load_config()
    while True:
        try:
            app_config = run_session(app_config)
            if input(Fore.YELLOW + "\nScrape another URL? [Y/n]: " + Style.RESET_ALL).lower() == 'n': break
        except (KeyboardInterrupt): break
        except Exception as e:
            c_print(Fore.RED, f"\nAn unexpected error occurred: {e}\nPlease report this bug and restart the tool.")
            
    c_print(Style.BRIGHT, "\nThank you for using the tool. Goodbye!")
