from nflreadpy import load_rosters
from src.common import Parameters


if __name__ == "__main__":
    # Get current params
    params = Parameters.get()
    print(params)

    # Get rosters
    rosters = load_rosters()
    print(rosters)

    # Write to table
