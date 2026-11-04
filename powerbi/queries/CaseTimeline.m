let
    Source = fxCsv("outputs/case_timeline.csv", {
        {"case_id", type text},
        {"date", type date},
        {"relative_day", Int64.Type},
        {"phase", type text},
        {"steam_peak_concurrent_players", Int64.Type},
        {"event_names", type text}
    })
in
    Source
