let
    Source = fxCsv("curated/reviews.csv", {
        {"period_start", type date},
        {"period_end", type date},
        {"positive", Int64.Type},
        {"negative", Int64.Type},
        {"total", Int64.Type},
        {"pct_positive", type number},
        {"granularity", type text},
        {"completeness", type text},
        {"filter_id", type text},
        {"source_path", type text}
    })
in
    Source
