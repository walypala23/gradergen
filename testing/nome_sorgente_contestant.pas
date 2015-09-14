unit nome_sorgente_contestant;

interface
function contapersone(M: Integer; from, too: array of Integer): Integer;

procedure sceglicolori(res: Integer; var scelti: array of Integer; var colore: array of Double);

implementation

function contapersone(M: Integer; from, too: array of Integer): Integer;
var
	xxx: Integer;

begin
	xxx := from[M-2] + from[M-1] + too[1];
	
	if xxx > 10000 Then
		contapersone := 10000
	else 
		contapersone := xxx;
end;

procedure sceglicolori(res: Integer; var scelti: array of Integer; var colore: array of Double);
var
	i: Integer;
	
begin
	for  i:= 0 to res do
	begin
		scelti[i] := i;
		colore[i] := 23.0;
	end;
end;

end.
