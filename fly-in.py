import sys
try:
    from rendering import MapDisplay
    import arcade
    import subprocess
    import time
    # from pudb import set_trace
except ImportError:
    print("Make sure to use: - make install before - make run\n "
          "or to switch on environment before running with"
          " - source venv/bin/activate")
    sys.exit(1)

if __name__ == "__main__":
    try:
        # set_trace()
        if len(sys.argv) == 1:
            renderer = MapDisplay(2500, 1400, "Fly-in", "01_linear_path.txt")
            arcade.run()
        elif len(sys.argv) == 2:
            user_input = sys.argv[1].strip()
            renderer = MapDisplay(2500, 1400, "Fly-in", user_input)
            arcade.run()
        else:
            raise ValueError("[ARGS] Number of arguments incompatible")

    except Exception as e:
        print(f"[ERROR] {e}")
    except KeyboardInterrupt:
        subprocess.run('clear', shell=True)
        print("Fly in simulation closed.")
        time.sleep(1)
        sys.exit(1)
