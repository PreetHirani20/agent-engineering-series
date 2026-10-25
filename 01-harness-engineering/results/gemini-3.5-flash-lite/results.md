# Results: gemini-3.5-flash-lite

20 tasks, 1 run(s) per task per harness, temperature 0.

| Harness | Solved | Avg steps | Median tokens / task | Mean tokens / task | Peak context | How runs ended |
|---|---|---|---|---|---|---|
| naive | **20/20** (100%) | 11.4 | 17,992 | 107,468 | 392 KB | finished 20 |
| engineered | **20/20** (100%) | 15.6 | 37,344 | 54,385 | 31 KB | finished 18, max_steps 2 |

## Per task

| Task | Stresses | naive | engineered |
|---|---|---|---|
| 01-slugify | instructions, verification | ✅ 1/1 | ✅ 1/1 |
| 02-parse-duration | verification | ✅ 1/1 | ✅ 1/1 |
| 03-invoice-rounding | instructions | ✅ 1/1 | ✅ 1/1 |
| 04-lru-cache | verification | ✅ 1/1 | ✅ 1/1 |
| 05-date-range | verification | ✅ 1/1 | ✅ 1/1 |
| 06-bulk-discount | context, tools | ✅ 1/1 | ✅ 1/1 |
| 07-big-file-temperature | tools | ✅ 1/1 | ✅ 1/1 |
| 08-log-parser | context | ✅ 1/1 | ✅ 1/1 |
| 09-split-name | verification | ✅ 1/1 | ✅ 1/1 |
| 10-csv-export | memory, instructions | ✅ 1/1 | ✅ 1/1 |
| 11-retry-decorator | memory, verification | ✅ 1/1 | ✅ 1/1 |
| 12-roman-numerals | verification | ✅ 1/1 | ✅ 1/1 |
| 13-version-compare | instructions | ✅ 1/1 | ✅ 1/1 |
| 14-config-merge | verification | ✅ 1/1 | ✅ 1/1 |
| 15-word-wrap | verification | ✅ 1/1 | ✅ 1/1 |
| 16-rate-limiter | verification | ✅ 1/1 | ✅ 1/1 |
| 17-report-percent | context, verification | ✅ 1/1 | ✅ 1/1 |
| 18-inventory-batch | instructions | ✅ 1/1 | ✅ 1/1 |
| 19-markdown-table | verification, instructions | ✅ 1/1 | ✅ 1/1 |
| 20-rename-across-files | loop, memory, tools | ✅ 1/1 | ✅ 1/1 |
