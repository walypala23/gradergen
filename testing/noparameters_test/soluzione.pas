unit nome_sorgente_contestant;

interface

procedure inizializza(first: Int64);

procedure aggiungi(N: Longint; X: array of Int64);

function risultato(): Int64;

implementation

var
	S: Int64;

procedure inizializza(first: Int64);
begin
	S := first;
end;

procedure aggiungi(N: Longint; X: array of Int64);
var
	i: Longint;
begin
	for i:=0 to N-1 do
		S := S + X[i];
end;

function risultato(): Int64;
begin
	risultato := S;
end;

end.
