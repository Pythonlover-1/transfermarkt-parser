import csv
import time
from fake_useragent import UserAgent
import asyncio
import aiohttp
import os
from utils import *
from re import compile
from config import PREFIX, PLAYERS_AMOUNT, PLAYERS_ON_PAGE, OUTPUT_DIR
from tqdm import tqdm

# We set headers for parsing (without it the site would not provide data)
agent = UserAgent()
headers = {
    "User-Agent":
        agent.random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US;q=0.8,en;q=0.7"
}


def extract_players_link(page_soup: BeautifulSoup):
    """
    Extracting links to football players from the page code
    :param page_soup: BeautifulSoup object for the page with football players
    :return: links generator for football player profile
    """
    extracted = page_soup.find_all("td", class_="hauptlink")
    for link_obj in extracted[::2]:
        yield link_obj.find("a")["href"]


async def get_player_information(session: aiohttp.ClientSession, player_link: str, result_list: list):
    """
    Get player information from player page
    :param session: session used to connect to the site
    :param player_link: link on player page
    :param result_list: the list in which the result will be placed
    :return:
    """
    async with session.get(player_link, headers=headers) as response:
        player_response_text = await response.text()
    player_soup = BeautifulSoup(player_response_text, "lxml")
    age = extract_header_label_by_regex(player_soup, r"[Aa]ge:")
    height = extract_header_label_by_regex(player_soup, r"[Hh]eight:")
    position = extract_header_label_by_regex(player_soup, "[Pp]osition:")
    nation_team = extract_header_label_by_regex(player_soup, r"[Cc]urrent international:")
    if nation_team is None:
        nation_team = extract_header_label_by_regex(player_soup, "[Cc]itizenship:")
    captain = player_soup.find("img", {"title": compile("Captain")}) is not None
    club_country = player_soup.find("div", class_="data-header__club-info").find("img",
                                                                                 class_="flaggenrahmen")
    club_country = club_country if club_country is None else club_country["title"].strip()
    cost = player_soup.find("a", class_="data-header__market-value-wrapper").text.strip()
    table = player_soup.find("div", {"id": "yw1"})
    if table.find("span", class_="empty") is not None:
        table = None
    minutes_in_game = table if table is None else table.find_all("td", class_="rechts")[1].text
    if table is None:
        games_count, goals_count = None, None
    else:
        games_count, goals_count, *_ = table.find_all("td", class_="zentriert")
        games_count = games_count.text
        goals_count = goals_count.text
    result_list.append((age, height, club_country, nation_team, position, captain, cost, minutes_in_game,
                        games_count, goals_count))


async def get_page_data(session: aiohttp.ClientSession, page_number: int, result_list: list):
    """
    :param session: session used to connect to the site
    :param page_number: page number to parse
    :param result_list: the list in which the result will be placed
    :return:
    """
    page_ref = f"{PREFIX}/detailsuche/spielerdetail/suche/51133918/page/{page_number}"
    async with session.get(page_ref, headers=headers) as response:
        response_text = await response.text()
    tasks = []
    page_soup = BeautifulSoup(response_text, "lxml")
    for player_link in extract_players_link(page_soup):
        task = get_player_information(session, link_formatter(player_link), result_list)
        tasks.append(task)
    await asyncio.gather(*tasks)


async def fill_player_list_from_page(page_number: int, result_list: list):
    """
    :param page_number: number of the page to parse
    :param result_list: the list in which the result will be placed
    :return:
    """
    async with aiohttp.ClientSession() as session:
        await get_page_data(session, page_number, result_list)


def parse_players(output_file="out_en.tsv", page_count=400):
    """
    :param output_file: name of output file
    :param page_count: number of pages to be parsed
    :return:
    """
    filename = f"{OUTPUT_DIR}/{output_file}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf8', newline='') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(["Age", "Height", "Club_country", "Nation_team", "Position",
                             "Captain", "Cost", "Minutes_in_game", "Games_count", "Goals_count"])
        players = []
        for i in tqdm(range(1, page_count + 1)):
            players.clear()
            for retr in range(5):
                try:
                    asyncio.run(fill_player_list_from_page(i, players))
                    break
                except Exception as e:
                    print(f"Error {repr(e)} on page: {i}")
                    print("-" * 50)
                    time.sleep(2.5)
            else:
                print("Error was not fixed...")
            tsv_writer.writerows(players)
            time.sleep(0.7)


def main():
    """
    Start parsing
    """
    page_amount = PLAYERS_AMOUNT // PLAYERS_ON_PAGE
    parse_players(page_count=page_amount)


if __name__ == "__main__":
    main()
