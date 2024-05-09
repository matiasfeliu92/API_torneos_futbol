import json
import requests
from bs4 import BeautifulSoup
import datetime
import os


def get_matchs_links(url):
    page = requests.get(url)
    content = page.content
    soup = BeautifulSoup(content, "html.parser")
    matchs = soup.find_all(id="tablemarcador")
    match_links = []
    for match in matchs:
        matchs_tr = match.find_all("tr")
        for match_tr in matchs_tr:
            matchs_links_td = match_tr.find_all("td", class_="tdinfo")
            links = [
                link.find("a")["href"] for link in matchs_links_td if link.find("a")
            ]
            match_links.append(links[0])
    return match_links


def get_match_data(code, name, country, year, url):
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    match_div = soup.find_all(id="marcador")
    matchs_data = {}
    matchs_statistics = {}
    matchs_data["code"] = code
    matchs_data["name"] = name
    matchs_data["country"] = country
    matchs_data["year"] = year
    for match_ in match_div:
        date = [
            date.text.strip() for date in match_.find_all("span", class_="jor-date")
        ]
        matchs_data["date"] = date[0]

        status = [
            status.text.strip()
            for status in match_.find_all("span", class_="jor-status")
        ]
        matchs_data["status"] = status[0]

        div_home_team = match_.find_all("div", class_="team equipo1")
        home_team_names = [
            b.text
            for div in div_home_team
            for h2 in div.find_all("h2")
            for b in h2.find_all("b")
        ]
        matchs_data["home_team"] = home_team_names[0]

        div_away_team = match_.find_all("div", class_="team equipo2")
        away_team_names = [
            b.text
            for div in div_away_team
            for h2 in div.find_all("h2")
            for b in h2.find_all("b")
        ]
        matchs_data["away_team"] = away_team_names[0]

        matchs_data["link"] = url

        div_scores = soup.find("div", id="marcador")
        div_scores = (
            [div_score for div_score in div_scores.find_all("div", class_="resultado")]
            if div_scores
            else []
        )
        scores = []
        for div_scor in div_scores:
            sp = div_scor.text.strip()
            scores.append(sp)
        scores = "-".join(scores)
        matchs_data["score"] = scores

        ul_tournament_name = soup.find("ul", id="crumbs")
        li_tournament_name = (
            [li for li in ul_tournament_name if ul_tournament_name and "\n" not in li]
            if ul_tournament_name
            else []
        )
        tournament_name = (
            [a for a in li_tournament_name[1].find("a")]
            if len(li_tournament_name) > 0
            else []
        )
        matchs_data["tournament"] = (
            tournament_name[0] if len(tournament_name) > 0 else ""
        )

        all_spans = soup.find_all("span")
        local_scorers_list = []
        away_scorers_list = []
        local_yellow_card_list = []
        list_away_yellow_cards = []
        for sp in all_spans:
            if "left" in sp.get("class", []) and "minutos" not in sp.get("class", []):
                local_scorers = [
                    a.text
                    for a in sp.find_all("a")
                    if "Gol de" in sp.find("small").text and a != ""
                ]
                if len(local_scorers) > 0:
                    local_scorers_list.append(local_scorers[0])
                local_yellow_cards = [
                    a.text
                    for a in sp.find_all("a")
                    if "T. Amarilla" in sp.find("small").text and a != ""
                ]
                if len(local_yellow_cards) > 0:
                    local_yellow_card_list.append(local_yellow_cards[0])
            if "right" in sp.get("class", []) and "minutos" not in sp.get("class", []):
                away_scorers = [
                    a.text
                    for a in sp.find_all("a")
                    if "Gol de" in sp.find("small").text and a != ""
                ]
                if len(away_scorers) > 0:
                    away_scorers_list.append(away_scorers[0])
                away_yellow_cards = [
                    a.text
                    for a in sp.find_all("a")
                    if "T. Amarilla" in sp.find("small").text and a != ""
                ]
                if len(away_yellow_cards) > 0:
                    list_away_yellow_cards.append(away_yellow_cards[0])
        matchs_data["local_scorers"] = (
            ", ".join(local_scorers_list) if len(local_scorers_list) > 0 else ""
        )
        matchs_data["away_scorers"] = (
            ", ".join(away_scorers_list) if len(away_scorers_list) > 0 else ""
        )
        matchs_data["local_yellow_cards"] = (
            ", ".join(local_yellow_card_list) if len(local_yellow_card_list) > 0 else ""
        )
        matchs_data["away_yellow_cards"] = (
            ", ".join(list_away_yellow_cards) if len(list_away_yellow_cards) > 0 else ""
        )

        div_statistic_table = soup.select("div.contentitem table")
        statistic_table = (
            [table.find("tbody") for table in div_statistic_table]
            if div_statistic_table
            else []
        )
        tr_elements = [tr for table in statistic_table for tr in table.find_all("tr")]
        for tr in tr_elements:
            if tr.find_all("td")[1].find("h6").text.strip() == "Posesión del balón":
                matchs_statistics["local_ball_position"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_ball_position"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Goles":
                matchs_statistics["local_goals"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_goals"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Tiros a puerta":
                matchs_statistics["local_kicks_to_goals"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_kicks_to_goals"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Tiros fuera":
                matchs_statistics["local_outside_kicks"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_outside_kicks"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Total tiros":
                matchs_statistics["local_total_kicks"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_total_kicks"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Paradas del portero":
                matchs_statistics["local_shortcuts"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_shortcuts"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Saques de esquina":
                matchs_statistics["local_corner_kicks"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_corner_kicks"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Fueras de juego":
                matchs_statistics["local_offside"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_offside"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Tarjetas Rojas":
                matchs_statistics["local_red_cards"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_red_cards"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Asistencias":
                matchs_statistics["local_assists"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_assists"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Tiros al palo":
                matchs_statistics["local_crossbar_kicks"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_crossbar_kicks"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Lesiones":
                matchs_statistics["local_lesions"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_lesions"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Sustituciones":
                matchs_statistics["local_substitutions"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_substitutions"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Faltas":
                matchs_statistics["local_faults"] = tr.find_all("td")[0].text.strip() 
                matchs_statistics["away_faults"] = tr.find_all("td")[2].text.strip() 
            elif tr.find_all("td")[1].find("h6").text.strip() == "Penalti cometido":
                matchs_statistics["local_commited_penalties"] = tr.find_all("td")[
                    0
                ].text.strip() 
                matchs_statistics["away_commited_penalties"] = tr.find_all("td")[
                    2
                ].text.strip() 
    if matchs_statistics:
        matchs_data['statistics'] = matchs_statistics
    else:
        matchs_data['statistics'] = {'message': 'no statistics data'}
    print("----------------------------RETURN IN FUNCTION--------------------------------------")
    print(matchs_data)
    return matchs_data