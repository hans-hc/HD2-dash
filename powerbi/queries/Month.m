let
    Keys = List.Sort(List.Distinct(List.Combine({#"Date"[MonthStart], Reviews[period_start]}))),
    Months = Table.FromColumns({Keys}, type table [MonthStart=date])
in
    Months
