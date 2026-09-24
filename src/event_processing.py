
import json
import pandas as pd


def get_decision_frame_number(
    possession_row,
    end_frame_column
):
    """
    Restituisce il frame immediatamente precedente
    alla fine della player possession.
    """

    end_frame = possession_row[end_frame_column]

    if pd.isna(end_frame):
        return None

    return int(end_frame) - 1


def find_next_possession_player(
    tracking_file,
    decision_frame_number,
    current_player_id,
    player_lookup,
    window_frames=50
):
    """
    Cerca il primo giocatore diverso dal portatore
    che viene identificato in possesso dopo il decision frame.

    window_frames=50 significa circa 5 secondi
    con tracking a 10 fps.
    """

    with open(tracking_file, "r", encoding="utf-8") as f:

        for line in f:

            frame = json.loads(line)

            # Ignoriamo i frame precedenti
            if frame["frame"] <= decision_frame_number:
                continue

            # Stop dopo la finestra scelta
            if frame["frame"] > decision_frame_number + window_frames:
                break

            player_id = frame["possession"]["player_id"]

            # Nessun possessore identificato
            if player_id is None:
                continue

            # È ancora il portatore originale
            if player_id == current_player_id:
                continue

            player_info = player_lookup.get(
                player_id,
                {}
            )

            return {
                "frame": frame["frame"],
                "timestamp": frame["timestamp"],
                "player_id": player_id,
                "player_name": player_info.get("player_name"),
                "team_id": player_info.get("team_id"),
                "shirt_number": player_info.get("shirt_number")
            }

    return None


def find_carrier_near_frame(
    tracking_file,
    target_frame,
    lookback_frames=10
):
    """
    Cerca il giocatore in possesso nel target frame.
    Se non è disponibile, guarda indietro fino a
    lookback_frames.

    Con tracking a 10 fps:
    10 frame ≈ 1 secondo.
    """

    best_match = None

    start_frame = max(
        0,
        target_frame - lookback_frames
    )

    with open(
        tracking_file,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            frame = json.loads(line)

            frame_number = frame["frame"]

            # Non ci interessa ciò che viene prima
            if frame_number < start_frame:
                continue

            # Ci fermiamo oltre il target
            if frame_number > target_frame:
                break

            player_id = frame["possession"]["player_id"]

            # Ogni volta che troviamo un possessore valido,
            # lo salviamo.
            # Alla fine rimarrà quello più vicino al target.
            if player_id is not None:

                best_match = {
                    "player_id": player_id,
                    "frame": frame_number,
                    "timestamp": frame["timestamp"],
                    "group": frame["possession"]["group"]
                }

    return best_match
