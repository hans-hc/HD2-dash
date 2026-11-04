let
    Source = fxCsv("curated/releases.csv", {
        {"release_id", type text},
        {"version", type text},
        {"date", type date},
        {"source_date", type date},
        {"official_name", type text},
        {"source_url", type text},
        {"summary", type text},
        {"download_size", type text},
        {"change_type_suggested", type text},
        {"scope_suggested", type text},
        {"change_type", type text},
        {"scope", type text},
        {"needs_review", type logical},
        {"verification", type text},
        {"wiki_date", type date},
        {"source_path", type text}
    })
in
    Source
