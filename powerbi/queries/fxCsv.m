(relativeFile as text, types as list) as table =>
let
    Path = Text.TrimEnd(DataFolder, {Character.FromNumber(92),"/"}) & "/" & relativeFile,
    Read = Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Read, [PromoteAllScalars=true]),
    Names = List.Transform(types, each _{0}),
    Selected = Table.SelectColumns(Headers, Names, MissingField.Error),
    Clean = Table.ReplaceValue(Selected, "", null, Replacer.ReplaceValue, Names),
    Typed = Table.TransformColumnTypes(Clean, types, "en-US")
in
    Typed
