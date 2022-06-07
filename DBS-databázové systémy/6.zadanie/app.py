import psycopg2
from zadanie6 import *
from vypisy import *

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

    prikazy = ("SELECT version();", "SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")
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

def vypis(prikaz, string, pocet_stlpcov):  # formatovanie vypisu pre /game_objectives a /abilities

    popis, odpoved, cur, conn = pripojenie(prikaz)
    matches = []
    actions = []

    keys = []
    for key in popis:
        keys.append(key.name)

    player = vytvor_dict_player(keys, odpoved, matches)
    akt_match_id = odpoved[0][3]

    while len(odpoved) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = odpoved.pop(0)

        if akt_zaznam[2] != akt_match_id:  # vytvorenie noveho zaznamu zapasov
            akt_match_id = akt_zaznam[2]
            actions = []
            match = {}

            for index in range(2, 4):  # zaplnenie hodnot pre dany zapas
                key = keys[index]
                match[key] = akt_zaznam[index]

            match[string] = actions  # pridanie listu akcii do dict akt. zapasu
            matches.append(match)

        action = {}
        for index in range(4, pocet_stlpcov):  # vytvorenie novej akcie a nacitanie hodnot
            key = keys[index]
            action[key] = akt_zaznam[index]
        actions.append(action)  # pridanie do listu akcii

    cur.close()
    conn.close()
    return flask.jsonify(player)


def pripojenie(prikaz):  # pripojenie sa na databazu
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(prikaz)
    popis = cur.description
    odpoved = cur.fetchall()

    return popis, odpoved, cur, conn


@app.route('/v2/patches/', methods=['GET'])
def patches_v2():
    prikaz = (
        "with tabulka as( select name as patch_version, extract(EPOCH from release_date)::integer as patch_start_date,LEAD(extract(EPOCH from release_date)::integer,1)over (order by name) as patch_end_date from patches  p ) select patch_version,patch_start_date, patch_end_date,m.id as match_id,Round(m.duration::numeric/60,2)::real as duration from tabulka left join matches m on (m.start_time >= patch_start_date  and (m.start_time < patch_end_date or patch_end_date is NULL)) order by patch_version asc;")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    keys = []
    for key in popis:
        keys.append(key.name)

    vypis_all = patches_vypis(odpoved, keys)
    cur.close()
    conn.close()

    return simplejson.dumps(vypis_all)


@app.route('/v2/players/<player_id>/game_exp/', methods=['GET'])
def game_exp_v2(player_id):
    prikaz = (
                "select p.id, Coalesce(p.nick,'unknown') as player_nick, m.id as match_id, h.localized_name as hero_localized_name, coalesce(mpd.xp_hero,0)+coalesce(mpd.xp_creep,0)+coalesce(mpd.xp_other,0)+coalesce(mpd.xp_roshan,0) as experiences_gained,Round(m.duration::numeric/60,2)::real as match_duration_minutes, level as level_gained,CASE when  player_slot <5 then m.radiant_win else not m.radiant_win end as winner from players p left join matches_players_details mpd on p.id = mpd.player_id join heroes h on h.id = mpd.hero_id left join matches m on m.id = mpd.match_id where p.id =" + player_id + "order by m.id")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    keys = []
    for key in popis:
        keys.append(key.name)

    player = game_exp_vypis(odpoved, keys)

    cur.close()
    conn.close()
    return flask.jsonify(player)


@app.route('/v2/players/<player_id>/game_objectives/', methods=['GET'])
def game_objectives_v2(player_id):
    prikaz = (
                "select p.id, Coalesce(p.nick,'unknown') as player_nick,m.id as match_id,h.localized_name as hero_localized_name, coalesce(go.subtype,'NO_ACTION')as hero_action, count(*) from players p left join matches_players_details mpd on p.id = mpd.player_id join heroes h on h.id = mpd.hero_id left join matches m on m.id = mpd.match_id left join game_objectives go on mpd.id = match_player_detail_id_1 where p.id =" + player_id + " group by hero_action,p.id,h.localized_name,m.id order by match_id")
    return vypis(prikaz, "actions", 6)


@app.route('/v2/players/<player_id>/abilities/', methods=['GET'])
def abilities_v2(player_id):
    prikaz = (
                "select p.id, Coalesce(p.nick,'unknown')as player_nick, m.id as match_id, h.localized_name as hero_localized_name, a.name as ability_name, count(a.name), MAX(au.level) as upgrade_level from players p join matches_players_details mpd on p.id = mpd.player_id join heroes h on hero_id = h.id join matches m on match_id = m.id left join ability_upgrades au on match_player_detail_id = mpd.id left join abilities a on ability_id = a.id where p.id = " + player_id + " group by a.name,p.id,p.nick,h.localized_name,m.id order by m.id")
    return vypis(prikaz, "abilities", 7)


