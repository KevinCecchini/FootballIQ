
import json
import pandas as pd


def get_tracking_frame(tracking_file, frame_number):
    """
    Cerca e restituisce un singolo frame dal file tracking JSONL.
    """

    with open(tracking_file, "r", encoding="utf-8") as f:

        for line in f:

            frame = json.loads(line)

            if frame["frame"] == frame_number:
                return frame

    return None

def build_players_table(
    frame,
    players_metadata,
    team_lookup
):
    """
    Converte i player_data di un frame in una tabella
    arricchita con nome, squadra, numero e ruolo.
    """

    players_df = pd.DataFrame(
        frame["player_data"]
    )

    players = players_df.merge(
        players_metadata,
        on="player_id",
        how="left"
    )

    players["team_name"] = (
        players["team_id"]
        .map(team_lookup)
    )

    return players
