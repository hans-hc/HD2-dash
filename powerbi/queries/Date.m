let
    First = List.Min(Players[date]),
    Last = List.Max(Players[date]),
    Keys = Table.FromColumns({List.Dates(First, Duration.Days(Last-First)+1, #duration(1,0,0,0))}, type table [DateKey=date]),
    Month = Table.AddColumn(Keys, "MonthStart", each Date.StartOfMonth([DateKey]), type date)
in
    Month
