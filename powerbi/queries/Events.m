let
    Source = fxCsv("curated/events.csv", {
        {"event_id", type text},
        {"case_id", type text},
        {"date", type date},
        {"event_name", type text},
        {"source_date", type date},
        {"source_name", type text},
        {"event_type", type text},
        {"release_id", type text},
        {"source_url", type text},
        {"verification", type text},
        {"source_path", type text},
        {"related_news_ids", type text}
    })
in
    Source
