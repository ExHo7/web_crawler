import argparse
import csv
import json
import logging
import random
import time
import aiohttp
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from logging.handlers import RotatingFileHandler
from colorama import Fore, init
import pandas as pd
from fake_useragent import UserAgent
import re
import sys
import os
from tqdm.asyncio import tqdm
from urllib.robotparser import RobotFileParser
from tenacity import retry, wait_exponential, stop_after_attempt
from threading import Lock
import gc
import warnings
from art import text2art

# Initialisation de Colorama pour les sorties colorées
init(autoreset=True)

# Pre-compiling regex patterns for filtering content
unwanted_patterns = re.compile(r'(Posted On|By|Next|Previous|Comments)', re.IGNORECASE)

# Configuration du logger avec rotation des fichiers logs
def configure_logger(log_level=logging.INFO):
    log_handler = RotatingFileHandler('webcrawler.log', maxBytes=5 * 1024 * 1024, backupCount=3)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(log_handler)
    logger.setLevel(log_level)
    return logger

logger = configure_logger()

# Suppression des avertissements inutiles
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# Gestion du User Agent avec une solution de secours
try:
    ua = UserAgent()
except Exception:
    ua = None
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                 '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def random_delay(retry=0):
    """Ajoute un délai avec backoff exponentiel pour éviter le throttling."""
    base = random.uniform(1, 3)
    delay = min(base * (2 ** retry), 60)  # Limiter le délai à 60 secondes
    time.sleep(delay)

