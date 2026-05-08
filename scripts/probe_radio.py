"""Probe a list of internet-radio URLs and report whether they look playable.

For each URL we issue an HTTP GET with a small Range request, follow up to 4
redirects, and record:
  - final URL after redirects
  - Content-Type
  - Whether the first bytes look like an MP3 frame (sync 0xFFE/0xFFF) or AAC
  - Whether ICY metadata is advertised
A URL is "OK" if we got 200/206, the body looks like MP3/AAC bytes, and the
Content-Type is reasonable. We don't decode -- we just confirm the stream
hands us audio bytes, which is exactly what esp_audio_simple_player needs.
"""
import socket, ssl, struct, urllib.parse, sys, time

CANDIDATES = [
    # The 10 currently in stations.h
    ("BBC Radio 1",          "Pop",         "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one.mp3"),
    ("BBC World Service",    "News/talk",   "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service.mp3"),
    ("KEXP Seattle",         "Indie",       "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"),
    ("NPR News",             "News",        "https://npr-ice.streamguys1.com/live.mp3"),
    ("SomaFM Groove Salad",  "Ambient",     "http://ice1.somafm.com/groovesalad-128-mp3"),
    ("SomaFM Drone Zone",    "Ambient",     "http://ice1.somafm.com/dronezone-128-mp3"),
    ("Radio Paradise",       "Eclectic",    "http://stream.radioparadise.com/mp3-128"),
    ("Radio FIP",            "Eclectic FR", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
    ("J-Pop Powerplay",      "J-Pop",       "http://igor.torontocast.com:1025/stream"),
    ("Antenne Bayern",       "Pop DE",      "http://stream.antenne.de/antenne"),

    # 20 candidate adds, weighted by popularity / variety
    ("BBC Radio 2",          "Adult pop",   "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_two.mp3"),
    ("BBC Radio 3",          "Classical",   "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_three.mp3"),
    ("BBC Radio 4",          "Talk UK",     "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm.mp3"),
    ("BBC Radio 6 Music",    "Alt rock",    "https://stream.live.vc.bbcmedia.co.uk/bbc_6music.mp3"),
    ("Classic FM",           "Classical UK","https://media-ice.musicradio.com/ClassicFMMP3"),
    ("Capital FM",           "Pop UK",      "https://media-ssl.musicradio.com/CapitalMP3"),
    ("SomaFM Lush",          "Vocal chill", "http://ice1.somafm.com/lush-128-mp3"),
    ("SomaFM Indie Pop",     "Indie pop",   "http://ice1.somafm.com/indiepop-128-mp3"),
    ("SomaFM Secret Agent",  "Spy lounge",  "http://ice1.somafm.com/secretagent-128-mp3"),
    ("SomaFM Deep Space One","Deep ambient","http://ice1.somafm.com/deepspaceone-128-mp3"),
    ("WFMU",                 "Free-form US","http://stream0.wfmu.org/freeform-128k.mp3"),
    ("WNYC FM",              "News/talk US","https://fm939.wnyc.org/wnycfm.aac"),
    ("KCRW Eclectic",        "Eclectic LA", "https://kcrw.streamguys1.com/kcrw_192k_mp3_e24"),
    ("Radio Paradise Mellow","Mellow mix",  "http://stream.radioparadise.com/mellow-128"),
    ("Radio Paradise Rock",  "Rock mix",    "http://stream.radioparadise.com/rock-128"),
    ("Radio Swiss Jazz",     "Jazz CH",     "http://stream.srg-ssr.ch/m/rsj/mp3_128"),
    ("Radio Swiss Classic",  "Classical CH","http://stream.srg-ssr.ch/m/rsc_de/mp3_128"),
    ("FluxFM Berlin",        "Indie DE",    "http://streams.fluxfm.de/Flux/mp3-320/streams.fluxfm.de/"),
    ("Radio Nova FR",        "Eclectic FR", "http://novazz.ice.infomaniak.ch/novazz-128.mp3"),
    ("ABC Jazz",             "Jazz AU",     "https://live-radio01.mediahubaustralia.com/2JAZW/mp3/"),
    ("Triple J",             "Pop AU",      "https://live-radio01.mediahubaustralia.com/2TJW/mp3/"),
    ("CBC Radio One",        "News CA",     "https://cbcliveradio-lh.akamaihd.net/i/CBCR1_TOR@392010/master.m3u8"),
    ("Venice Classic Radio", "Classical IT","http://174.36.206.197:8000/stream"),
    ("RNE Radio Nacional",   "News ES",     "http://crtve-livehls-amd.akamaized.net/hls-live/livepkgr/_definst_/liveevent/mp4_p1/RNE_Radio_Nacional@393937/RNE_Radio_Nacional_1.m3u8"),
]

def fetch_head(url, follow=4, timeout=6):
    """GET first ~32 KB of a URL, follow redirects, return (status, headers, body, final_url)."""
    cur = url
    for hop in range(follow + 1):
        u = urllib.parse.urlparse(cur)
        host = u.hostname
        port = u.port or (443 if u.scheme == "https" else 80)
        path = u.path or "/"
        if u.query:
            path += "?" + u.query
        sock = socket.create_connection((host, port), timeout=timeout)
        if u.scheme == "https":
            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(sock, server_hostname=host)
        req = (
            f"GET {path} HTTP/1.0\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: esp-radio-probe/1.0\r\n"
            f"Icy-MetaData: 1\r\n"
            f"Range: bytes=0-32767\r\n"
            f"Connection: close\r\n\r\n"
        ).encode()
        sock.sendall(req)
        buf = b""
        sock.settimeout(timeout)
        try:
            while len(buf) < 65536:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                buf += chunk
        except socket.timeout:
            pass
        sock.close()
        if b"\r\n\r\n" not in buf:
            return None, {}, b"", cur
        head, body = buf.split(b"\r\n\r\n", 1)
        lines = head.decode("iso-8859-1", "replace").split("\r\n")
        status_line = lines[0]
        try:
            status = int(status_line.split(" ", 2)[1])
        except Exception:
            return None, {}, b"", cur
        headers = {}
        for ln in lines[1:]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        if status in (301, 302, 303, 307, 308) and "location" in headers and hop < follow:
            cur = urllib.parse.urljoin(cur, headers["location"])
            continue
        return status, headers, body, cur
    return None, {}, b"", cur

def looks_like_mp3(b):
    # Search for an MP3 frame sync 0xFFE/F in the first 4 KB. This catches
    # streams that prefix ID3 tags or that prepend a few bytes of metadata.
    for i in range(min(len(b) - 1, 4096)):
        if b[i] == 0xFF and (b[i+1] & 0xE0) == 0xE0:
            return True
    return b[:3] == b"ID3"

def looks_like_aac(b):
    for i in range(min(len(b) - 1, 4096)):
        if b[i] == 0xFF and (b[i+1] & 0xF6) == 0xF0:  # AAC ADTS sync
            return True
    return False

def is_hls(headers, final_url):
    ct = headers.get("content-type", "")
    return ("mpegurl" in ct.lower()) or final_url.endswith((".m3u8", ".m3u"))

def assess(name, genre, url):
    t0 = time.time()
    try:
        status, headers, body, final = fetch_head(url)
    except Exception as e:
        return {"name": name, "url": url, "ok": False, "reason": f"net error: {e}"}
    elapsed = time.time() - t0
    if not status:
        return {"name": name, "url": url, "ok": False, "reason": "no response"}
    ct = headers.get("content-type", "")
    if status not in (200, 206):
        return {"name": name, "url": url, "ok": False,
                "reason": f"HTTP {status}, ct={ct}", "elapsed": elapsed}
    if is_hls(headers, final):
        return {"name": name, "url": url, "ok": False,
                "reason": "HLS playlist (not supported by simple_player)", "ct": ct}
    if looks_like_mp3(body):
        kind = "mp3"
    elif looks_like_aac(body):
        kind = "aac"
    else:
        # Some shoutcast servers identify via Content-Type only.
        if "audio" in ct or "mpeg" in ct or "aac" in ct:
            kind = "audio (by ct)"
        else:
            return {"name": name, "url": url, "ok": False,
                    "reason": f"no mp3/aac sync in body, ct={ct}, body[:8]={body[:8]!r}"}
    icy = "icy-metaint" in headers
    return {"name": name, "genre": genre, "url": url, "ok": True,
            "kind": kind, "ct": ct, "icy": icy,
            "final": final, "elapsed_s": round(elapsed, 2)}

results = []
for name, genre, url in CANDIDATES:
    print(f"probing {name:24s} ...", end=" ", flush=True)
    r = assess(name, genre, url)
    if r["ok"]:
        print(f"OK  ({r['kind']}, {r.get('ct','?')}, icy={r['icy']}, {r['elapsed_s']}s)")
    else:
        print(f"FAIL: {r.get('reason','?')}")
    results.append(r)

print("\n=== SUMMARY ===")
for r in results:
    flag = "OK " if r["ok"] else "FAIL"
    print(f"  {flag}  {r['name']:24s}  {r.get('reason') or r.get('kind')}")

print("\n=== KEEPERS (paste into stations.h) ===")
for r in results:
    if r["ok"]:
        # Use final URL after redirects so the device doesn't have to follow them.
        u = r.get("final", r["url"])
        print(f'    {{ "{r["name"]:<22s}", "{r.get("genre",""):<12s}", "{u}" }},')
