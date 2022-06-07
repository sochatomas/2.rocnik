import flask


def vypis_v4(odpoved,keys, string, pocet_stlpcov):  # formatovanie vypisu pre /game_objectives a /abilities

    matches = []
    actions = []


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


    return flask.jsonify(player)


def vytvor_dict_player(popis, odpoved, matches):  # vytvorenie dict hraca
    player = {
        popis[0]: odpoved[0][0],
        popis[1]: odpoved[0][1],
        "matches": matches
    }
    return player


def tower_kills_vypis(result,keys):
    hero_list = []
    all = {
        "heroes": hero_list
    }

    while len(result) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = result.pop(0)

        if akt_zaznam[0] is not None:  # vytvorenie noveho zaznamu pre zapas
            match = {}
            for index in range(0, 3):  # naplnenie hodnot v dict. akt. zapasu
                key = keys[index]
                match[key] = akt_zaznam[index]
            hero_list.append(match)

    return all


def ability_usage_vypis(ability_id,result,keys):
    hero_list = []
    all = {
        "id": int(ability_id),
        keys[0]: result[0][0],
        "heroes": hero_list
    }
    match = {}
    id = 0
    usage_loosers = {}
    usage_winners = {}

    while len(result) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = result.pop(0)

        if id != akt_zaznam[1]:
            if id != 0:
                match['usage_winners'] = usage_winners
                match['usage_loosers'] = usage_loosers
                hero_list.append(match)
                match = {}
                usage_loosers = {}
                usage_winners = {}
            id = akt_zaznam[1]

            for index in range(1, 3):  # naplnenie hodnot v dict. akt. zapasu
                key = keys[index]
                match[key] = akt_zaznam[index]

        if akt_zaznam[3] is True:
            usage_winners = {
                keys[4]: akt_zaznam[4],
                keys[5]: akt_zaznam[5]
            }
        else:
            usage_loosers = {
                keys[4]: akt_zaznam[4],
                keys[5]: akt_zaznam[5]
            }

    if (len(usage_winners) > 0):
        match['usage_winners'] = usage_winners
    if (len(usage_loosers) > 0):
        match['usage_loosers'] = usage_loosers
    hero_list.append(match)

    return all


def top_purchases_vypis(match_id,result,keys):
    hero_list = []
    actions = []

    player = {
        'id': int(match_id),
        "heroes": hero_list
    }
    akt_match_id = 0

    while len(result) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = result.pop(0)

        if akt_zaznam[0] != akt_match_id:  # vytvorenie noveho zaznamu zapasov
            akt_match_id = akt_zaznam[0]
            actions = []
            match = {}

            for index in range(0, 2):  # zaplnenie hodnot pre dany zapas
                key = keys[index]
                match[key] = akt_zaznam[index]

            match['top_purchases'] = actions  # pridanie listu akcii do dict akt. zapasu
            hero_list.append(match)

        action = {}
        for index in range(2, 5):  # vytvorenie novej akcie a nacitanie hodnot
            key = keys[index]
            action[key] = akt_zaznam[index]
        actions.append(action)  # pridanie do listu akcii

        return player


def game_exp_vypis(result,keys):
    match_list = []
    player = vytvor_dict_player(keys, result, match_list)

    while len(result) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = result.pop(0)

        if akt_zaznam[2] is not None:  # vytvorenie noveho zaznamu pre zapas
            match = {}
            for index in range(2, 8):  # naplnenie hodnot v dict. akt. zapasu
                key = keys[index]
                match[key] = akt_zaznam[index]
            match_list.append(match)

    return player


def patches_vypis(result,keys):

    akt_verzia_patch = ''
    patch_list = []
    match_list = []

    while len(result) > 0:  # prechadzanie vsetkych zaznamov
        akt_zaznam = result.pop(0)

        if akt_zaznam[0] != akt_verzia_patch:  # vytvorenie noveho zaznamu
            akt_verzia_patch = akt_zaznam[0]
            match_list = []
            patch = {  # vytvorenie noveho dict  pre patch
                keys[0]: akt_zaznam[0],
                keys[1]: akt_zaznam[1],
                keys[2]: akt_zaznam[2],
                "matches": match_list
            }
            patch_list.append(patch)

        if akt_zaznam[4] is not None:  # vytvorenie noveho zaznamu pre zapas
            match = {
                keys[3]: akt_zaznam[3],
                keys[4]: akt_zaznam[4]
            }
            match_list.append(match)

    vypis_all = {"patches": patch_list}
    return vypis_all
