from bs4 import BeautifulSoup
import re
from config import PREFIX


def extract_header_label(raw_label):
    return raw_label.find("span").text.strip()


def extract_header_label_by_regex(soup: BeautifulSoup, regex):
    result = soup.find(lambda tag: (tag.name == "li" and
                                    re.match(fr"[\s\S]*{regex}", tag.get_text()) is not None))
    return result.find("span").text.strip() if result is not None else None


def link_formatter(link):
    return f"{PREFIX}{link.replace('profil', 'leistungsdatendetails')}/saison/2024"


def extract_age(raw_age):
    return int(raw_age.split("(")[-1].strip()[:-1])


def extract_height(raw_height):
    return float(raw_height.split()[0].replace(",", ".").strip())


def extract_club_country(raw_country):
    return (raw_country.strip().capitalize().replace(" ", "_")
            .replace("ü", "u")
            .replace(",", "")
            .replace("'", "_"))


def extract_national_team(raw_country):
    return (re.split(r"u\d\d", raw_country.strip()
                     .capitalize())[0]
            .strip()
            .replace(" ", "_")
            .replace("ü", "u")
            .replace(",", "")
            .replace("'", "_"))


def extract_position(raw_position):
    return raw_position.strip().lower().replace(" ", "-")


def extract_captain(raw_captain):
    return str(raw_captain).upper()


def extract_cost(raw_cost):
    return float(raw_cost.split()[0][1:-1])


def extract_minutes(raw_minutes):
    return int(raw_minutes[:-1].replace(".", "")) if len(raw_minutes) else None


def extract_games_amount(raw_games_amount):
    stripped = raw_games_amount.strip()
    return int(stripped) if len(stripped) else None


def extract_goals_amount(raw_goals_amount):
    stripped = raw_goals_amount.strip()
    return int(stripped) if len(stripped) and stripped != '-' else None
