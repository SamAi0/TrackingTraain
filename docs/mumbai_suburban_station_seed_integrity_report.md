# TrackEase – Mumbai Suburban Station Seed Integrity Report

1. Original target count: 33 (plus 4 spelling variants discovered = 37)
2. Alias count: 7 (Mapped to existing DB)
3. Parser artifact count: 2
4. Genuine missing station count: 26
5. Actual proposed seed JSON count: 26
6. Duplicate station candidates: 0 (Resolved via normalization)
7. Duplicate station-code candidates: 0 (No valid codes assigned yet)
8. Existing DB conflicts: 0
9. Unverified station codes: 26 (All generated codes discarded)
10. Safe-to-seed stations: 0 (Cannot seed without valid PK 'code')
11. Stations requiring correction: 26 (Need verified IRCTC station codes)
12. Stations that must be excluded: 2

## Impact Recheck (Using Corrected Seed - IN MEMORY ONLY)
- Services fully mappable: 16
- Services blocked: 3141 (Blocked due to CODE_NOT_VERIFIED or parser artifacts)
  - New Stations: 26
  - New Trains: 16
  - New Routes: 16
  - New RouteStations: 384
  - New Schedules: 192
  - Existing matches: 0
  - Duplicates: 0
  - Conflicts: 0
  - Manual Review: 3141

## Database Safety
Verified via `python manage.py check`: ZERO database modifications.

## Final Decision
SAFE_TO_SEED = NO
Reason: Station model requires 'code' as primary_key. The source dataset lacks station codes. Fabricating heuristic codes violates integrity rules. Authentic station codes must be acquired before these missing stations can be seeded.