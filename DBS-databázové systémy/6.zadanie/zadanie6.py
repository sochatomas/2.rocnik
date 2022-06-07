
import flask
import sqlalchemy
from sqlalchemy import cast, case, not_, text, extract
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy.sql.functions import coalesce, func
from modely import *
from vypisy import *
import simplejson

# zadanie 6
@app.route('/v4/patches/', methods=['GET'])
def patches_v4():
    tabulka = (db.session.query(patches.id.label("id"),patches.name.label("patch_version"),
            cast(extract('epoch',patches.release_date),sqlalchemy.Integer).label("patch_start_date"),
            func.lead(cast(extract('epoch',patches.release_date),sqlalchemy.Integer),1)
                .over(text("0"),patches.id).label("patch_end_date"),

    ).select_from(patches).
        subquery())

    result = (db.session.query(tabulka.c.patch_version,tabulka.c.patch_start_date,tabulka.c.patch_end_date,
                matches.id.label("match_id"),cast(func.round(cast(matches.duration,sqlalchemy.Numeric)/60,2),sqlalchemy.REAL).label("duration"))
               .select_from(tabulka)
    .join(matches,and_(matches.start_time >= tabulka.c.patch_start_date,or_(matches.start_time < tabulka.c.patch_end_date,tabulka.c.patch_end_date == None)),isouter=True)
               .order_by(tabulka.c.patch_version).all()
               )
    keys = ["patch_version", "patch_start_date", "patch_end_date", "match_id", "duration"]

    vypis_all = patches_vypis(result,keys)
    return simplejson.dumps(vypis_all)

@app.route('/v4/players/<player_id>/game_exp/', methods=['GET'])
def game_exp_v4(player_id):

    result = (db.session.query(
                players.id.label("id"), coalesce(players.nick, "unknown").label("player_nick"),
                matches.id.label("match_id"),heroes.localized_name.label("hero_localized_name"),
                coalesce(matches_players_details.xp_hero, 0) + coalesce(matches_players_details.xp_creep, 0) + coalesce(
                matches_players_details.xp_other, 0) + coalesce(matches_players_details.xp_roshan, 0)
                    .label("experiences_gained"),
                cast(func.round(cast(matches.duration, sqlalchemy.Numeric) / 60, 2), sqlalchemy.REAL)
                    .label("match_duration_minutes"),
                matches_players_details.level.label("level_gained"),
        case([(matches_players_details.player_slot < 5, matches.radiant_win), ], else_=not_(matches.radiant_win)).label(
            "winner"),
    ).select_from(players).
      join(matches_players_details).
      join(heroes).
      join(matches).
      filter(players.id == player_id).
      order_by(matches.id).all()
              )

    # sql = result.statement.compile(engine, compile_kwargs={"literal_binds": True})
    # res = db.session.execute(f'Explain {sql}')
    # results = res.mappings().all()
    # for instance in results:
    #     print(instance)

    keys = ["id","player_nick","match_id","hero_localized_name","experiences_gained","match_duration_minutes","level_gained","winner"]
    player = game_exp_vypis(result, keys)

    return flask.jsonify(player)


@app.route('/v4/players/<player_id>/game_objectives/', methods=['GET'])
def game_objectives_v4(player_id):

    result = (db.session.query(
                    players.id.label("id"), coalesce(players.nick, "unknown").label("player_nick"),
                    matches.id.label("match_id"),heroes.localized_name.label("hero_localized_name"),
                    coalesce(game_objectives.subtype,"NO_ACTION").label("hero_action"),
                    func.count(),
    )
              .select_from(players).
              join(matches_players_details).
              join(heroes).
              join(matches).
              join(game_objectives,game_objectives.match_player_detail_id_1 == matches_players_details.id,isouter=True).
              filter(players.id == player_id).
              group_by(text("hero_action"),players.id,text("hero_localized_name"),matches.id).
              order_by(matches.id).
              all())

    keys = ["id","player_nick","match_id","hero_localized_name","hero_action","count"]
    return vypis_v4(result,keys, "actions", 6)


@app.route('/v4/players/<player_id>/abilities/', methods=['GET'])
def abilities_v4(player_id):

    result = (db.session.query(
        players.id.label("id"), coalesce(players.nick, "unknown").label("player_nick"), matches.id.label("match_id"),
        heroes.localized_name.label("hero_localized_name"), abilities.name.label("ability_name"),
        func.count(abilities.name),func.max(ability_upgrades.level),
    )
              .select_from(players).
              join(matches_players_details).
              join(heroes).
              join(matches).
              join(ability_upgrades).
              join(abilities).
              filter(players.id == player_id).
              group_by(text("ability_name"),players.id,text("player_nick"),text("hero_localized_name"),matches.id).
              order_by(matches.id).
              all())

    keys = ["id","player_nick","match_id","hero_localized_name","ability_name","count","upgrade_level"]

    return vypis_v4(result,keys, "abilities", 7)


