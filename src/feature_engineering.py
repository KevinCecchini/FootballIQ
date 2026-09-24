
import numpy as np
import pandas as pd


def get_attack_direction(team_players):
    """
    Stima la direzione d'attacco usando la posizione del portiere.

    Restituisce:
        +1 -> squadra attacca verso x positivo
        -1 -> squadra attacca verso x negativo
    """

    goalkeeper = team_players[
        team_players["position"].str.contains(
            "Goalkeeper",
            case=False,
            na=False
        )
    ]

    if len(goalkeeper) == 0:
        raise ValueError("Goalkeeper not found.")

    goalkeeper_x = goalkeeper.iloc[0]["x"]

    if goalkeeper_x < 0:
        return 1
    else:
        return -1


def nearest_defender_info(
    receiver_x,
    receiver_y,
    opponents
):
    """
    Trova l'avversario più vicino al possibile ricevente.
    """

    distances = np.sqrt(
        (opponents["x"] - receiver_x) ** 2
        +
        (opponents["y"] - receiver_y) ** 2
    )

    nearest_index = distances.idxmin()

    defender = opponents.loc[nearest_index]

    return pd.Series({
        "nearest_defender_name":
            defender["player_name"],

        "nearest_defender_distance":
            distances.loc[nearest_index]
    })


def passing_lane_features(
    carrier_x,
    carrier_y,
    receiver_x,
    receiver_y,
    opponents,
    lane_width=1.5
):
    """
    Misura quanto è ostruita la linea
    tra portatore e possibile ricevente.
    """

    dx = receiver_x - carrier_x
    dy = receiver_y - carrier_y

    segment_length_squared = dx**2 + dy**2

    if segment_length_squared == 0:

        return pd.Series({
            "lane_blockers": 0,
            "nearest_lane_defender_distance": np.nan
        })

    lane_distances = []

    for _, opponent in opponents.iterrows():

        px = opponent["x"] - carrier_x
        py = opponent["y"] - carrier_y

        # Proiezione dell'avversario
        # sul segmento portatore-ricevente
        t = (
            px * dx + py * dy
        ) / segment_length_squared

        # Consideriamo solo avversari
        # tra portatore e ricevente
        if 0 <= t <= 1:

            projection_x = carrier_x + t * dx
            projection_y = carrier_y + t * dy

            distance_to_lane = np.sqrt(
                (opponent["x"] - projection_x) ** 2
                +
                (opponent["y"] - projection_y) ** 2
            )

            lane_distances.append(
                distance_to_lane
            )

    if len(lane_distances) == 0:

        return pd.Series({
            "lane_blockers": 0,
            "nearest_lane_defender_distance": np.nan
        })

    lane_distances = np.array(
        lane_distances
    )

    blockers = np.sum(
        lane_distances <= lane_width
    )

    return pd.Series({
        "lane_blockers": int(blockers),
        "nearest_lane_defender_distance":
            lane_distances.min()
    })


def build_candidate_passes(
    players,
    carrier_player_id,
    lane_width=1.5
):
    """
    Dato uno stato del gioco, costruisce
    le possibili opzioni di passaggio del portatore
    e calcola le principali feature spaziali.
    """

    # ----------------------------
    # PORTATORE
    # ----------------------------

    carrier_df = players[
        players["player_id"] == carrier_player_id
    ]

    if len(carrier_df) == 0:
        raise ValueError("Ball carrier not found.")

    carrier = carrier_df.iloc[0]

    carrier_team_id = carrier["team_id"]


    # ----------------------------
    # COMPAGNI E AVVERSARI
    # ----------------------------

    teammates = players[
        (players["team_id"] == carrier_team_id)
        &
        (players["player_id"] != carrier_player_id)
    ].copy()

    opponents = players[
        players["team_id"] != carrier_team_id
    ].copy()


    # ----------------------------
    # DIREZIONE D'ATTACCO
    # ----------------------------

    team_players = players[
        players["team_id"] == carrier_team_id
    ]

    attack_direction = get_attack_direction(
        team_players
    )


    # ----------------------------
    # CANDIDATE PASSES
    # ----------------------------

    candidates = teammates.copy()


    # Distanza del passaggio
    candidates["pass_distance"] = np.sqrt(
        (candidates["x"] - carrier["x"]) ** 2
        +
        (candidates["y"] - carrier["y"]) ** 2
    )


    # Progressione verso la porta avversaria
    candidates["forward_progression"] = (
        attack_direction
        *
        (candidates["x"] - carrier["x"])
    )


    # Difensore più vicino
    defender_info = candidates.apply(
        lambda row: nearest_defender_info(
            row["x"],
            row["y"],
            opponents
        ),
        axis=1
    )

    candidates[
        [
            "nearest_defender_name",
            "nearest_defender_distance"
        ]
    ] = defender_info


    # Passing lane
    lane_info = candidates.apply(
        lambda row: passing_lane_features(
            carrier["x"],
            carrier["y"],
            row["x"],
            row["y"],
            opponents,
            lane_width
        ),
        axis=1
    )

    candidates[
        [
            "lane_blockers",
            "nearest_lane_defender_distance"
        ]
    ] = lane_info


    return candidates
