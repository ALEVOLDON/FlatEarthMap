import os
import sys
import time
import subprocess
import threading
import http.server
import socketserver
import shutil

WORKDIR = r"C:\Users\alevo\.gemini\antigravity\scratch\femap_presentation"
LOCAL_WEB_DIR = os.path.abspath("femap_local")
PORT = 8089

AUDIO_DIR = os.path.join(WORKDIR, "audio_gtts")
MUSIC_PATH = os.path.join(WORKDIR, "ambient_bg.wav")
OVERLAYS_DIR = os.path.join(WORKDIR, "overlays")
RECORDINGS_V2 = os.path.join(WORKDIR, "recordings_v2")
PROCESSED_V2 = os.path.join(WORKDIR, "processed_v2")

for d in [RECORDINGS_V2, PROCESSED_V2]:
    os.makedirs(d, exist_ok=True)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=LOCAL_WEB_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    server = socketserver.TCPServer(("", PORT), QuietHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

def get_duration(audio_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def perform_scene_actions(scene_idx, page, target_duration):
    t0 = time.time()
    def remaining():
        return max(0.3, target_duration - (time.time() - t0))

    if scene_idx == 1:
        # Scene 1: Welcome & Overview
        time.sleep(2.0)
        page.mouse.move(960, 540)
        time.sleep(1.5)
        # Pan map smoothly
        page.mouse.down()
        page.mouse.move(910, 480, steps=15)
        page.mouse.up()
        time.sleep(2.0)
        page.click("#btn-reset-zoom")
        time.sleep(remaining())

    elif scene_idx == 2:
        # Scene 2: Projection Centers
        time.sleep(2.0)
        page.click(".btn-preset[data-lat='90']") # North pole
        time.sleep(3.0)
        page.click(".btn-preset[data-lat='-90']") # South pole (flip!)
        time.sleep(5.0)
        page.click(".btn-preset[data-lat='0']") # Equator
        time.sleep(4.0)
        # Custom center Moscow
        page.fill("#inp-lat", "55.75")
        page.fill("#inp-lon", "37.61")
        page.click("#btn-apply")
        time.sleep(5.0)
        # Reset back
        page.click(".btn-preset[data-lat='90']")
        page.click("#btn-reset-zoom")
        time.sleep(remaining())

    elif scene_idx == 3:
        # Scene 3: Grid, coordinates, cities, adding custom point
        time.sleep(2.0)
        page.click("#chk-labels") # Labels of coordinates
        time.sleep(3.0)
        page.evaluate("() => document.getElementById('controls').scrollTop = 450")
        time.sleep(1.5)
        page.fill("#add-name", "Санкт-Петербург")
        page.fill("#add-lat", "59.93")
        page.fill("#add-lon", "30.33")
        time.sleep(1.5)
        page.click("#btn-add-point")
        time.sleep(3.0)
        page.evaluate("() => document.getElementById('controls').scrollTop = 0")
        time.sleep(remaining())

    elif scene_idx == 4:
        # Scene 4: Distance ruler - Sphere vs Flat Earth
        time.sleep(2.0)
        page.click("#chk-ruler")
        time.sleep(2.0)
        page.evaluate("""() => {
            const sydney = [151.21, -33.87];
            const santiago = [-70.67, -33.46];
            state.ruler.points = [sydney, santiago];
            calculateRulerDistances();
            renderRuler();
            const t = LANG[state.lang];
            setStatus('📏 ' + t.sphereDist + ': ' + Math.round(state.ruler.distSphere).toLocaleString() + ' ' + t.km +
                      ' | 📐 ' + t.aeDist + ': ' + Math.round(state.ruler.distAE).toLocaleString() + ' ' + t.km);
        }""")
        time.sleep(6.0)
        page.click("#chk-ruler")
        time.sleep(remaining())

    elif scene_idx == 5:
        # Scene 5: Flight routes
        time.sleep(2.0)
        page.click("#chk-routes")
        time.sleep(3.0)
        page.evaluate("""() => {
            const r = ROUTES.find(x => x.id === 'SYD-SCL');
            if (r) showRouteTooltip({ clientX: 1150, clientY: 620 }, r);
        }""")
        time.sleep(5.0)
        page.evaluate("""() => {
            const r = ROUTES.find(x => x.id === 'JNB-PER');
            if (r) showRouteTooltip({ clientX: 1050, clientY: 550 }, r);
        }""")
        time.sleep(5.0)
        page.evaluate("() => hideRouteTooltip()")
        page.click("#chk-routes")
        time.sleep(remaining())

    elif scene_idx == 6:
        # Scene 6: Astronomy: Sun, Moon, Terminator & Eclipses
        time.sleep(2.0)
        page.click("#chk-sun")
        page.click("#chk-moon")
        page.click("#chk-night")
        time.sleep(3.5)
        page.click("#btn-ecl-solar")
        time.sleep(5.0)
        page.click("#btn-ecl-lunar")
        time.sleep(5.0)
        page.click("#btn-astro-now")
        time.sleep(remaining())

    elif scene_idx == 7:
        # Scene 7: Celestial Spheres: Planets, Zodiac, Stars & Milky Way
        time.sleep(2.0)
        page.click("#chk-planets")
        page.click("#chk-equator")
        page.click("#chk-tropics")
        page.click("#chk-ecliptic")
        time.sleep(3.0)
        page.click("#chk-zodiac")
        page.click("#chk-stars")
        page.click("#chk-milkyway")
        time.sleep(5.0)
        page.evaluate("() => { if (!document.getElementById('coords-details').open) document.getElementById('coords-details').open = true; }")
        time.sleep(remaining())

    elif scene_idx == 8:
        # Scene 8: ISS Live Tracking & Orbit simulation
        time.sleep(2.0)
        page.click("#chk-iss")
        time.sleep(3.5)
        page.evaluate("""() => {
            try {
                var pt = (typeof issSubpoint === 'function') ? issSubpoint(state.astro.date) : { lon: 35.5, lat: 48.2 };
                if (pt && typeof showIssTooltip === 'function') {
                    showIssTooltip({ clientX: 960, clientY: 540 }, pt);
                }
            } catch(e) {}
        }""")
        time.sleep(4.5)
        page.evaluate("() => { if (typeof hideIssTooltip === 'function') hideIssTooltip(); }")
        # Activate ISS simulation
        page.click("#btn-play-iss")
        time.sleep(2.0)
        page.click("#btn-iss-speed-20")
        time.sleep(6.5)
        page.click("#btn-play-iss") # pause
        time.sleep(remaining())

    elif scene_idx == 9:
        # Scene 9: Trajectory Tails & Time Animation
        time.sleep(1.5)
        page.evaluate("() => { const cd = document.getElementById('coords-details'); if (cd) cd.open = false; }")
        page.evaluate("""() => {
            var chkSun = document.getElementById('chk-sun-trail');
            if (chkSun) { chkSun.checked = true; chkSun.dispatchEvent(new Event('change')); }
            var chkMoon = document.getElementById('chk-moon-trail');
            if (chkMoon) { chkMoon.checked = true; chkMoon.dispatchEvent(new Event('change')); }
            var chkSunMain = document.getElementById('chk-sun');
            if (chkSunMain && !chkSunMain.checked) { chkSunMain.checked = true; chkSunMain.dispatchEvent(new Event('change')); }
        }""")
        time.sleep(2.0)
        page.click("#btn-play-day")
        time.sleep(7.0)
        page.click("#btn-play-day") # pause
        page.click("#btn-astro-now")
        time.sleep(remaining())

    elif scene_idx == 10:
        # Scene 10: Conclusion & Architecture
        time.sleep(2.0)
        page.select_option("#lang-select", "en")
        time.sleep(3.5)
        page.select_option("#lang-select", "de")
        time.sleep(3.5)
        page.select_option("#lang-select", "ru")
        time.sleep(2.5)
        page.click("#btn-reset-zoom")
        time.sleep(remaining())

def main():
    print("=" * 60)
    print("FlatEarthMap v6.4.2 — Generating Upgraded Presentation v2")
    print("=" * 60)

    server = start_server()
    print(f"[OK] Local web server running on port {PORT}")

    from playwright.sync_api import sync_playwright

    # Calculate audio durations with 1.06 tempo
    tempo = 1.06
    voice_durations = {}
    for i in range(1, 11):
        mp3 = os.path.join(AUDIO_DIR, f"scene_{i}.mp3")
        raw_dur = get_duration(mp3)
        voice_durations[i] = raw_dur / tempo
        print(f"Scene {i} voice duration: {voice_durations[i]:.2f} s (raw: {raw_dur:.2f} s)")

    # Record all 10 scenes
    print("\n--- Recording Browser Scenes for v2 ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for i in range(1, 11):
            target_dur = voice_durations[i] + 1.2
            scene_dir = os.path.join(RECORDINGS_V2, f"scene_{i}")
            os.makedirs(scene_dir, exist_ok=True)
            print(f"Recording Scene {i}/10 ({target_dur:.2f} s)...")

            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=scene_dir,
                record_video_size={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto(f"http://localhost:{PORT}/", wait_until="networkidle")
            time.sleep(0.5)

            perform_scene_actions(i, page, target_dur)

            context.close()

            rec_files = [f for f in os.listdir(scene_dir) if f.endswith(".webm")]
            if rec_files:
                src_webm = os.path.join(scene_dir, rec_files[0])
                dst_webm = os.path.join(RECORDINGS_V2, f"raw_scene_{i}.webm")
                shutil.copy2(src_webm, dst_webm)
                print(f"  -> Saved: raw_scene_{i}.webm")

        browser.close()

    # Composite Scenes with FFmpeg: Voice Processing + Ambient Music Bed + Overlays
    print("\n--- Compositing Scenes with Lively Voice & Ambient Music ---")
    processed_clips = []
    music_offset = 0.0

    for i in range(1, 11):
        raw_webm = os.path.join(RECORDINGS_V2, f"raw_scene_{i}.webm")
        raw_mp3 = os.path.join(AUDIO_DIR, f"scene_{i}.mp3")
        overlay_png = os.path.join(OVERLAYS_DIR, f"scene_{i}.png")
        out_mp4 = os.path.join(PROCESSED_V2, f"scene_{i}.mp4")

        clip_dur = voice_durations[i] + 0.8

        # Audio filter:
        # Voice: atempo=1.06, radio EQ & compressor, volume=1.0
        # Music: seek from music_offset, atrim to clip_dur, volume=0.12 (soft atmospheric bed)
        # amix: mixes voice and music together seamlessly
        filter_complex = (
            f"[0:v][2:v]overlay=0:0[vout]; "
            f"[1:a]atempo={tempo},equalizer=f=300:t=q:w=1.2:g=2.5,equalizer=f=3500:t=q:w=1.0:g=2.0,"
            f"acompressor=threshold=-16dB:ratio=3:attack=5:release=50,volume=1.05[voice]; "
            f"[3:a]atrim=start={music_offset:.2f}:duration={clip_dur:.2f},asetpts=PTS-STARTPTS,volume=0.12[bg]; "
            f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", raw_webm,
            "-i", raw_mp3,
            "-i", overlay_png,
            "-i", MUSIC_PATH,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{clip_dur:.3f}",
            out_mp4
        ]
        print(f"Encoding Scene {i}.mp4 (duration {clip_dur:.2f} s)...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error encoding scene {i}: {res.stderr}")
        else:
            print(f"  -> Encoded: scene_{i}.mp4 ({os.path.getsize(out_mp4)/1024/1024:.2f} MB)")
            processed_clips.append(out_mp4)

        music_offset += clip_dur

    # Concatenate Final Video
    print("\n--- Concatenating Final Presentation Video v2 ---")
    concat_list_path = os.path.join(WORKDIR, "concat_list_v2.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for clip in processed_clips:
            clean_path = clip.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    final_output = os.path.join(WORKDIR, "femap_full_presentation.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        final_output
    ]
    res = subprocess.run(concat_cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(final_output):
        final_size_mb = os.path.getsize(final_output) / 1024 / 1024
        print(f"\n[SUCCESS] Upgraded presentation created: {final_output}")
        print(f"  -> File size: {final_size_mb:.2f} MB")

        # Copy to artifact directory
        artifact_dest = r"C:\Users\alevo\.gemini\antigravity\brain\c61b6742-6e03-4db8-848b-ef68e1d034a2\femap_full_presentation.mp4"
        shutil.copy2(final_output, artifact_dest)

        # Copy to Desktop folder
        desktop_dest = r"C:\Users\alevo\Desktop\FlatEarthMap_Presentation\femap_full_presentation.mp4"
        shutil.copy2(final_output, desktop_dest)
        print(f"  -> Copied to Desktop: {desktop_dest}")
    else:
        print("Concatenation failed:", res.stderr)

if __name__ == "__main__":
    main()
