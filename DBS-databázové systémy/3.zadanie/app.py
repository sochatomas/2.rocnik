import flask
from flask import Flask
import os
import psycopg2
import simplejson

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False


def get_db_connection():

    conn = psycopg2.connect(
        host=os.getenv("DBIP"),
        database=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        port=os.getenv("DBPORT"))

    return conn

# zadanie 2
@app.route('/v1/health', methods=['GET'])
def api():
    conn = get_db_connection()
    cur = conn.cursor()

    prikazy = ("SELECT version();","SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")
    vypis = {}

    for prikaz in prikazy:
        cur.execute(prikaz)
        popis = cur.description[0].name
        odpoved = cur.fetchone()
        vypis[popis] = odpoved[0]

    vypis_all = {"pgsql": vypis}

    cur.close()
    conn.close()
    return flask.jsonify(vypis_all)


@app.route('/')
def hello():
    return "fungujem "


@app.route('/v1')
def almost():
    return "zadanie 1"


# zadanie 3

def vypis(prikaz,string, pocet_stlpcov):                # formatovanie vypisu pre /game_objectives a /abilities

    popis,odpoved,cur,conn = pripojenie(prikaz)
    matches = []
    actions = []

    player = vytvor_dict_player(popis, odpoved, matches)
    akt_match_id = odpoved[0][3]

    while len(odpoved) > 0:                             # prechadzanie vsetkych zaznamov
        akt_zaznam = odpoved.pop(0)

        if akt_zaznam[2] != akt_match_id:               # vytvorenie noveho zaznamu zapasov
            akt_match_id = akt_zaznam[2]
            actions = []
            match = {}

            for index in range(2, 4):                   # zaplnenie hodnot pre dany zapas
                key = popis[index].name
                match[key] = akt_zaznam[index]

            match[string] = actions                     # pridanie listu akcii do dict akt. zapasu
            matches.append(match)

        action = {}
        for index in range(4, pocet_stlpcov):           # vytvorenie novej akcie a nacitanie hodnot
            key = popis[index].name
            action[key] = akt_zaznam[index]
        actions.append(action)                          # pridanie do listu akcii

    cur.close()
    conn.close()
    return flask.jsonify(player)


def vytvor_dict_player(popis, odpoved, matches):        #vytvorenie dict hraca
    player = {
        popis[0].name: odpoved[0][0],
        popis[1].name: odpoved[0][1],
        "matches": matches
    }
    return player


def pripojenie(prikaz):                         #pripojenie sa na databazu
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(prikaz)
    popis = cur.description
    odpoved = cur.fetchall()

    return popis,odpoved,cur,conn



@app.route('/v2/patches/',methods=['GET'])
def patches():

    prikaz = ("with tabulka as( select name as patch_version, extract(EPOCH from release_date)::integer as patch_start_date,LEAD(extract(EPOCH from release_date)::integer,1)over (order by name) as patch_end_date from patches  p ) select patch_version,patch_start_date, patch_end_date,m.id as match_id,Round(m.duration::numeric/60,2)::real as duration from tabulka left join matches m on (m.start_time >= patch_start_date  and (m.start_time < patch_end_date or patch_end_date is NULL)) order by patch_version asc;")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    akt_verzia_patch = ''
    patches = []
    matches = []

    while len(odpoved) > 0:                             # prechadzanie vsetkych zaznamov
        akt_zaznam = odpoved.pop(0)

        if akt_zaznam[0] != akt_verzia_patch:           # vytvorenie noveho zaznamu
            akt_verzia_patch = akt_zaznam[0]
            matches = []
            patch = {                                   # vytvorenie noveho dict  pre patch
                popis[0].name: akt_zaznam[0],
                popis[1].name: akt_zaznam[1],
                popis[2].name: akt_zaznam[2],
                "matches": matches
            }
            patches.append(patch)

        if akt_zaznam[4] is not None:                   # vytvorenie noveho zaznamu pre zapas
            match = {
                popis[3].name: akt_zaznam[3],
                popis[4].name: akt_zaznam[4]
                     }
            matches.append(match)

    cur.close()
    conn.close()
    vypis_all = {"patches": patches}

    return simplejson.dumps(vypis_all)


@app.route('/v2/players/<player_id>/game_exp/', methods=['GET'])
def game_exp(player_id):

    prikaz = ("select p.id, Coalesce(p.nick,'unknown') as player_nick, m.id as match_id, h.localized_name as hero_localized_name, coalesce(mpd.xp_hero,0)+coalesce(mpd.xp_creep,0)+coalesce(mpd.xp_other,0)+coalesce(mpd.xp_roshan,0) as experiences_gained,Round(m.duration::numeric/60,2)::real as match_duration_minutes, level as level_gained,CASE when  player_slot <5 then m.radiant_win else not m.radiant_win end as winner from players p left join matches_players_details mpd on p.id = mpd.player_id join heroes h on h.id = mpd.hero_id left join matches m on m.id = mpd.match_id where p.id =" + player_id + "order by m.id")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    matches = []
    player = vytvor_dict_player(popis, odpoved, matches)

    while len(odpoved) > 0:                     # prechadzanie vsetkych zaznamov
        akt_zaznam = odpoved.pop(0)

        if akt_zaznam[2] is not None:           # vytvorenie noveho zaznamu pre zapas
            match = {}
            for index in range(2,8):            # naplnenie hodnot v dict. akt. zapasu
                key = popis[index].name
                match[key] = akt_zaznam[index]
            matches.append(match)

    cur.close()
    conn.close()
    return flask.jsonify(player)


@app.route('/v2/players/<player_id>/game_objectives/', methods=['GET'])
def game_objectives(player_id):

    prikaz = ("select p.id, Coalesce(p.nick,'unknown') as player_nick,m.id as match_id,h.localized_name as hero_localized_name, coalesce(go.subtype,'NO_ACTION')as hero_action, count(*) from players p left join matches_players_details mpd on p.id = mpd.player_id join heroes h on h.id = mpd.hero_id left join matches m on m.id = mpd.match_id left join game_objectives go on mpd.id = match_player_detail_id_1 where p.id =" + player_id + " group by hero_action,p.id,h.localized_name,m.id order by match_id")
    return vypis(prikaz,"actions",6)


@app.route('/v2/players/<player_id>/abilities/', methods=['GET'])
def abilities(player_id):

    prikaz = ("select p.id, Coalesce(p.nick,'unknown')as player_nick, m.id as match_id, h.localized_name as hero_localized_name, a.name as ability_name, count(a.name), MAX(au.level) as upgrade_level from players p join matches_players_details mpd on p.id = mpd.player_id join heroes h on hero_id = h.id join matches m on match_id = m.id left join ability_upgrades au on match_player_detail_id = mpd.id left join abilities a on ability_id = a.id where p.id = " + player_id + " group by a.name,p.id,p.nick,h.localized_name,m.id order by m.id")
    return vypis(prikaz,"abilities",7)


if __name__ == '__main__':
    app.run()


