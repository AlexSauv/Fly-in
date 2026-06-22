import sys
try:
    from rendering import MapDisplay
    import arcade
    import subprocess
    import time
except ImportError:
    print("Make sure to use: - make install before - make run\n "
          "or to switch on environment before running with"
          " - source venv/bin/activate")
    sys.exit(1)

if __name__ == "__main__":
    try:
        maps = ["maps/easy/01_linear_path.txt",
                "maps/easy/02_simple_fork.txt",
                "maps/easy/03_basic_capacity.txt",
                "maps/medium/01_dead_end_trap.txt",
                "maps/medium/02_circular_loop.txt",
                "maps/medium/03_priority_puzzle.txt",
                "maps/hard/01_maze_nightmare.txt",
                "maps/hard/02_capacity_hell.txt",
                "maps/hard/03_ultimate_challenge.txt",
                "maps/challenger/01_the_impossible_dream.txt"
                ]
        if len(sys.argv) == 1:
            renderer = MapDisplay(2500, 1400, "Fly-in", maps)
            arcade.run()
        elif len(sys.argv) == 2:
            user_input = sys.argv[1].strip()
            matched_map = None
            for map in maps:
                if map.endswith(user_input):
                    matched_map = map
                    break
            if matched_map:
                renderer = MapDisplay(2500, 1400, "Fly-in", maps)
                arcade.run()
            else:
                raise ValueError(f"[LOADING] {user_input} map not found")

            # renderer = MapDisplay(2500, 1400, "Fly-in", maps)
            # arcade.run()
    except Exception as e:
        print(f"[ERROR] {e}")
    except KeyboardInterrupt:
        subprocess.run('clear', shell=True)
        print("Fly in simulation closed.")
        time.sleep(1)
        sys.exit(1)
