# TrackEase – Mumbai Suburban Data Sources (Verified)

| Corridor | Source | Category | Actual format | Route sequence | Timings | Running days | Currentness | License | Status |
|---|---|---|---|---|---|---|---|---|---|
| Western | `Umang-Lodaya/Mumbai-Local-TimeTable-Extractor` | D (Scraped) | CSV | YES | YES | PARTIAL | 2023 | MIT | VERIFIED |
| Central | `Umang-Lodaya/Mumbai-Local-TimeTable-Extractor` | D (Scraped) | CSV | YES | YES | PARTIAL | 2023 | MIT | VERIFIED |
| Harbour | `Umang-Lodaya/Mumbai-Local-TimeTable-Extractor` | D (Scraped) | CSV | YES | YES | PARTIAL | 2023 | MIT | VERIFIED |
| Trans-Harbour | Existing TrackEase data | A (Official-derived) | JSON | YES | YES | NO | 2024 | N/A | VERIFIED |
| Uran | Official CR PDF / Press Release | A (Official) | PDF | YES | YES | YES | 2024 | Gov Open | VERIFIED (Needs manual parsing) |
| Vasai-Diva | `Umang-Lodaya/Mumbai-Local-TimeTable-Extractor` | D (Scraped) | CSV | YES | YES | PARTIAL | 2023 | MIT | VERIFIED |
| Panvel-Karjat | `Umang-Lodaya/Mumbai-Local-TimeTable-Extractor` | D (Scraped) | CSV | YES | YES | PARTIAL | 2023 | MIT | VERIFIED |

**Note on rejected sources:**
- **Kaggle (anirudh...unsplash)**: `UNVERIFIED` - URL is invalid/hallucinatory and does not point to a railway dataset.
- **`railpull` (NTES extractor)**: `REJECTED` - NTES API explicitly returns `Invalid Train No./Name` for Mumbai Local trains (e.g., 99001, 90011). NTES does not track the 9xxxx Mumbai suburban services.
