import json, os, subprocess, sys

def frames(p):
    if not os.path.exists(p):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=nb_frames,avg_frame_rate,duration",
                          "-of", "json", p], capture_output=True, text=True).stdout
    st = json.loads(out)["streams"][0]
    nb = st.get("nb_frames")
    dur = float(st.get("duration", 0) or 0)
    return nb, st.get("avg_frame_rate"), round(dur, 3)

folder = sys.argv[1]
names = sys.argv[2:]
for n in names:
    r = os.path.join(folder, "assets", "RTM output", n + ".mp4")
    c = os.path.join(folder, "assets", "ManimCE output", n + "-manimce.mp4")
    print(f"{n:36} RTM={frames(r)}  CE={frames(c)}")
