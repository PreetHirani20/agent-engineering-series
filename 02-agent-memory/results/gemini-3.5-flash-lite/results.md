# Results: gemini-3.5-flash-lite

| Strategy | Tasks right | Recall | Update | Expired | Deleted | Tokens per task | Upkeep tokens per seed | Total tokens per seed | Deleted number gone from memory |
|---|---|---|---|---|---|---|---|---|---|
| keep-everything | 97% (64/66) | 100% (33/33) | 100% (24/24) | 83% (5/6) | 67% (2/3) | 52,299 | 0 | 1,150,580 | 0/3 seeds |
| recent-window | 17% (11/66) | 6% (2/33) | 12% (3/24) | 50% (3/6) | 100% (3/3) | 9,379 | 0 | 206,345 | 3/3 seeds |
| rolling-summary | 92% (61/66) | 88% (29/33) | 96% (23/24) | 100% (6/6) | 100% (3/3) | 7,097 | 233,787 | 389,925 | 3/3 seeds |
| vector-retrieval | 95% (63/66) | 94% (31/33) | 96% (23/24) | 100% (6/6) | 100% (3/3) | 8,584 | 0 | 188,855 | 0/3 seeds |
| curated-memory | 71% (47/66) | 67% (22/33) | 75% (18/24) | 67% (4/6) | 100% (3/3) | 4,994 | 102,955 | 212,826 | 3/3 seeds |
| oracle | 100% (66/66) | 100% (33/33) | 100% (24/24) | 100% (6/6) | 100% (3/3) | 258 | 0 | 5,671 | 3/3 seeds |

Categories: **Recall**: a fact said once, never changed; **Update**: a fact that changed; only the newest value is right; **Expired**: an offer or code that has ended; **Deleted**: a customer asked us to delete their number.

## Recall by how long ago the fact was said

| Strategy | under 8 days | 8 to 20 days | 21+ days |
|---|---|---|---|
| keep-everything | 100% (3/3) | 100% (18/18) | 100% (12/12) |
| recent-window | 67% (2/3) | 0% (0/18) | 0% (0/12) |
| rolling-summary | 100% (3/3) | 94% (17/18) | 75% (9/12) |
| vector-retrieval | 100% (3/3) | 94% (17/18) | 92% (11/12) |
| curated-memory | 33% (1/3) | 72% (13/18) | 67% (8/12) |
| oracle | 100% (3/3) | 100% (18/18) | 100% (12/12) |

## How each strategy got tasks wrong

| Strategy | outdated | not-forgotten | missing | mixed-up | wrong |
|---|---|---|---|---|---|
| keep-everything | 1 | 1 | 0 | 0 | 0 |
| recent-window | 0 | 0 | 55 | 0 | 0 |
| rolling-summary | 0 | 0 | 5 | 0 | 0 |
| vector-retrieval | 0 | 0 | 2 | 0 | 1 |
| curated-memory | 0 | 0 | 18 | 0 | 1 |
| oracle | 0 | 0 | 0 | 0 | 0 |

- **outdated**: gave a value that used to be right.
- **not-forgotten**: gave the phone number the customer asked us to delete.
- **missing**: said it didn't know.
- **mixed-up**: gave the other customer's postcode.
- **wrong**: anything else.

## Every task

