# Results: gemma-4-26b-a4b-it

16 tasks, 1 run(s) per task per harness, temperature 0.

Excluded because at least one harness could not complete them due to API errors or rate limits (not counted for any harness): 07-big-file-temperature, 08-log-parser, 17-report-percent, 19-markdown-table.

| Harness | Solved | Avg steps | Median tokens / task | Mean tokens / task | Peak context | How runs ended |
|---|---|---|---|---|---|---|
| naive | **14/16** (88%) | 9.7 | 36,451 | 36,548 | 36 KB | finished 16 |
| engineered | **16/16** (100%) | 14.9 | 70,710 | 102,222 | 70 KB | finished 15, max_steps 1 |

## Per task

| Task | Stresses | naive | engineered |
|---|---|---|---|
| 01-slugify | instructions, verification | ✅ 1/1 | ✅ 1/1 |
| 02-parse-duration | verification | ✅ 1/1 | ✅ 1/1 |
| 03-invoice-rounding | instructions | ✅ 1/1 | ✅ 1/1 |
| 04-lru-cache | verification | ✅ 1/1 | ✅ 1/1 |
| 05-date-range | verification | ✅ 1/1 | ✅ 1/1 |
| 06-bulk-discount | context, tools | ✅ 1/1 | ✅ 1/1 |
| 09-split-name | verification | ✅ 1/1 | ✅ 1/1 |
| 10-csv-export | memory, instructions | ✅ 1/1 | ✅ 1/1 |
| 11-retry-decorator | memory, verification | ✅ 1/1 | ✅ 1/1 |
| 12-roman-numerals | verification | ✅ 1/1 | ✅ 1/1 |
| 13-version-compare | instructions | ❌ 0/1 | ✅ 1/1 |
| 14-config-merge | verification | ✅ 1/1 | ✅ 1/1 |
| 15-word-wrap | verification | ❌ 0/1 | ✅ 1/1 |
| 16-rate-limiter | verification | ✅ 1/1 | ✅ 1/1 |
| 18-inventory-batch | instructions | ✅ 1/1 | ✅ 1/1 |
| 20-rename-across-files | loop, memory, tools | ✅ 1/1 | ✅ 1/1 |
