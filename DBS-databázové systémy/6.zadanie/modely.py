import os

import pandas as pd
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://' + os.getenv("DBUSER") +
        ':' + os.getenv("DBPASS") +
        '@' + os.getenv("DBIP") +
        ':' + os.getenv("DBPORT") +
        '/' + os.getenv("DBNAME"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

DATABASE_CONNECTION = (
        'postgresql://' + os.getenv("DBUSER") +
        ':' + os.getenv("DBPASS") +
        '@' + os.getenv("DBIP") +
        ':' + os.getenv("DBPORT") +
        '/' + os.getenv("DBNAME"))

engine = create_engine(DATABASE_CONNECTION)
connection = engine.connect()

data = pd.read_sql_query("select * from players where id = 10",connection)


class players(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    nick = db.Column(db.Text)
    # matches_players_details = relationship("matches_players_details",back_populates="players")


class player_ratings(db.Model):
    __tablename__ = 'player_ratings'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    total_wins = db.Column(db.Integer)
    total_matches = db.Column(db.Integer)
    trueskill_mu = db.Column(db.Numeric)
    trueskill_sigma = db.Column(db.Numeric)


class cluster_regions(db.Model):
    __tablename__ = 'cluster_regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class matches(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    cluster_region_id = db.Column(db.Integer, db.ForeignKey("cluster_regions.id"))
    start_time = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    tower_status_radiant = db.Column(db.Integer)
    tower_status_dire = db.Column(db.Integer)
    barracks_status_radiant = db.Column(db.Integer)
    barracks_status_dire = db.Column(db.Integer)
    first_blood_time = db.Column(db.Integer)
    game_mode = db.Column(db.Integer)
    radiant_win = db.Column(db.Boolean)
    negative_votes = db.Column(db.Integer)
    positive_votes = db.Column(db.Integer)


class heroes(db.Model):
    __tablename__ = 'heroes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    localized_name = db.Column(db.Text)
    # matches_players_details = relationship("matches_players_details",back_populates="heroes")


class teamfights(db.Model):
    __tablename__ = 'teamfights'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"))
    start_teamfight = db.Column(db.Integer)
    end_teamfight = db.Column(db.Integer)
    last_death = db.Column(db.Integer)
    deaths = db.Column(db.Integer)


class items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class abilities(db.Model):
    __tablename__ = 'abilities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class matches_players_details(db.Model):
    __tablename__ = 'matches_players_details'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"))
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    hero_id = db.Column(db.Integer, db.ForeignKey("heroes.id"))
    player_slot = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    gold_spent = db.Column(db.Integer)
    gold_per_min = db.Column(db.Integer)
    xp_per_min = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    denies = db.Column(db.Integer)
    last_hits = db.Column(db.Integer)
    stuns = db.Column(db.Integer)
    hero_damage = db.Column(db.Integer)
    hero_healing = db.Column(db.Integer)
    tower_damage = db.Column(db.Integer)
    item_id_1 = db.Column(db.Integer, db.ForeignKey("items.id"))
    item_id_2 = db.Column(db.Integer, db.ForeignKey("items.id"))
    item_id_3 = db.Column(db.Integer, db.ForeignKey("items.id"))
    item_id_4 = db.Column(db.Integer, db.ForeignKey("items.id"))
    item_id_5 = db.Column(db.Integer, db.ForeignKey("items.id"))
    item_id_6 = db.Column(db.Integer, db.ForeignKey("items.id"))
    level = db.Column(db.Integer)
    leaver_status = db.Column(db.Integer)
    xp_hero = db.Column(db.Integer)
    xp_creep = db.Column(db.Integer)
    xp_roshan = db.Column(db.Integer)
    xp_other = db.Column(db.Integer)
    gold_other = db.Column(db.Integer)
    gold_death = db.Column(db.Integer)
    gold_buyback = db.Column(db.Integer)
    gold_abandon = db.Column(db.Integer)
    gold_sell = db.Column(db.Integer)
    gold_destroying_structure = db.Column(db.Integer)
    gold_killing_heroes = db.Column(db.Integer)
    gold_killing_creeps = db.Column(db.Integer)
    gold_killing_roshan = db.Column(db.Integer)
    gold_killing_couriers = db.Column(db.Integer)
    # heroes = relationship("heroes",back_populates="matches_players_details")
    # players = relationship("players",back_populates="matches_players_details")


class player_times(db.Model):
    __tablename__ = 'player_times'
    id = db.Column(db.Integer, primary_key=True)
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    time = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    lh = db.Column(db.Integer)
    xp = db.Column(db.Integer)


class teamfights_players(db.Model):
    __tablename__ = 'teamfights_players'
    id = db.Column(db.Integer, primary_key=True)
    teamfight_id = db.Column(db.Integer, db.ForeignKey("teamfights.id"))
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    buyback = db.Column(db.Integer)
    damage = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    gold_delta = db.Column(db.Integer)
    xp_start = db.Column(db.Integer)
    xp_end = db.Column(db.Integer)


class purchase_logs(db.Model):
    __tablename__ = 'purchase_logs'
    id = db.Column(db.Integer, primary_key=True)
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    item_id = db.Column(db.Integer,db.ForeignKey("items.id"))
    time = db.Column(db.Integer)




class game_objectives(db.Model):
    __tablename__ = 'game_objectives'
    id = db.Column(db.Integer, primary_key=True)
    match_player_detail_id_1 = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    match_player_detail_id_2 = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    key = db.Column(db.Integer)
    subtype = db.Column(db.Text)
    team = db.Column(db.Integer)
    time = db.Column(db.Integer)
    value = db.Column(db.Integer)
    slot = db.Column(db.Integer)


class ability_upgrades(db.Model):
    __tablename__ = 'ability_upgrades'
    id = db.Column(db.Integer, primary_key=True)
    ability_id = db.Column(db.Integer, db.ForeignKey("abilities.id"))
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    level = db.Column(db.Integer)
    time = db.Column(db.Integer)


class chats(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    message = db.Column(db.Text)
    time = db.Column(db.Integer)
    nick = db.Column(db.Text)


class player_actions(db.Model):
    __tablename__ = 'player_actions'
    id = db.Column(db.Integer, primary_key=True)
    match_player_detail_id = db.Column(db.Integer, db.ForeignKey("matches_players_details.id"))
    unit_order_none = db.Column(db.Integer)
    unit_order_move_to_position = db.Column(db.Integer)
    unit_order_move_to_target = db.Column(db.Integer)
    unit_order_attack_move = db.Column(db.Integer)
    unit_order_attack_target = db.Column(db.Integer)
    unit_order_cast_position = db.Column(db.Integer)
    unit_order_cast_target = db.Column(db.Integer)
    unit_order_cast_target_tree = db.Column(db.Integer)
    unit_order_cast_no_target = db.Column(db.Integer)
    unit_order_cast_toggle = db.Column(db.Integer)
    unit_order_hold_position = db.Column(db.Integer)
    unit_order_train_ability = db.Column(db.Integer)
    unit_order_drop_item = db.Column(db.Integer)
    unit_order_give_item = db.Column(db.Integer)
    unit_order_pickup_item = db.Column(db.Integer)
    unit_order_pickup_rune = db.Column(db.Integer)
    unit_order_purchase_item = db.Column(db.Integer)
    unit_order_sell_item = db.Column(db.Integer)
    unit_order_disassemble_item = db.Column(db.Integer)
    unit_order_move_item = db.Column(db.Integer)
    unit_order_cast_toggle_auto = db.Column(db.Integer)
    unit_order_stop = db.Column(db.Integer)
    unit_order_buyback = db.Column(db.Integer)
    unit_order_glyph = db.Column(db.Integer)
    unit_order_eject_item_from_stash = db.Column(db.Integer)
    unit_order_cast_rune = db.Column(db.Integer)
    unit_order_ping_ability = db.Column(db.Integer)
    unit_order_move_to_direction = db.Column(db.Integer)


class patches(db.Model):
    __tablename__ = 'patches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    release_date = db.Column(db.TIMESTAMP)