# zadanie 5
@app.route('/v3/matches/<match_id>/top_purchases/', methods=['GET'])
def top_purchases_v3(match_id):
    prikaz = (
                "with tabulka as( select item_id,i.name as i_name,hero_id,localized_name as h_name, count(*) as pocet, row_number() over(partition by hero_id order by count(*) desc, i.name) from matches m left join matches_players_details mpd on m.id = match_id left join purchase_logs pl on mpd.id = match_player_detail_id left join items i on i.id = pl.item_id left join heroes h on h.id = hero_id where match_id = " + match_id + " and ((player_slot < 5 and radiant_win = true) or (player_slot > 127 and radiant_win = false)) group by hero_id,localized_name,item_id,i.name order by hero_id, count(*) desc, i.name) select hero_id as id,h_name as name, pocet as count , item_id as id, i_name as name from tabulka where row_number <=5 order by hero_id")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    keys = []
    for key in popis:
        keys.append(key.name)

    player = top_purchases_vypis(match_id,prikaz,keys)

    cur.close()
    conn.close()
    return flask.jsonify(player)


@app.route('/v3/abilities/<ability_id>/usage/', methods=['GET'])
def ability_usage_v3(ability_id):
    prikaz = (
                "with tabulka as( select h.id,h.localized_name as h_name,a.name, case when Round(au.time::numeric/m.duration*100::numeric,5) < 10 then '0-9' when Round(au.time::numeric/m.duration*100::numeric,5) < 20 then '10-19' when Round(au.time::numeric/m.duration*100::numeric,5) < 30 then '20-29' when Round(au.time::numeric/m.duration*100::numeric,5) < 40 then '30-39' when Round(au.time::numeric/m.duration*100::numeric,5) < 50 then '40-49' when Round(au.time::numeric/m.duration*100::numeric,5) < 60 then '50-59' when Round(au.time::numeric/m.duration*100::numeric,5) < 70 then '60-69' when Round(au.time::numeric/m.duration*100::numeric,5) < 80 then '70-79' when Round(au.time::numeric/m.duration*100::numeric,5) < 90 then '80-89' when Round(au.time::numeric/m.duration*100::numeric,5) < 100 then '90-99' else '100-109' end as bucket, CASE when  player_slot < 5 then m.radiant_win else not m.radiant_win end as winner, count (*), row_number() over (partition by h.id,CASE when  player_slot < 5 then m.radiant_win else not m.radiant_win end order by count(*) desc) from abilities a left join ability_upgrades au on a.id = ability_id left join matches_players_details mpd on mpd.id = match_player_detail_id left join matches m on m.id = match_id left join heroes h on hero_id = h.id where ability_id = " + ability_id + " group by h.id,bucket, winner, a.name order by h_name, count desc) select name,id,h_name as name,winner,bucket,count from tabulka where row_number = 1 ")

    popis, odpoved, cur, conn = pripojenie(prikaz)
    keys = []
    for key in popis:
        keys.append(key.name)

    all = ability_usage_vypis(ability_id, odpoved, keys)
    cur.close()
    conn.close()
    return flask.jsonify(all)


@app.route('/v3/statistics/tower_kills/', methods=['GET'])
def tower_kills_v3():
    prikaz = (
        "with tabulka2 as(with tabulka as( select h.id,h.localized_name, match_id, hero_id, lead(hero_id,1) over (order by match_id,go.time ) as lead_hero_id,lead(match_id,1) over (order by match_id,go.time) as lead_match_id, row_number() over( order by match_id,hero_id,go.time) - row_number() over( order by match_id,go.time) as sequence_id from game_objectives go left join matches_players_details mpd on mpd.id = match_player_detail_id_1 left join heroes h on hero_id = h.id where subtype = 'CHAT_MESSAGE_TOWER_KILL' and match_player_detail_id_1 is  not null order by match_id,go.time,hero_id) select * ,count(*)+1 as tower_kills, row_number() over(partition by localized_name order by count(*)+1 desc) from tabulka where hero_id = lead_hero_id and match_id = lead_match_id group by tabulka.id,localized_name, match_id,hero_id,lead_hero_id, lead_match_id,sequence_id order by match_id) select id,localized_name as name,tower_kills from tabulka2 where row_number = 1 order by tower_kills desc, name asc")
    popis, odpoved, cur, conn = pripojenie(prikaz)

    keys = []
    for key in popis:
        keys.append(key.name)

    all = tower_kills_vypis(odpoved, keys)

    cur.close()
    conn.close()
    return flask.jsonify(all)



if __name__ == '__main__':
    app.run()
