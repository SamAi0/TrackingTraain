# TrackEase – Mumbai Suburban Data Quality Audit

This is a read-only audit of the parsed data.

## Central
- Actual services: 1646
- Actual unique stations: 99
- Valid timetable cells: 30180
- Blank cells: 35345
- Annotation cells: 0
- Invalid cells: 5095
- Duplicate groups: 8

**10 Missing Time Examples:**
- Source: `Table - 1.csv`, Train: 99001, Station: SNPD, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99001, Station: VSH, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99003, Station: SNPD, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99003, Station: VSH, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: JNJ, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: NEU, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: SWDV, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: BEPR, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: KHAG, Reason: blank, Raw: ``
- Source: `Table - 1.csv`, Train: 99401, Station: MANR, Reason: blank, Raw: ``

**10 Invalid Time Examples:**
- Source: `Table - 17.csv`, Train: 95902, Station: Nahur, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Bhandup, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Kanjur Marg, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Vikhroli, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Vidyavihar, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Sion, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Matunga, Raw: `...`
- Source: `Table - 17.csv`, Train: 95902, Station: Parel, Raw: `…`
- Source: `Table - 17.csv`, Train: 95902, Station: Currey Road, Raw: `…`
- Source: `Table - 17.csv`, Train: 95902, Station: Chinchpokli, Raw: `…`

## Harbour
- Actual services: 599
- Actual unique stations: 18
- Valid timetable cells: 5628
- Blank cells: 2382
- Annotation cells: 0
- Invalid cells: 2772
- Duplicate groups: 101

**10 Missing Time Examples:**
- Source: `Table - 51.csv`, Train: 98801, Station: KHAR, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: SANTACURTZ, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: VILEPARLE, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: ANDHERI, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: JOGESWARI, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: RAM MANDIR, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98801, Station: GOREGAON, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98803, Station: KHAR, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98803, Station: SANTACURTZ, Reason: blank, Raw: ``
- Source: `Table - 51.csv`, Train: 98803, Station: VILEPARLE, Reason: blank, Raw: ``

**10 Invalid Time Examples:**
- Source: `Table - 51.csv`, Train: 98801, Station: MUMBAI CSMT, Raw: `0:17`
- Source: `Table - 51.csv`, Train: 98801, Station: MASJID, Raw: `0:20`
- Source: `Table - 51.csv`, Train: 98801, Station: SANDHURST ROAD, Raw: `0:23`
- Source: `Table - 51.csv`, Train: 98801, Station: DOCK YARD ROAD, Raw: `0:25`
- Source: `Table - 51.csv`, Train: 98801, Station: REAY ROAD, Raw: `0:27`
- Source: `Table - 51.csv`, Train: 98801, Station: COTTON GREEN, Raw: `0:29`
- Source: `Table - 51.csv`, Train: 98801, Station: SEWERI, Raw: `0:32`
- Source: `Table - 51.csv`, Train: 98801, Station: VADALA ROAD, Raw: `0:35`
- Source: `Table - 51.csv`, Train: 98801, Station: KING'S CIRCLE, Raw: `0:39`
- Source: `Table - 51.csv`, Train: 98801, Station: MAHIM JN., Raw: `0:41`

**Duplicate Investigation (101 groups):**
- Train 98802_GOREGAON to MUMBAI CSMT appears 2 times. Kind: service variant
- Train 98804_GOREGAON to MUMBAI CSMT appears 2 times. Kind: service variant
- Train 98806_GOREGAON to MUMBAI CSMT appears 2 times. Kind: service variant
- Train 98704_GOREGAON to MUMBAI CSMT appears 3 times. Kind: service variant
- Train 98706_GOREGAON to MUMBAI CSMT appears 5 times. Kind: service variant
- Train 98708_GOREGAON to MUMBAI CSMT appears 6 times. Kind: service variant
- Train 98808_GOREGAON to MUMBAI CSMT appears 6 times. Kind: service variant
- Train 98710_GOREGAON to MUMBAI CSMT appears 5 times. Kind: service variant
- Train 98712_GOREGAON to MUMBAI CSMT appears 6 times. Kind: service variant
- Train 98810_GOREGAON to MUMBAI CSMT appears 6 times. Kind: service variant
- ... and 91 more.

## Panvel_karjat
- Actual services: 0
- Actual unique stations: 0
- Valid timetable cells: 0
- Blank cells: 0
- Annotation cells: 0
- Invalid cells: 0
- Duplicate groups: 0

**10 Missing Time Examples:**

**10 Invalid Time Examples:**

## Trans_harbour
- Actual services: 0
- Actual unique stations: 0
- Valid timetable cells: 0
- Blank cells: 0
- Annotation cells: 0
- Invalid cells: 0
- Duplicate groups: 0

**10 Missing Time Examples:**

**10 Invalid Time Examples:**

## Uran
- Actual services: 40
- Actual unique stations: 9
- Valid timetable cells: 300
- Blank cells: 60
- Annotation cells: 0
- Invalid cells: 0
- Duplicate groups: 0

**10 Missing Time Examples:**
- Source: `Table - 15.csv`, Train: 99701, Station: NERUL, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99701, Station: SEAWOODS DARAVE, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99601, Station: BELAPUR, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99603, Station: BELAPUR, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99703, Station: NERUL, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99703, Station: SEAWOODS DARAVE, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99605, Station: BELAPUR, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99705, Station: NERUL, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99705, Station: SEAWOODS DARAVE, Reason: blank, Raw: ``
- Source: `Table - 15.csv`, Train: 99607, Station: BELAPUR, Reason: blank, Raw: ``

