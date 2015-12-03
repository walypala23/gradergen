procedure AggiungiTutti(N: Longint; X: array of Int64);
var
	i: Longint;
begin
	for i := 0 to N-1 do
		aggiungi(X[i]);
end;