"""
Dashboard generator for the Hope Index.

Reads the SQLite time series (hope.db) and writes a single self-contained
dashboard.html — same editorial charte as The Miracle Index (warm paper,
Fraunces / Newsreader, claret accent). No server, no CDN chart library:
the chart is hand-drawn SVG fed by the embedded data.

    python build_dashboard.py                 # read hope.db
    python build_dashboard.py --demo          # synthetic match-day arc (for preview)
    python build_dashboard.py --opponent Spain --out dashboard.html

Cron it right after run.py so the page is always fresh:
    0 * * * * cd ~/hope_index && .venv/bin/python run.py --opponent Haiti && \
              .venv/bin/python build_dashboard.py --opponent Haiti
"""
import argparse
import json
import math
import sqlite3
from datetime import datetime, timedelta, timezone


def load_db(db="hope.db", team="MAR"):
    try:
        c = sqlite3.connect(db)
        rows = c.execute(
            "SELECT ts,hope,mood,volume,intensity,stat_hope,belief_gap "
            "FROM hope WHERE team=? ORDER BY ts", (team,)).fetchall()
        c.close()
    except Exception:
        return []
    keys = ["ts", "hope", "mood", "volume", "intensity", "stat_hope", "belief_gap"]
    return [dict(zip(keys, r)) for r in rows]


def demo_series(opponent="Spain", stat=28.0):
    """A synthetic match-day arc so the dashboard looks alive in preview."""
    base = datetime(2026, 6, 24, 16, 0, tzinfo=timezone.utc)
    script = [  # (minutes_from_start, hope, volume, note)
        (0,   58, 120, "Morning: quiet hope"),
        (120, 63, 180, "Build-up"),
        (200, 69, 340, "Pre-match nerves"),
        (240, 72, 520, "Kickoff"),
        (262, 78, 910, "Morocco pressing"),
        (271, 91, 1480, "GOAL — Morocco lead"),
        (285, 86, 1010, "Holding the lead"),
        (300, 83, 880, "Half-time"),
        (320, 80, 760, "Second half"),
        (352, 64, 1190, "Opponent equalises"),
        (366, 49, 1620, "Panic"),
        (378, 41, 1380, "Pinned back"),
        (393, 55, 900, "Stabilising"),
        (405, 60, 1020, "Late push"),
        (415, 47, 1740, "Extra time looms"),
        (430, 38, 1980, "Penalties"),
        (438, 94, 2600, "WON on penalties"),
        (455, 88, 1500, "Relief"),
        (520, 79, 760, "Celebration settles"),
    ]
    out = []
    for mins, hope, vol, note in script:
        ts = (base + timedelta(minutes=mins)).isoformat()
        out.append({"ts": ts, "hope": hope, "mood": round(hope / 50 - 1, 3),
                    "volume": vol, "intensity": round(vol / 600, 2),
                    "stat_hope": stat, "belief_gap": round(hope - stat, 1),
                    "note": note})
    return out


