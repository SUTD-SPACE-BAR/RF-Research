# D2 — Reddit gap analysis (W4-D2)

Status: **in progress** (2026-09-29). Owner: W4-D2. Log: `research-logs/W4-D2-reddit.md`. Companion: `gaps/D1-stackexchange.md` (Stack Exchange sweep) — this file focuses on what Reddit adds.

## 0. Method (short)

- **Access.** reddit.com JSON (`/top.json`, `api.reddit.com`) returns HTTP 403 to unauthenticated clients and
  old.reddit redirects to a login page; the public RSS feeds work but are rate-limited to about one request per
  minute and carry no scores. PullPush refuses automated clients. So posts were harvested read-only from the
  **Arctic Shift** Reddit archive API (raw JSON with `score` and `num_comments`; scores of old posts are current,
  not frozen at ingestion — checked on rfelectronics), and keyword searches were run through **Reddit's own search
  RSS** (`/r/<sub>/search.rss?q=…&restrict_sr=on&sort=top&t=all`, top 100 per query) with scores then looked up by id
  in Arctic Shift. No login, posting or voting. Only titles (paraphrased here) and counts were used; no comment text
  is reproduced.
- **What was harvested.** Full post history (2011–2026-09) of r/rfelectronics (14 054 posts), r/sdr, r/GNURadio,
  r/Radar, r/LoRa, r/HighPowerRocketry, r/HamRadio, r/DSP; r/amateurradio posts flaired QUESTION/ANTENNA/PROPAGATION;
  r/RTLSDR posts flaired Troubleshooting / DIY Projects/questions / Antennas; r/meshtastic 2024–2026; top-100
  keyword searches in r/AskElectronics, r/ElectricalEngineering, r/PrintedCircuitBoard, r/ECE, r/rocketry,
  r/amateurradio, r/meshtastic, r/RTLSDR, r/rfelectronics. r/antennas is not in the archive (r/Antenna is tiny) and
  r/HighPowerRocketry has only 38 archived posts, so rocketry radio questions come from r/rocketry searches.
- **Selection.** Question-like titles ("?", question words, or a question flair) ranked by score per subreddit;
  the top of each list was read by hand and off-topic posts dropped (showcases, memes, repair of consumer gear, buying
  a specific radio, licence-exam admin, pure software bugs). "What is this antenna/signal/connector?" photo posts
  were kept (sampled, not all) because they reveal an identification gap. Career questions are kept (domain CAR,
  status out-of-scope) only to inform §4.
- **Coverage check.** Against the live "Questions this page answers" lists of every kb/ page (re-extracted during
  the run because pages kept landing), FAQ.md, and grep of kb/ for the key terms; the section was opened when unsure.
  **covered** = a page answers this specific question; **partial** = the topic is there but the specific point,
  misconception or practical step is not; **missing** = nothing usable. Spot-checks of "covered" calls are logged in §0
  of the log and summarised at the end of this section.
