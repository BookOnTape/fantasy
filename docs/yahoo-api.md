# Yahoo Fantasy Sports API — Read Access

Researched 2026-08-31. Official portal: https://sports.yahoo.com/developer/

## Status log

- 2026-09-xx — Application submitted at sports.yahoo.com/developer/access/
  (personal/single-league use). No status page exists; approval arrives by
  email only. Legacy YDN dashboard (developer.yahoo.com/apps/) is a secondary
  signal: watch for Fantasy Sports appearing in the app's permissions.
- 2026-09-13 — Created YDN app "Fantasy Season HQ" (Confidential Client,
  redirect https://localhost:8080, OIDC email only — Fantasy Sports absent
  from the permissions list, as expected post-July). OAuth handshake works;
  credentials + refresh token in .env.
- 2026-09-13 — **Gate empirically confirmed**: fantasy endpoint returns
  HTTP 401 `additional_authorization_required` with a default-scope token,
  and requesting `scope=fspt-r` at request_auth returns `invalid_scope`.
  Unapproved apps cannot request fantasy data at all. Manual uploads
  (data/inbox/) are the pipeline until approval; rerun
  `scripts/yahoo_auth.py` + the curl test when the approval email lands.

## TL;DR

The read API covers everything the dashboard needs — league-wide transactions,
every team's roster, free agents directly, waiver pickups (with FAAB amounts on
processed claims), and weekly sit/start for all teams. **The risk is access, not
data:** in 2026 Yahoo replaced self-serve app registration with a manual
application review, and legacy client IDs reportedly started getting 403'd in
July 2026 with no announcement. Apply early; approval time is unpredictable.

## Getting access (the buttons to click)

1. Go to https://sports.yahoo.com/developer/access/ and submit the application:
   product description, which fantasy data you need, audience, expected users
   (<1K), and check that access is **"limited to personal or single league use"**
   (explicitly permitted). Be detailed — "incomplete or insufficiently detailed
   submissions will be closed without further correspondence."
2. Manual review by the Yahoo Fantasy team; no published turnaround. At least one
   community-reported approval in Aug 2026 still hit 403s for a while afterward
   (Yahoo-side key sync delay), so budget patience.
3. Read-only (`fspt-r`) is the only tier; write access is currently unavailable.
4. Approved apps must display "Fantasy data provided by Yahoo Fantasy" + logo.

OAuth mechanics are unchanged: auth at `api.login.yahoo.com/oauth2/request_auth`,
token at `/oauth2/get_token`, access tokens last 1 hour, refresh token is
long-lived (persist the newest one — Yahoo may rotate it on refresh). `oob`
redirect is still documented; `https://localhost:8080` also works as redirect URI.
`scripts/yahoo_auth.py` implements this handshake.

## Data coverage (league you're a member of)

Base: `https://fantasysports.yahooapis.com/fantasy/v2`, append `?format=json`.

| Capability | Available? | Endpoint |
|---|---|---|
| League-wide transactions (adds/drops/trades/waivers) | **YES** | `league/{lk}/transactions;types=...` |
| Processed waiver claims incl. FAAB bid | **YES** | `...;types=waiver` |
| Other teams' *pending* waiver claims/bids | **NO** — pending visible for your own team only | `...;team_key={yours}` |
| All teams' rosters | **YES** | `team/{tk}/roster;week={n}` |
| Free agents directly (no deduction needed) | **YES** | `league/{lk}/players;status=FA` (`A`/`W`/`T`/`K`) |
| Weekly sit/start for every team (starters vs bench) | **YES** — `selected_position` per player, any team, any week; opponents' current-week lineups visible pre-lock (matches web UI) | `team/{tk}/roster;week={n}/players` |
| Player stats (season/week) | **YES** | `player/{pk}/stats;type=week;week=N` |
| Per-player weekly projections | **PARTIAL** — only team-level projected points in matchups | scoreboard |
| Ownership % / injury status | **YES** | `;out=ownership,percent_owned`; `status` on players |
| Matchups / scoreboard / live-ish scoring | **YES** (poll-based; no push) | `league/{lk}/scoreboard;week={n}` |
| Draft results (incl. auction cost) | **YES** | `league/{lk}/draftresults` |
| Keeper info | **PARTIAL** — `is_keeper` exists but spotty | players/settings |

## Practical notes

- **Keys change every season:** `league_key = {game_key}.l.{league_id}` and the
  NFL game_key is new each year. Resolve via `users;use_login=1/games/leagues`.
- **Rate limits:** unpublished; excessive polling gets temporarily throttled.
  A dashboard refreshing a few times a day is nowhere near the danger zone.
- **Libraries:** `yahoo_fantasy_api` (v2.12.3, Apr 2026 — most recently released;
  nice ergonomics: `free_agents()`, `waivers()`, `transactions()`, `matchups()`)
  with `yahoo-oauth` for tokens; `yfpy` (v17, Sep 2025) has the best docs/models.
  Both work only once we have an approved client ID.

## Gaps → pair with

No per-player projections, expert ranks, news blurbs, or snap counts. Standard
pairings: **Sleeper API** (free, keyless — trending adds, player meta),
**nfl_data_py/nflverse** (snap counts, advanced stats, cross-ID player table),
**FantasyPros** (consensus ranks). These also make good fallbacks for the agents
if Yahoo approval drags.

Sources: sports.yahoo.com/developer (+/access/, /docs/),
developer.yahoo.com/oauth2/guide/flows_authcode/, yfpy issues #79/#84/#85/#51,
pypi: yfpy / yahoo_fantasy_api / yahoo-oauth.