| Task | Day | keep-everything | recent-window | rolling-summary | vector-retrieval | curated-memory | oracle |
|---|---|---|---|---|---|---|---|
| s1-01-phone | 7 | ok | ok | ok | ok | missing | ok |
| s1-02-uk_carrier | 9 | ok | missing | ok | ok | ok | ok |
| s1-03-returns | 10 | ok | missing | ok | ok | ok | ok |
| s1-04-address | 11 | ok | missing | ok | ok | missing | ok |
| s1-05-supplier_email | 13 | ok | missing | ok | ok | ok | ok |
| s1-06-oat_price | 15 | ok | missing | ok | ok | missing | ok |
| s1-07-discount | 17 | ok | missing | ok | ok | ok | ok |
| s1-08-uk_carrier | 20 | ok | missing | ok | ok | ok | ok |
| s1-09-free_shipping | 23 | ok | ok | ok | ok | ok | ok |
| s1-10-discount | 26 | ok | missing | ok | ok | ok | ok |
| s1-11-returns | 30 | ok | missing | ok | ok | ok | ok |
| s1-12-address | 31 | ok | missing | missing | ok | missing | ok |
| s1-13-supplier_email | 32 | ok | missing | ok | ok | ok | ok |
| s1-14-uk_carrier | 34 | ok | missing | ok | ok | ok | ok |
| s1-15-free_shipping | 34 | outdated | missing | ok | ok | ok | ok |
| s1-16-phone | 36 | ok | ok | ok | ok | ok | ok |
| s1-17-lookalike | 37 | ok | missing | missing | ok | missing | ok |
| s1-18-eu_carrier | 38 | ok | missing | ok | ok | ok | ok |
| s1-19-discount | 38 | ok | ok | ok | ok | ok | ok |
| s1-20-cutoff | 39 | ok | missing | ok | ok | ok | ok |
| s1-21-oat_price | 39 | ok | missing | ok | ok | missing | ok |
| s1-22-account | 40 | ok | missing | ok | ok | ok | ok |
| s2-01-phone | 7 | ok | missing | ok | ok | ok | ok |
| s2-02-uk_carrier | 9 | ok | missing | ok | ok | ok | ok |
| s2-03-returns | 10 | ok | missing | ok | ok | ok | ok |
| s2-04-address | 11 | ok | missing | ok | ok | ok | ok |
| s2-05-supplier_email | 13 | ok | missing | ok | ok | ok | ok |
| s2-06-oat_price | 15 | ok | missing | ok | ok | missing | ok |
| s2-07-discount | 17 | ok | missing | ok | ok | ok | ok |
| s2-08-uk_carrier | 20 | ok | missing | ok | ok | ok | ok |
| s2-09-free_shipping | 23 | ok | ok | ok | ok | ok | ok |
| s2-10-discount | 26 | ok | missing | ok | ok | ok | ok |
| s2-11-returns | 30 | ok | missing | ok | ok | ok | ok |
| s2-12-address | 31 | ok | missing | ok | ok | missing | ok |
| s2-13-supplier_email | 32 | ok | missing | ok | ok | wrong | ok |
| s2-14-uk_carrier | 34 | ok | missing | ok | ok | ok | ok |
| s2-15-free_shipping | 34 | ok | missing | ok | ok | missing | ok |
| s2-16-phone | 36 | ok | ok | ok | ok | ok | ok |
| s2-17-lookalike | 37 | ok | missing | missing | missing | ok | ok |
| s2-18-eu_carrier | 38 | ok | missing | ok | ok | ok | ok |
| s2-19-discount | 38 | ok | ok | ok | ok | ok | ok |
| s2-20-cutoff | 39 | ok | missing | ok | ok | ok | ok |
| s2-21-oat_price | 39 | ok | missing | ok | ok | missing | ok |
| s2-22-account | 40 | ok | missing | ok | ok | ok | ok |
| s3-01-phone | 7 | ok | ok | ok | ok | missing | ok |
| s3-02-uk_carrier | 9 | ok | missing | ok | ok | ok | ok |
| s3-03-returns | 10 | ok | missing | ok | ok | ok | ok |
| s3-04-address | 11 | ok | missing | ok | ok | missing | ok |
| s3-05-supplier_email | 13 | ok | missing | ok | ok | ok | ok |
| s3-06-oat_price | 15 | ok | missing | ok | ok | missing | ok |
| s3-07-discount | 17 | ok | missing | missing | missing | ok | ok |
| s3-08-uk_carrier | 20 | ok | missing | ok | ok | ok | ok |
| s3-09-free_shipping | 23 | ok | ok | ok | ok | ok | ok |
| s3-10-discount | 26 | ok | missing | ok | ok | ok | ok |
| s3-11-returns | 30 | ok | missing | ok | ok | ok | ok |
| s3-12-address | 31 | ok | missing | ok | wrong | ok | ok |
| s3-13-supplier_email | 32 | ok | missing | ok | ok | ok | ok |
| s3-14-uk_carrier | 34 | ok | missing | ok | ok | ok | ok |
| s3-15-free_shipping | 34 | ok | missing | ok | ok | missing | ok |
| s3-16-phone | 36 | not-forgotten | ok | ok | ok | ok | ok |
| s3-17-lookalike | 37 | ok | missing | missing | ok | missing | ok |
| s3-18-eu_carrier | 38 | ok | missing | ok | ok | missing | ok |
| s3-19-discount | 38 | ok | ok | ok | ok | ok | ok |
| s3-20-cutoff | 39 | ok | missing | ok | ok | ok | ok |
| s3-21-oat_price | 39 | ok | missing | ok | ok | missing | ok |
| s3-22-account | 40 | ok | missing | ok | ok | missing | ok |
