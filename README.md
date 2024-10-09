
# 🚀 Async Web Scraper with Aiohttp & BeautifulSoup 🕸️

Welcome to the **Async Web Scraper** project! This Python-based web scraper is designed to efficiently scrape web content using asynchronous requests powered by `aiohttp`, and beautiful HTML parsing via `BeautifulSoup`. 

It's fast ⚡, easy to use 🛠️, and highly customizable 🔧!

---

## 🛠️ Features

- **Asynchronous Scraping**: Uses `aiohttp` for non-blocking requests to scrape multiple websites concurrently. Scrape like a pro and save time! ⏱️
- **BeautifulSoup Integration**: Efficient HTML parsing to extract data from the scraped web pages with ease! 🍜
- **User-Agent Randomization**: Avoid blocks by websites with the help of `fake_useragent`. Be anonymous! 🕶️
- **Parallel Scraping**: Thanks to `asyncio`, scrape hundreds of URLs in parallel without breaking a sweat! 🧠
- **Progress Bars**: Keep track of your scraping progress with a fun, visual progress bar (courtesy of `tqdm`) 🎯.
- **Customizable Output**: Save your results in either CSV or JSON format with a single option! 📜
- **Retry Mechanism**: Integrated retry mechanism using `tenacity` to handle transient issues during scraping 🛡️.

---

## 🎯 How It's Built

This project uses several key Python libraries to perform efficient and flexible web scraping:

1. **aiohttp**: For handling asynchronous HTTP requests 🌐.
2. **BeautifulSoup**: For parsing and extracting useful data from the HTML of web pages 🍜.
3. **tenacity**: To retry failed scraping attempts with exponential backoff ⏳.
4. **pandas**: For working with CSV files when saving scraped data in tabular format 📊.
5. **tqdm**: To show progress bars during scraping, keeping you informed and motivated 🚀.
6. **fake_useragent**: For rotating user agents, so websites won’t detect you as a bot 🤖.

---

## 🎛️ Command-Line Usage

This scraper comes with several handy options you can use. Here’s how you can run it:

```bash
python web_crawler.py --url <URL> --output <filename> --format <csv/json>
```

### 💡 Available Options

- `--url <URL>`: Specify the single URL you want to scrape 🌍.
- `--file <path>`: Provide a file containing multiple URLs to scrape (CSV or JSON) 📂.
- `--output <filename>`: Define the output file name (without extension) where your scraped data will be saved 📝.
- `--format <csv/json>`: Choose whether you want your output in CSV or JSON format 🗂️.
- `--workers <int>`: Specify the number of asynchronous workers (default is 5) 🧑‍🔧.
- `--ignore-robots`: Ignore the `robots.txt` restrictions and scrape all pages 🦾.
- `--log-level <DEBUG/INFO/WARNING/ERROR>`: Set the logging verbosity level (default is INFO) 📜.

### 🕹️ Example Usage

To scrape a single website and save the output as a JSON file:

```bash
python web_crawler.py --url https://example.com --output results --format json
```

To scrape multiple websites listed in a CSV file with 10 workers:

```bash
python web_crawler.py --file urls.csv --output results --format csv --workers 10
```

To ignore `robots.txt` and be a true web scraping rebel:

```bash
python web_crawler.py --url https://example.com --output results --ignore-robots
```

---

## 🔧 Installation

### 1. Setting Up a Python Virtual Environment (Highly Recommended)

It's a good practice to run the scraper inside a virtual environment to avoid conflicts with other Python projects or system packages.

### 2. Clone the Repository

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-repo/web-crawler.git
   ```

2. Navigate to the project folder:

   ```bash
   cd web-crawler
   ```

3. Install the required libraries using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Requirements

Here's a list of the main dependencies used in this project:

```bash
aiohttp==3.10.9
beautifulsoup4==4.12.3
colorama==0.4.6
fake_useragent==1.5.1
pandas==2.2.3
tenacity==9.0.0
tqdm==4.66.5
```

---

## 🌟 Fun Features

- **Progressive Scraping**: Watch a real-time progress bar while scraping! 🎉
- **Rotating User-Agents**: Change your user-agent with every request for maximum stealth mode! 🕵️‍♂️.
- **Custom Logging**: Control the verbosity of logging to see what’s happening under the hood 🖥️.

---

## 🤔 Got Questions?

If you run into any issues or have questions, feel free to reach out via [GitHub Issues](https://github.com/your-repo/web-crawler/issues) or open a pull request! Let's make scraping fun and easy, together! 💡

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### 🚀 Now go forth and scrape the web responsibly! 🌍🕸️
