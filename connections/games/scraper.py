import requests
from bs4 import BeautifulSoup
import logging
from pydantic import BaseModel, Field
from typing import List, Optional
from DataModels import WordGroups, ConnectionsEntry


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NYTConnectionsScraper:
    """
    A scraper for extracting NYT Connections answers from the archive page.
    """

    def __init__(self):
        self.url = "https://tryhardguides.com/nyt-connections-answers/"
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def get_page_content(self) -> Optional[BeautifulSoup]:
        """
        Fetch the webpage content and return a BeautifulSoup object.

        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        try:
            logger.info(f"Fetching content from {self.url}")
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            logger.info("Successfully parsed HTML content")
            return soup

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching webpage: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def extract_connections_list(self, soup: BeautifulSoup) -> List[str]:
        try:
            target_heading = soup.find(
                "h2",
                {"class": "wp-block-heading"},
                string="NYT Connections Answers Archive",
            )

            logger.info("Found the target heading")

            ul_element = target_heading.find_next("ul")

            connection_games_texts = ul_element.find_all("li")
            logger.info(f"Found {len(connection_games_texts)} list items")

            connections_list = []

            for li in connection_games_texts:
                word_group_texts = li.find_all("li")
                if len(word_group_texts) != 0:
                    groups = []
                    for i in range(4):
                        words = (
                            word_group_texts[i]
                            .get_text(strip=True)
                            .split("- ")[1]
                            .split(", ")
                        )
                        if len(words) == 4:
                            word = WordGroups(
                                connection=word_group_texts[i]
                                .get_text(strip=True)
                                .split("- ")[0],
                                difficulty=i + 1,
                                words=words,
                            )
                            groups.append(word)

                    if len(groups) == 4:
                        connections_list.append(
                            ConnectionsEntry(
                                id=int(li.get_text(strip=True).split()[2]),
                                groups=groups,
                            )
                        )

            logger.info(f"Extracted {len(connections_list)} connections entries")
            return connections_list

        except Exception as e:
            logger.error(f"Error extracting connections list: {e}")
            return []

    def scrape_connections(self) -> List[str]:
        soup = self.get_page_content()
        if not soup:
            return []

        connections = self.extract_connections_list(soup)
        return connections

    def print_connections(self, connections: List[str]) -> None:
        if not connections:
            print("No connections found.")
            return

        print(f"\nFound {len(connections)} NYT Connections entries:")
        print("-" * 50)
        for i, connection in enumerate(connections, 1):
            print(f"{i}. {connection}")
        print("-" * 50)


def main():
    scraper = NYTConnectionsScraper()
    connections = scraper.scrape_connections()
    # scraper.print_connections(connections)

    # Optional: Return the data for further processing
    return connections


if __name__ == "__main__":
    connections = main()
    with open("connections/games/AllConnections.json", "w") as f:
        import json

        f.write(json.dumps([entry.dict() for entry in connections], indent=4))
