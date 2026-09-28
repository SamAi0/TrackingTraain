# TrackEase – Mumbai Suburban Station Code Verification Report

A. Total missing stations (initially evaluated): 26
B. Verified codes (Truly Missing & Safe to Seed): 19
C. Unverified stations: 0
D. Conflicting codes (Different physical station): 0
E. Existing DB conflicts (Same physical station/Alias found): 7

F. Source used for each verified code: Official IRCTC standard station lists (Indian Railways).
G. Corridor-wise breakdown: All mapped to Mumbai Suburban.
H. Final recommendation: The 19 VERIFIED stations should be seeded into the database. The 7 Existing DB conflicts are the exact same physical stations already present in the DB under slightly different spellings (e.g. KANDIVALI -> KANDIVLI). They should be handled as alias mappings rather than new seeded stations.

## Detailed Table

| Source station | Canonical station | Verified code | Status | Source |
|---|---|---|---|---|
| KHOPOLI | KHOPOLI | KHPI | VERIFIED | IRCTC |
| LOWJEE | LOWJEE | LWJ | VERIFIED | IRCTC |
| DOLAVLI | DOLAVLI | DLV | VERIFIED | IRCTC |
| KELAVLI | KELAVLI | KLY | VERIFIED | IRCTC |
| CSMT | CSMT | CSMT | VERIFIED | IRCTC |
| DOCKYARD ROAD | DOCKYARD ROAD | DKRD | VERIFIED | IRCTC |
| REAY ROAD | REAY ROAD | RRD | VERIFIED | IRCTC |
| COTTON GREEN | COTTON GREEN | CTGN | VERIFIED | IRCTC |
| SEWRI | SEWRI | SVE | VERIFIED | IRCTC |
| KING'S CIRCLE | KING'S CIRCLE | KCE | VERIFIED | IRCTC |
| CHEMBUR | CHEMBUR | CMBR | VERIFIED | IRCTC |
| GOVANDI | GOVANDI | GV | VERIFIED | IRCTC |
| MANKHURD | MANKHURD | MNKD | VERIFIED | IRCTC |
| SEAWOODSDARAWE | SEAWOODSDARAWE | SWDV | VERIFIED | IRCTC |
| CHURCHGATE | CHURCHGATE | CCG | VERIFIED | IRCTC |
| MARINE LINES | MARINE LINES | MEL | VERIFIED | IRCTC |
| GRANT ROAD | GRANT ROAD | GTR | VERIFIED | IRCTC |
| PRABHADEVI | PRABHADEVI | PBHD | VERIFIED | IRCTC |
| RAM MANDIR | RAM MANDIR | RMAR | VERIFIED | IRCTC |
| PALASDHARI | PALASDHARI | PDI | EXISTING_DB_ALIAS (PALASDARI) | IRCTC |
| THAKURLI | THAKURLI | THK | EXISTING_DB_ALIAS (THAKRULI) | IRCTC |
| KHAR ROAD | KHAR ROAD | KHAR | EXISTING_DB_ALIAS (KHAR) | IRCTC |
| SANTACRUZ | SANTACRUZ | STC | EXISTING_DB_ALIAS (SANTA CRUZ) | IRCTC |
| NALLASOPARA | NALLASOPARA | NSP | EXISTING_DB_ALIAS (NALLA SOPARA) | IRCTC |
| KELVE ROAD | KELVE ROAD | KLV | EXISTING_DB_ALIAS (KELVA ROAD) | IRCTC |
| KANDIVALI | KANDIVALI | KILE | EXISTING_DB_ALIAS (KANDIVLI) | IRCTC |