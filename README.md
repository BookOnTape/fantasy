# Fantasy Football Season HQ

Season dashboard + research agents for the 2026 fantasy football season.

## What this is

- **Dashboard** — a web dashboard (published online) tracking the league and season: standings, matchups, transactions, waiver activity, and weekly sit/start intel.
- **Agents** — auto-running research agents that do the legwork before each week starts (and ideally throughout the week): waiver-wire targets, injury news, matchup analysis, league transaction monitoring.
- **Yahoo integration** — read-only access to the Yahoo Fantasy league via the Yahoo Fantasy Sports API (OAuth), pulling rosters, transactions, free agents, and lineups.

## Layout

```
fantasy/
├── README.md
├── docs/
│   ├── yahoo-api.md        # What the Yahoo read API can/can't do, auth setup
│   └── architecture.md     # Dashboard + agent design
├── dashboard/              # The season dashboard (web)
├── agents/                 # Agent prompts/specs for scheduled research runs
├── scripts/                # Yahoo OAuth + data-pull scripts
├── data/                   # Pulled league data snapshots (JSON)
└── .env.example            # Yahoo API credentials template (never commit .env)
```

## Status

- [x] Repo scaffolded, connected to `BookOnTape/fantasy`
- [ ] Yahoo developer app registered (requires clicking through developer.yahoo.com)
- [ ] OAuth flow working, first league data pull
- [ ] Dashboard v1
- [ ] Scheduled agents wired up
