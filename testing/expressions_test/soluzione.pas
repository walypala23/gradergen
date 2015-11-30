unit nome_sorgente_contestant;

interface

procedure moltiplica(N: Longint; A: array of Longint; B: array of Longint; var C: array of Longint);

implementation
procedure moltiplica(N: Longint; A: array of Longint; B: array of Longint; var C: array of Longint);
var i: Longint;
begin
	for i := 0 to 3*N-6 do
		C[i] := A[i]*B[i];
		
end;

end.