@app.route('/v4/matches/<match_id>/top_purchases/', methods=['GET'])
def top_purchases_v4(match_id):

    tabulka = (db.session.query(items.id.label("item_id"),items.name.label("i_name"),heroes.id.label("hero_id"),
                                heroes.localized_name.label("h_name"),
                                func.count().label("pocet"),
                                func.row_number().over(heroes.id,and_(func.count().desc(),items.name))
                                .label("row_number"))
                .select_from(matches)
                .join(matches_players_details)
                .join(purchase_logs)
                .join(items,items.id == purchase_logs.item_id)
                .join(heroes)
                .filter(and_(matches.id == match_id,
                                or_(and_(matches_players_details.player_slot < 5,matches.radiant_win == True),
                                and_(matches_players_details.player_slot > 127,matches.radiant_win == False)) ))
                .group_by(heroes.id,heroes.localized_name,items.id)
                .order_by(heroes.id,func.count().desc(),items.name)
                .subquery()
               )

    result = (db.session.query(tabulka.c.hero_id.label("id"), tabulka.c.h_name.label("name"),
                               tabulka.c.pocet.label("count"),tabulka.c.item_id.label("id"),
                               tabulka.c.i_name.label("name"))
                .select_from(tabulka)
                .filter(tabulka.c.row_number <= 5)
                .order_by(tabulka.c.hero_id)
                .all()

              )

    keys = ["id","name","count","id","name"]
    player = top_purchases_vypis(match_id,result,keys)

    return flask.jsonify(player)


@app.route('/v4/abilities/<ability_id>/usage/', methods=['GET'])
def ability_usage_v4(ability_id):

    tabulka = (db.session.query(heroes.id.label("id"),heroes.localized_name.label("h_name"),abilities.name.label("name"),
        case([
        (func.round(cast(ability_upgrades.time,sqlalchemy.Numeric)/cast(matches.duration,sqlalchemy.Numeric) * 100,5) < 10, '0-9'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric)*100,5) < 20, '10-19'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 30, '20-29'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 40, '30-39'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 50, '40-49'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 60, '50-59'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 70, '60-69'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 80, '70-79'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 90, '80-89'),
            (func.round(cast(ability_upgrades.time, sqlalchemy.Numeric) / cast(matches.duration, sqlalchemy.Numeric) * 100,5) < 100, '90-99'),
          ],
        else_='100-109'
        ).label("bucket"),
                case(
                    [(matches_players_details.player_slot < 5, matches.radiant_win)],
                    else_=not_(matches.radiant_win)).label("winner"),
                func.count().label("count"),
                func.row_number().over(and_(heroes.id,
                case(
                    [(matches_players_details.player_slot < 5, matches.radiant_win)],
                    else_=not_(matches.radiant_win))),func.count().desc()).label("row_number")
                )
               .select_from(abilities)
               .join(ability_upgrades)
               .join(matches_players_details,matches_players_details.id == ability_upgrades.match_player_detail_id)
               .join(matches)
               .join(heroes)
               .filter(abilities.id == ability_id)
               .group_by(heroes.id,text("winner"),text("bucket"),abilities.name)
               .order_by(heroes.name,func.count().desc())
               .subquery()
               )

    result = (db.session.query(tabulka.c.name,tabulka.c.id,tabulka.c.h_name.label("name"),tabulka.c.winner,
                               tabulka.c.bucket,tabulka.c.count)
              .select_from(tabulka)
              .filter(tabulka.c.row_number == 1).all()
              )

    keys = ["name","id","name","winner","bucket","count"]

    all = ability_usage_vypis(ability_id,result,keys)

    return flask.jsonify(all)


@app.route('/v4/statistics/tower_kills/', methods=['GET'])
def tower_kills_v4():
    tabulka1 = (db.session.query(heroes.id.label("id"),heroes.localized_name.label("localized_name"),
                                 matches_players_details.match_id.label("match_id"),matches_players_details.hero_id.label("hero_id"),
                func.lead(heroes.id).over(text("0"),and_(matches_players_details.match_id,game_objectives.time)).label("lead_hero_id"),
                func.lead(matches_players_details.match_id,1).over(text("0"),and_(matches_players_details.match_id,heroes.id,game_objectives.time))
                                 .label("lead_match_id"),
                                 (func.row_number().over(text("0"),and_(matches_players_details.match_id,heroes.id,game_objectives.time)) -
                                 func.row_number().over(text("0"),and_(matches_players_details.match_id,game_objectives.time))).label("sequence_id"),
                                 )
                .select_from(game_objectives)
                .join(matches_players_details,game_objectives.match_player_detail_id_1 == matches_players_details.id,isouter=True)
                .join(heroes,isouter=True)
                .filter(and_(game_objectives.subtype == "CHAT_MESSAGE_TOWER_KILL",game_objectives.match_player_detail_id_1 != None))
                .order_by(matches_players_details.match_id,game_objectives.time,heroes.id).subquery()
                )

    tabulka2 = (db.session.query(tabulka1,(func.count()+1).label("tower_kills"),func.row_number().
                                 over(tabulka1.c.localized_name,(func.count()+1).desc()).label("row_number"))
                .select_from(tabulka1)
                .filter(and_(tabulka1.c.hero_id == tabulka1.c.lead_hero_id,tabulka1.c.match_id == tabulka1.c.lead_match_id))
                .group_by(tabulka1.c.id,tabulka1.c.localized_name,tabulka1.c.match_id,tabulka1.c.hero_id,
                          tabulka1.c.lead_hero_id,tabulka1.c.lead_match_id,tabulka1.c.sequence_id)
                .order_by(tabulka1.c.match_id).subquery()

                )
    result = (db.session.query(tabulka2.c.id,tabulka2.c.localized_name.label("name"),tabulka2.c.tower_kills)
              .select_from(tabulka2)
              .filter(tabulka2.c.row_number == 1)
              .order_by(tabulka2.c.tower_kills.desc(),tabulka2.c.localized_name.asc()).all()
              )

    keys = ["id","name","tower_kills"]

    all = tower_kills_vypis(result, keys)

    return flask.jsonify(all)




