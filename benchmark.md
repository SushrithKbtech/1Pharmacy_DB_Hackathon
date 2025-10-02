### Overview  
The Pharmacy Search API was benchmarked against ~280,227 medicine records imported into PostgreSQL.  
The benchmarks cover the following search modes:  
1.Prefix search (/search/prefix)  
2.Substring search (/search/substring)  
3.Full-text search (/search/fulltext)  
4.Fuzzy search (/search/fuzzy)  
All queries were executed using the fixed query set provided in the hackathon instructions.  
  
### Dataset & Indexes  
Dataset size:280,227 medicines (JSON → PostgreSQL import)  
Indexes used:  
1.pg_trgm (trigram index) - supports substring/fuzzy search efficiently.  
2.GIN index on fts column - enables full-text search.  
3.unaccent extension - normalizes text for case/diacritic-insensitive matching.  
  
### Query Results (submission.json excerpts)  
Example Queries:  
1.Prefix (q = “boc”):  
    ["Bocarlol 6.25mg Tablet", "BOCARNIDE 0.5mg Respules", "BOCARSTIN-20 Tablet", "Bocarstin-M 20mg/10mg Tablet", "Bocef 100mg Tablet"]  
2.Prefix (q = “Unic”):  
    ["Unicafen MR 100mg/325mg/250mg Tablet", "Unicafen P 100mg/325mg Tablet", "Unicain 2% Injection", "Unical-D3 60K Softgel Capsule", "Unicalcin 100IU Injection"]  
3.Substring (q = “Leekuf”):  
    ["Leekuf Tablet", "Leekuf 5mg Lozenges", "Leekuf Soft Gelatin Capsule", "Neo Leekuf 5mg/2mg/10mg Tablet", "Neo Leekuf SF Syrup Sugar Free"]  
4.Fuzzy (q = “daxid”):  
    ["Daxid 25mg Tablet", "Daxid 50mg Tablet", "Daxid 100mg Tablet"]  
  
### Performance Metrics (bench_stats.json)  
Metric	Value (ms)  
Min	0.169  
P50	0.561  
Avg	29.9  
P90	106.4  
Max	176.8  
Per-query Latency:  
Prefix (boc) - 0.77 ms  
Prefix (Unic) - 0.35 ms  
Prefix (Carb) - 1.06 ms  
Substring (Leekuf) - 0.29 ms  
Fuzzy (daxid) - 176.8 ms (expected higher due to trigram similarity scan)  
Fulltext (cancer) - 0.17 ms  
  
### Observations  
Prefix/Substring/Fulltext are consistently sub-millisecond for typical queries.  
Fuzzy search is slower (p90 = 176 ms), but still acceptable for typo-tolerant lookups.  
Indexes (pg_trgm, GIN) were critical in ensuring fast lookups on a large dataset.  
After VACUUM ANALYZE, planner consistently picked indexes.  
  
### Conclusion  
The system achieves fast, scalable search over ~280k+ medicines.  
Median latency (p50) is <1 ms, average latency ~30 ms (skewed by fuzzy search).  
With proper indexing, PostgreSQL handles both exact and typo-tolerant search efficiently.  
  
submission.json - Query results  
bench_stats.json - Performance metrics  
benchmark.md (this file) - Documentation  

