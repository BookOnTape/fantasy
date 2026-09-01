# Research Agents

Specs for the scheduled agents that keep the season dashboard current. Each agent
gets its own spec file here once the Yahoo data layer is proven out; the schedule
lives in [docs/architecture.md](../docs/architecture.md).

Planned:
- `waiver-scout.md` — Tuesday-night waiver target research
- `sit-start.md` — Thu/Sun lineup check for my roster
- `league-monitor.md` — daily transaction/roster diff
- `week-recap.md` — Tuesday-morning recap + look-ahead

Output convention: agents write dated markdown reports to `data/reports/YYYY-WW/`
which the dashboard surfaces.
