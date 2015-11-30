unit nome_sorgente_contestant;

interface
function contapersone(M: Longint; from, too: array of Longint): Longint;

procedure sceglicolori(res: Longint; var scelti: array of Longint; var colore: array of Double);

implementation

function contapersone(M: Longint; from, too: array of Longint): Longint;
var
	xxx: Longint;

begin
	xxx := from[M-2] + from[M-1] + too[1];
	
	if xxx > 10000 Then
		contapersone := 10000
	else 
		contapersone := xxx;
end;

procedure sceglicolori(res: Longint; var scelti: array of Longint; var colore: array of Double);
var
	i: Longint;
	
begin
	for  i:= 0 to res do
	begin
		scelti[i] := i;
		colore[i] := 23.0;
	end;
end;

end.
