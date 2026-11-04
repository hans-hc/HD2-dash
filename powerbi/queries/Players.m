let
    Source = fxCsv("curated/players.csv", {
        {"date", type date},
        {"steam_peak_concurrent_players", Int64.Type},
        {"average_concurrent_players", Int64.Type},
        {"sampled_max_concurrent_players", Int64.Type},
        {"observation_method", type text},
        {"sample_count", Int64.Type},
        {"weekday", type text},
        {"is_weekend", type logical},
        {"steam_peak_7d_mean", type number},
        {"source_path", type text}
    })
in
    Source