class WebCrawler:
    """Classe principale pour le web crawler."""

    def __init__(self, max_workers=5, respect_robots_txt=True):
        self.max_workers = max_workers
        self.respect_robots_txt = respect_robots_txt
        self.visited_urls = set()
        self.lock = Lock()

    def validate_url(self, url):
        """Valide la structure d'une URL donnée."""
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])

    def filter_content(self, elements):
        """Filtre le contenu et supprime les motifs de texte indésirables."""
        return [self.clean_text(el.get_text()) for el in elements
                if el.get_text().strip() and not unwanted_patterns.search(el.get_text())]

    def clean_text(self, text):
        """Nettoie le texte en supprimant les espaces inutiles et les caractères spéciaux."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def is_allowed(self, url, user_agent='*'):
        """Vérifie si le scraping est autorisé selon robots.txt."""
        if not self.respect_robots_txt:
            return True
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            return rp.can_fetch(user_agent, url)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de robots.txt pour {url}: {e}")
            return False
    
    async def scrape_page(self, session, url, max_retries=3):
        """Scrape une page web de façon asynchrone et extrait le contenu utile."""
        if not self.is_allowed(url):
            logger.info(f"L'accès à {url} est interdit par robots.txt.")
            return None

        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Scraping URL: {url}")

                async with session.get(url, timeout=10) as response:
                    content_type = response.headers.get('Content-Type', '').lower()
                    parser = 'xml' if 'xml' in content_type else 'lxml'

                    text = await response.text()

                    soup = BeautifulSoup(text, parser)
                    titles = self.filter_content(soup.find_all(re.compile('^h[1-6]$')))
                    paragraphs = self.filter_content(soup.find_all(['p', 'div', 'section', 'article', 'span']))
                    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                             if self.validate_url(urljoin(url, a['href']))]
                    images = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]

                    result = {
                        "url": url,
                        "titles": titles,
                        "paragraphs": paragraphs,
                        "links": links,
                        "images": images,
                    }

                    gc.collect()
                    return result

            except Exception as e:
                logger.error(f"Erreur inattendue lors du scraping de {url}: {e}")
                retry_count += 1

        return None

    async def scrape_urls_parallel(self, urls, output_path, format_choice):
        """Scrape les URLs en parallèle en utilisant asyncio."""
        is_first = True
        async with aiohttp.ClientSession(headers={'User-Agent': ua.random if ua else user_agent}) as session:
            tasks = [self.scrape_page(session, url) for url in urls]
            for result in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scraping"):
                data = await result
                if data:
                    await self.save_result(data, output_path, format_choice, is_first)
                    is_first = False
            if format_choice == "json":
                await self.finalize_json(output_path)
            else:
                print(Fore.GREEN + f"Résultats enregistrés dans {output_path}")

    async def save_result(self, result, output_path, format_choice, is_first=False):
        """Enregistre un résultat individuel dans le format choisi."""
        try:
            with self.lock:
                if format_choice == "csv":
                    file_exists = os.path.isfile(output_path)
                    mode = 'a' if file_exists else 'w'
                    fieldnames = result.keys()
                    with open(output_path, mode=mode, newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(result)
                elif format_choice == "json":
                    mode = 'a'
                    with open(output_path, mode=mode, encoding='utf-8') as f:
                        if is_first:
                            f.write("[\n")
                        else:
                            f.write(",\n")
                        json.dump(result, f, indent=4, ensure_ascii=False)
                else:
                    logger.error(f"Format de sortie non supporté: {format_choice}")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du résultat: {e}")

    async def finalize_json(self, output_path):
        """Finalise le fichier JSON en fermant le tableau."""
        try:
            with self.lock:
                with open(output_path, mode='a', encoding='utf-8') as f:
                    f.write("\n]")
            print(Fore.GREEN + f"Résultats enregistrés dans {output_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la finalisation du fichier JSON: {e}")

    def load_urls_from_file(self, file_path):
        """Charge les URLs à partir d'un fichier (CSV ou JSON)."""
        urls = []
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                if 'url' in df.columns:
                    urls = df['url'].dropna().tolist()
                else:
                    logger.error(f"Aucune colonne 'url' trouvée dans {file_path}")
            elif file_path.endswith('.json'):
                with open(file_path, mode='r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        urls = [url for url in data if self.validate_url(url)]
                    elif isinstance(data, dict) and 'url' in data:
                        urls = [data['url']] if self.validate_url(data['url']) else []
            else:
                logger.error(f"Format de fichier non supporté: {file_path}")
            logger.info(f"{len(urls)} URLs valides chargées depuis {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des URLs depuis le fichier: {e}")
        return urls

# Use aiohttp session when scraping single URLs outside of the class
async def scrape_single_url(crawler, url):
    async with aiohttp.ClientSession(headers={'User-Agent': ua.random if ua else user_agent}) as session:
        result = await crawler.scrape_page(session, url)
        return result

def main():
    print(Fore.LIGHTYELLOW_EX + text2art("WEB CRAWLER"))

    parser = argparse.ArgumentParser(description='Web Crawler')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL à scraper')
    group.add_argument('--file', help='Chemin vers le fichier contenant les URLs')
    parser.add_argument('--output', help='Nom du fichier de sortie (sans extension)', required=True)
    parser.add_argument('--format', help='Format de sauvegarde des résultats (csv/json)', choices=['csv', 'json'], default='csv')
    parser.add_argument('--workers', help='Nombre de threads pour le scraping parallèle', type=int, default=5)
    parser.add_argument('--ignore-robots', help='Ignorer les directives de robots.txt', action='store_true')
    parser.add_argument('--log-level', help='Niveau de logging', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    args = parser.parse_args()

    # Set logging level based on user input
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    configure_logger(log_level)

    crawler = WebCrawler(max_workers=args.workers, respect_robots_txt=not args.ignore_robots)
    output_path = f"{args.output}.{args.format}"

    if args.file:
        urls = crawler.load_urls_from_file(args.file)
        if not urls:
            print(Fore.RED + "Aucune URL valide n'a été trouvée dans le fichier.")
            sys.exit(1)
        asyncio.run(crawler.scrape_urls_parallel(urls, output_path, args.format))
    elif args.url:
        if crawler.validate_url(args.url):
            result = asyncio.run(scrape_single_url(crawler, args.url))  # Now calling the correct function
            if result:
                asyncio.run(crawler.save_result(result, output_path, args.format, is_first=True))
                if args.format == "json":
                    asyncio.run(crawler.finalize_json(output_path))
                else:
                    print(Fore.GREEN + f"Résultats enregistrés dans {output_path}")
            else:
                print(Fore.RED + "Aucun résultat à enregistrer.")
        else:
            print(Fore.RED + "L'URL saisie n'est pas valide. Veuillez entrer une URL valide.")
    else:
        print(Fore.RED + "Veuillez spécifier une URL avec --url ou un fichier avec --file.")
        sys.exit(1)

if __name__ == "__main__":
    main()