def render(series, opponent, out_path="dashboard.html"):
    payload = json.dumps(series)
    latest = series[-1] if series else {"hope": 50, "stat_hope": None, "belief_gap": None}
    gap = latest.get("belief_gap")
    verdict = "—"
    if gap is not None:
        verdict = "Faith" if gap > 0 else "Doubt"
    cur_hope = latest.get("hope", 50)
    cur_stat = latest.get("stat_hope")

    html = _TEMPLATE
    repl = {
        "__DATA__": payload,
        "__OPP__": opponent or "—",
        "__CUR_HOPE__": f"{cur_hope:.0f}",
        "__CUR_STAT__": ("%.0f" % cur_stat) if cur_stat is not None else "—",
        "__GAP__": (f"{gap:+.1f}" if gap is not None else "—"),
        "__VERDICT__": verdict,
        "__N__": str(len(series)),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    with open(out_path, "w") as f:
        f.write(html)
    return out_path


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Hope Index — Morocco</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">
<style>
  :root{
    --paper:#f3efe6;--paper2:#f8f5ed;--ink:#211d18;--ink-soft:#403a32;--mut:#8a8073;
    --line:rgba(33,29,24,.14);--line-soft:rgba(33,29,24,.08);
    --accent:#7c2e2c;--accent-soft:#a9534f;
    --disp:'Fraunces',Georgia,serif;--read:'Newsreader',Georgia,serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:var(--paper);color:var(--ink);font-family:var(--read);font-size:18px;
    line-height:1.7;-webkit-font-smoothing:antialiased;font-feature-settings:"onum" 1}
  body::after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.025;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
  .wrap{position:relative;z-index:1;max-width:860px;margin:0 auto;padding:0 26px}
  .eyebrow{font-size:13px;letter-spacing:.26em;text-transform:uppercase;color:var(--accent);
    font-weight:500;display:flex;align-items:center;gap:14px}
  .eyebrow::before{content:"";width:30px;height:1px;background:var(--accent);display:inline-block;opacity:.6}
  header{padding:80px 0 0}
  h1{font-family:var(--disp);font-weight:500;font-size:clamp(48px,9vw,86px);line-height:.98;
    letter-spacing:-.02em;margin:26px 0 0}
  h1 em{font-style:italic;color:var(--accent)}
  .deck{font-style:italic;color:var(--ink-soft);font-size:clamp(19px,2.4vw,23px);margin-top:22px;max-width:620px}
  .rule{height:1px;background:var(--line);margin:46px 0;border:0}

  .reading{display:flex;flex-wrap:wrap;gap:34px;align-items:flex-end;margin:8px 0 6px}
  .reading .big{font-family:var(--disp);font-size:clamp(72px,15vw,120px);font-weight:500;
    color:var(--accent);line-height:.8;letter-spacing:-.03em}
  .reading .col .l{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut)}
  .reading .col .v{font-family:var(--disp);font-size:34px;color:var(--ink);margin-top:2px}
  .verdict{font-family:var(--disp);font-style:italic;font-size:26px}
  .verdict.faith{color:var(--accent)} .verdict.doubt{color:var(--ink-soft)}
  .ctx{font-style:italic;color:var(--mut);font-size:16px;margin-top:10px}

  .chartwrap{margin:30px 0 0}
  .legend{display:flex;gap:26px;flex-wrap:wrap;font-size:14px;color:var(--ink-soft);margin-bottom:14px}
  .legend i{display:inline-block;width:22px;height:0;vertical-align:middle;margin-right:8px}
  .legend .e i{border-top:2px solid var(--accent)}
  .legend .s i{border-top:2px dashed var(--ink-soft)}
  .legend .f{color:var(--accent)} .legend .d{color:var(--mut)}
  svg{width:100%;height:auto;display:block;overflow:visible}
  .ax{font-family:var(--read);font-size:12px;fill:var(--mut)}
  .gl{stroke:var(--line-soft);stroke-width:1}
  .baseline{stroke:var(--line);stroke-width:1}

  .vol{margin-top:30px}
  .vol .cap{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);margin-bottom:8px}

  h2{font-family:var(--disp);font-weight:500;font-size:clamp(26px,5vw,38px);margin:0 0 8px}
  .method{color:var(--ink-soft);font-size:16px;line-height:1.8}
  .method b{color:var(--ink);font-weight:500}
  footer{margin:54px 0 56px;padding-top:24px;border-top:1px solid var(--line);
    font-size:14px;font-style:italic;color:var(--mut)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">A Live Reading &nbsp;·&nbsp; Morocco &nbsp;·&nbsp; World Cup 2026</div>
    <h1>The <em>Hope</em> Index</h1>
    <p class="deck">How far a nation's heart drifts from the arithmetic — measured hour by hour, against the cold expectation of the model.</p>
  </header>

  <hr class="rule">

  <div class="eyebrow">The Latest Reading &nbsp;·&nbsp; vs __OPP__</div>
  <div class="reading">
    <div class="big">__CUR_HOPE__</div>
    <div class="col"><div class="l">Emotional hope</div><div class="v">__CUR_HOPE__/100</div></div>
    <div class="col"><div class="l">Statistical hope (Elo)</div><div class="v">__CUR_STAT__/100</div></div>
    <div class="col"><div class="l">Belief gap</div><div class="v">__GAP__</div></div>
    <div class="col"><div class="l">Verdict</div><div class="verdict __VERDICT___c">__VERDICT__</div></div>
  </div>
  <p class="ctx">When the crowd believes more than the model, the band glows claret — <em>faith</em>. When it believes less, it falls to grey — <em>doubt</em>. The story is the gap.</p>

  <div class="chartwrap">
    <div class="legend">
      <span class="e"><i></i>Emotional hope (the crowd)</span>
      <span class="s"><i></i>Statistical hope (Elo)</span>
      <span class="f">▩ Faith</span>
      <span class="d">▩ Doubt</span>
    </div>
    <svg id="chart" viewBox="0 0 860 380" preserveAspectRatio="xMidYMid meet"></svg>
  </div>

  <div class="vol">
    <div class="cap">Attention — volume of posts per reading</div>
    <svg id="vol" viewBox="0 0 860 90" preserveAspectRatio="none"></svg>
  </div>

  <hr class="rule">

  <h2>Reading the gap</h2>
  <p class="method">The <b>emotional hope</b> line is drawn from real posts on YouTube and Bluesky —
  scored in English, French, Arabic and Darija by a multilingual model — and mapped to a 0–100 mood.
  The <b>statistical hope</b> line is the Elo win expectation for Morocco's next opponent, the same
  engine behind The Miracle Index. The shaded band between them is the <b>belief gap</b>: a nation's
  faith, or its doubt, made visible.</p>

  <footer>The Hope Index · companion to The Miracle Index · __N__ readings · auto-generated from hope.db</footer>
</div>

<script>
const DATA = __DATA__;
const W=860;

function draw(){
  if(!DATA.length){return;}
  const H=380, L=46, R=18, T=20, B=42;
  const iw=W-L-R, ih=H-T-B;
  const n=DATA.length;
  const x=i=> L + (n<=1?iw/2:(i/(n-1))*iw);
  const y=v=> T + (1-v/100)*ih;

  let svg="";
  // gridlines + y labels
  [0,25,50,75,100].forEach(g=>{
    const yy=y(g).toFixed(1);
    svg+=`<line class="gl" x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}"/>`;
    svg+=`<text class="ax" x="${L-10}" y="${(+yy+4)}" text-anchor="end">${g}</text>`;
  });
  // 50 baseline emphasised
  svg+=`<line class="baseline" x1="${L}" y1="${y(50)}" x2="${W-R}" y2="${y(50)}"/>`;

  // build faith/doubt band polygons between emotional and stat lines (per segment)
  const hasStat = DATA.every(d=>d.stat_hope!=null);
  if(hasStat){
    for(let i=0;i<n-1;i++){
      const xa=x(i),xb=x(i+1);
      const ea=y(DATA[i].hope), eb=y(DATA[i+1].hope);
      const sa=y(DATA[i].stat_hope), sb=y(DATA[i+1].stat_hope);
      // faith if emotional above stat (smaller y). Colour by midpoint.
      const faith = ((DATA[i].hope+DATA[i+1].hope)/2) >= ((DATA[i].stat_hope+DATA[i+1].stat_hope)/2);
      const fill = faith? "rgba(124,46,44,.16)":"rgba(33,29,24,.10)";
      svg+=`<polygon points="${xa},${ea} ${xb},${eb} ${xb},${sb} ${xa},${sa}" fill="${fill}" stroke="none"/>`;
    }
    // stat line (dashed)
    let sp="";DATA.forEach((d,i)=>sp+=(i?"L":"M")+x(i).toFixed(1)+","+y(d.stat_hope).toFixed(1)+" ");
    svg+=`<path d="${sp}" fill="none" stroke="var(--ink-soft)" stroke-width="1.5" stroke-dasharray="5 4" opacity=".7"/>`;
  }
  // emotional line
  let ep="";DATA.forEach((d,i)=>ep+=(i?"L":"M")+x(i).toFixed(1)+","+y(d.hope).toFixed(1)+" ");
  svg+=`<path d="${ep}" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round"/>`;
  // dots + annotate peaks/troughs lightly
  DATA.forEach((d,i)=>{
    svg+=`<circle cx="${x(i).toFixed(1)}" cy="${y(d.hope).toFixed(1)}" r="3" fill="var(--accent)"/>`;
  });
  // x labels (first, middle, last + any 'note' extremes)
  const fmt=ts=>{const dt=new Date(ts);return dt.toLocaleString('en-GB',{hour:'2-digit',minute:'2-digit'});};
  const idxs=[...new Set([0,Math.floor(n/2),n-1])];
  idxs.forEach(i=>{svg+=`<text class="ax" x="${x(i).toFixed(1)}" y="${H-16}" text-anchor="middle">${fmt(DATA[i].ts)}</text>`;});

  // annotate the single highest and lowest emotional points
  let hi=0,lo=0;DATA.forEach((d,i)=>{if(d.hope>DATA[hi].hope)hi=i;if(d.hope<DATA[lo].hope)lo=i;});
  [[hi,'var(--accent)'],[lo,'var(--ink-soft)']].forEach(([i,c])=>{
    if(DATA[i].note){
      const yy=y(DATA[i].hope);const above=DATA[i].hope<70;
      svg+=`<text class="ax" x="${x(i).toFixed(1)}" y="${(above?yy-12:yy+20).toFixed(1)}" text-anchor="middle" fill="${c}" font-style="italic" font-size="12.5">${DATA[i].note}</text>`;
    }
  });

  document.getElementById('chart').innerHTML=svg;

  // volume strip
  const vmax=Math.max(...DATA.map(d=>d.volume||0),1);
  const VH=90, vb=10;
  let vs="";const bw=(W-L-R)/n*0.6;
  DATA.forEach((d,i)=>{
    const h=((d.volume||0)/vmax)*(VH-vb-6);
    const xx=x(i)-bw/2;
    vs+=`<rect x="${xx.toFixed(1)}" y="${(VH-vb-h).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="var(--mut)" opacity=".5"/>`;
  });
  vs+=`<line x1="${L}" y1="${VH-vb}" x2="${W-R}" y2="${VH-vb}" class="baseline"/>`;
  document.getElementById('vol').innerHTML=vs;
}
draw();

// light auto-reload for match days (no server needed; just re-pulls the regenerated file)
// comment out if you don't want it:
setTimeout(()=>location.reload(), 1000*60*5);
</script>
</body>
</html>
"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--opponent", default="Haiti")
    ap.add_argument("--out", default="dashboard.html")
    ap.add_argument("--db", default="hope.db")
    a = ap.parse_args()

    if a.demo:
        s = demo_series(a.opponent)
    else:
        s = load_db(a.db)
        if len(s) < 2:
            print(f"[dashboard] hope.db has {len(s)} point(s) — not enough yet. "
                  f"Rendering a demo arc so you can see the layout. "
                  f"Re-run without --demo once more readings accumulate.")
            s = demo_series(a.opponent)

    path = render(s, a.opponent, a.out)
    print(f"[dashboard] wrote {path} ({len(s)} readings)")
