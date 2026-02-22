import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from abc import ABC, abstractmethod
from typing import List, Dict


# Абстрактний клас
class JobScraper(ABC):
    def __init__(self, source_name: str, base_url_template: str):
        self.source_name = source_name
        self.base_url_template = base_url_template
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_html(self, query: str) -> str | None:
        url = self.base_url_template.format(query=query)
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Failed to access {self.source_name}: {e}")
            return None

    @abstractmethod
    def parse(self, html: str) -> List[Dict[str, str]]:
        pass

    def scrape(self, query: str) -> pd.DataFrame:
        print(f"[{self.source_name}] Fetching data...")
        html = self.fetch_html(query)

        if not html:
            return pd.DataFrame()  # Пустий dataframe

        parsed_data = self.parse(html)
        for item in parsed_data:
            item['Source'] = self.source_name

        return pd.DataFrame(parsed_data)


class DouScraper(JobScraper):
    def __init__(self):
        super().__init__(source_name="DOU.ua", base_url_template="https://jobs.dou.ua/vacancies/?search={query}")

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('li', class_='l-vacancy')
        data = []

        for card in cards:
            title = card.find('a', class_='vt')
            company = card.find('a', class_='company')
            salary = card.find('span', class_='salary')
            data.append({
                "Title": title.text.strip().replace('\xa0', ' ') if title else "Не вказано",
                "Company": company.text.strip().replace('\xa0', ' ') if company else "Не вказано",
                "Salary": salary.text.strip().replace('\xa0', ' ') if salary else "Не вказано"
            })
        return data


class WorkUaScraper(JobScraper):
    def __init__(self):
        super().__init__(source_name="Work.ua", base_url_template="https://www.work.ua/jobs-{query}/")

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.find_all('div', class_='card-hover')
        data = []

        for card in cards:
            title = card.find('h2')
            company_span = card.find('span', class_='strong-600')
            salary = "Не вказано"

            for b_tag in card.find_all('b'):
                if '₴' in b_tag.text or 'грн' in b_tag.text or '$' in b_tag.text:
                    salary = b_tag.text.strip().replace('\u202f', ' ')
                    break
            data.append({
                "Title": title.text.strip().replace('\xa0', ' ') if title else "Не вказано",
                "Company": company_span.text.strip() if company_span else "Не вказано",
                "Salary": salary
            })
        return data


def main():
    search_term = "mobile developer"
    print(f"\nSearching for jobs matching: '{search_term}'\n")
    scrapers = [WorkUaScraper(), DouScraper()]
    all_dataframes = []

    for scraper in scrapers:
        df = scraper.scrape(search_term)
        if not df.empty:
            all_dataframes.append(df)
        time.sleep(2)  # Пауза між сайтами

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\nSuccessfully collected {len(final_df)} jobs!")
        pd.set_option('display.max_rows', None)
        print("\nResult:")
        print(final_df)
    else:
        print("Failed to collect data.")


if __name__ == "__main__":
    main()