**10 Invalid Time Examples:**

## Vasai_diva
- Actual services: 1022
- Actual unique stations: 33
- Valid timetable cells: 16296
- Blank cells: 12412
- Annotation cells: 282
- Invalid cells: 627
- Duplicate groups: 276

**10 Missing Time Examples:**
- Source: `Table - 33.csv`, Train: 90002, Station: VIRAR, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Nalla Sopara, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: VASAI ROAD, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Naigaon, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: BHAYANDAR, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Mira Road, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Dahisar, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: BORIVALI, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Kandivali, Reason: blank, Raw: ``
- Source: `Table - 33.csv`, Train: 90002, Station: Malad, Reason: blank, Raw: ``

**10 Invalid Time Examples:**
- Source: `Table - 33.csv`, Train: 90008, Station: VASAI ROAD, Raw: `ONLY`
- Source: `Table - 33.csv`, Train: 94002, Station: Malad, Raw: `ON SAT`
- Source: `Table - 33.csv`, Train: 94002, Station: Ram Mandir, Raw: `NON AC`
- Source: `Table - 33.csv`, Train: 94002, Station: Vile Parle, Raw: `Air`
- Source: `Table - 33.csv`, Train: 94002, Station: Santa Cruz, Raw: `Condition`
- Source: `Table - 33.csv`, Train: 94004, Station: VIRAR, Raw: `ON SAT`
- Source: `Table - 33.csv`, Train: 94004, Station: VASAI ROAD, Raw: `NON AC`
- Source: `Table - 33.csv`, Train: 94004, Station: Naigaon, Raw: `Air`
- Source: `Table - 33.csv`, Train: 94004, Station: BHAYANDAR, Raw: `Condition`
- Source: `Table - 34.csv`, Train: 94080, Station: VIRAR, Raw: `AC`

**Duplicate Investigation (276 groups):**
- Train 94002_UP appears 2 times. Kind: duplicate source entry (cross-file)
- Train 94004_UP appears 2 times. Kind: duplicate source entry (cross-file)
- Train 94080_UP appears 2 times. Kind: duplicate source entry (cross-file)
- Train 94082_UP appears 4 times. Kind: duplicate source entry (cross-file)
- Train 94084_UP appears 5 times. Kind: duplicate source entry (cross-file)
- Train 94086_UP appears 9 times. Kind: duplicate source entry (cross-file)
- Train 94088_UP appears 8 times. Kind: duplicate source entry (cross-file)
- Train 94090_UP appears 4 times. Kind: duplicate source entry (cross-file)
- Train 94092_UP appears 6 times. Kind: duplicate source entry (cross-file)
- Train 94094_UP appears 6 times. Kind: duplicate source entry (cross-file)
- ... and 266 more.

## Western
- Actual services: 1440
- Actual unique stations: 51
- Valid timetable cells: 21985
- Blank cells: 17980
- Annotation cells: 317
- Invalid cells: 893
- Duplicate groups: 466

**10 Missing Time Examples:**
- Source: `Table - 24.csv`, Train: 90001, Station: CHURCHGATE, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Marine Lines, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Charni Road, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Grant Road, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: M'BAI CENTRAL (L), Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Mahalakshmi, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Lower Parel, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Prabhadevi, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: DADAR, Reason: blank, Raw: ``
- Source: `Table - 24.csv`, Train: 90001, Station: Matunga Road, Reason: blank, Raw: ``

**10 Invalid Time Examples:**
- Source: `Table - 24.csv`, Train: 92003, Station: Prabhadevi, Raw: `ONLY`
- Source: `Table - 24.csv`, Train: 94001, Station: Mahalakshmi, Raw: `Air`
- Source: `Table - 24.csv`, Train: 94001, Station: Lower Parel, Raw: `Condition`
- Source: `Table - 24.csv`, Train: 94001, Station: Mahalakshmi, Raw: `Air`
- Source: `Table - 24.csv`, Train: 94001, Station: Lower Parel, Raw: `Condition`
- Source: `Table - 24.csv`, Train: 94001, Station: Mahalakshmi, Raw: `Air`
- Source: `Table - 24.csv`, Train: 94001, Station: Lower Parel, Raw: `Condition`
- Source: `Table - 24.csv`, Train: 90035, Station: Prabhadevi, Raw: `ONLY`
- Source: `Table - 24.csv`, Train: 90035, Station: Prabhadevi, Raw: `ONLY`
- Source: `Table - 24.csv`, Train: 90037, Station: Bhayandar, Raw: `ONLY`

**Duplicate Investigation (466 groups):**
- Train 94001_CHURCHGATE to VIRAR appears 3 times. Kind: service variant
- Train 90007_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90009_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90011_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90013_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90015_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90017_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 90019_CHURCHGATE to VIRAR appears 2 times. Kind: service variant
- Train 93003_CHURCHGATE to VIRAR appears 2 times. Kind: exact duplicate
- Train 90031_CHURCHGATE to VIRAR appears 2 times. Kind: exact duplicate
- ... and 456 more.

## Panvel-Karjat Investigation
- Panvel-Karjat data is completely absent from all parsed tables. Umang-Lodaya extractor did not capture this branch line.

## Uran Investigation
- The Uran line was parsed strictly from the Official CR PDF manual extraction. Umang-Lodaya CSVs did not contain Uran data. No Uran data is currently present in the structured output because the manual parse is pending Phase 5.