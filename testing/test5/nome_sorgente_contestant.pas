unit nome_sorgente_contestant;

interface
procedure Pianifica(N: longint; var H: array of longint);

implementation
uses nome_sorgente_contestantlib;

procedure Pianifica(N: longint; var H: array of longint);
var i : longint;
begin
	for i:=0 to N div 2 - 1 do
		if H[i] > 10 then
			Abbatti(i, 0)
		else
			Abbatti(N - i, 1);
end;

end.
