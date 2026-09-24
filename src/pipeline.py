
import pandas as pd

from tracking_utils import (
    get_tracking_frame,
    build_players_table
)

from feature_engineering import (
    build_candidate_passes
)

from event_processing import (
    get_decision_frame_number,
    find_next_possession_player
)


def process_possession(
    possession_row,
    end_frame_column,
    tracking_file,
    players_metadata,
    team_lookup,
    player_lookup,
    window_frames=50
):
    """
    Processa una singola player_possession.

    Restituisce una tabella:
    una riga per ogni possibile ricevente,
    con feature spaziali e scelta osservata.

    La scelta è ancora PROVVISORIA:
    same-team next possession viene usato come proxy
    del ricevente reale.
    """

    # -------------------------------------------------
    # 1. TROVIAMO IL DECISION FRAME
    # -------------------------------------------------

    decision_frame_number = get_decision_frame_number(
        possession_row,
        end_frame_column
    )

    if decision_frame_number is None:
        return None


    # -------------------------------------------------
    # 2. RECUPERIAMO IL TRACKING
    # -------------------------------------------------

    frame = get_tracking_frame(
        tracking_file,
        decision_frame_number
    )

    if frame is None:
        return None


    # -------------------------------------------------
    # 3. IDENTIFICHIAMO IL PORTATORE
    # -------------------------------------------------

    carrier_player_id = frame["possession"]["player_id"]

    if carrier_player_id is None:
        return None


    # -------------------------------------------------
    # 4. COSTRUIAMO LA TABELLA DEI 22 GIOCATORI
    # -------------------------------------------------

    players = build_players_table(
        frame,
        players_metadata,
        team_lookup
    )

    carrier_df = players[
        players["player_id"] == carrier_player_id
    ]

    if len(carrier_df) == 0:
        return None

    carrier = carrier_df.iloc[0]

    carrier_team_id = carrier["team_id"]


    # -------------------------------------------------
    # 5. GENERIAMO LE ALTERNATIVE DI PASSAGGIO
    # -------------------------------------------------

    try:

        candidates = build_candidate_passes(
            players,
            carrier_player_id
        )

    except Exception:
        return None


    # -------------------------------------------------
    # 6. TROVIAMO IL PRIMO NUOVO POSSESSORE
    # -------------------------------------------------

    next_player = find_next_possession_player(
        tracking_file,
        decision_frame_number,
        carrier_player_id,
        player_lookup,
        window_frames=window_frames
    )


    # -------------------------------------------------
    # 7. CLASSIFICHIAMO IL RISULTATO
    # -------------------------------------------------

    actual_receiver_id = None
    actual_receiver_name = None

    if next_player is None:

        choice_status = "unresolved"

    elif next_player["team_id"] == carrier_team_id:

        choice_status = "same_team_new_possession"

        actual_receiver_id = next_player["player_id"]
        actual_receiver_name = next_player["player_name"]

    else:

        choice_status = "possession_lost"


    # -------------------------------------------------
    # 8. AGGIUNGIAMO LA SCELTA OSSERVATA
    # -------------------------------------------------

    candidates = candidates.copy()

    candidates["chosen"] = 0

    if actual_receiver_id is not None:

        candidates.loc[
            candidates["player_id"] == actual_receiver_id,
            "chosen"
        ] = 1


    # -------------------------------------------------
    # 9. AGGIUNGIAMO INFORMAZIONI SULLA DECISIONE
    # -------------------------------------------------

    candidates["event_id"] = possession_row["event_id"]

    candidates["decision_frame"] = decision_frame_number

    candidates["carrier_id"] = carrier_player_id
    candidates["carrier_name"] = carrier["player_name"]

    candidates["carrier_team_id"] = carrier_team_id

    candidates["choice_status"] = choice_status

    candidates["actual_receiver_id"] = actual_receiver_id
    candidates["actual_receiver_name"] = actual_receiver_name


    return candidates
