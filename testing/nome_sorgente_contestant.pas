unit nome_sorgente_contestant;

interface
function contapersone(M: Integer; from, too: array of Integer): Integer;

type
  IntArray = array of Integer;
  RealArray = array of Double;

procedure sceglicolori(res: Integer; var scelti: IntArray; var colore: RealArray);

implementation

function contapersone(M: Integer; from, too: array of Integer): Integer;
var
	xxx: Integer;

begin
	xxx := from[M-2] + from[M-1] + too[1];
{
	name := min(xxx, 10000);
}
	if xxx > 10000 Then
		contapersone := 10000
	else 
		contapersone := xxx;
end;

procedure sceglicolori(res: Integer; var scelti: IntArray; var colore: RealArray);
var
	i: Integer;
	
begin
	SetLength(scelti, res);
	SetLength(colore, res);
	
	for  i:= 0 to res do
	begin
		scelti[i] := i;
		colore[i] := 23.0;
	end;
end;

end.
