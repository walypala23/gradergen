unit nome_sorgente_contestant;

interface

procedure inizializza(first: Int64);

procedure aggiungi(X: Int64);

function risultato(): Int64;

implementation

var
	S: Int64;

procedure inizializza(first: Int64);
begin
	S := first;
end;

procedure aggiungi(X: Int64);
begin
	S := S + X;
end;

function risultato(): Int64;
begin
	risultato := S;
end;

end.
