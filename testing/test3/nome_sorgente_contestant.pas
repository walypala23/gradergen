unit nome_sorgente_contestant;

interface

type
    charmatrix = array of array of char;

procedure cerca(N : longint; var mat : charmatrix);

implementation
procedure cerca(N : longint; var mat : charmatrix);
var
    i, j : longint;
begin
    for i:=0 to N-1 do
        for j:=0 to N-1 do
            if mat[i][j] = '1' then
                mat[i][j] := '0'
            else
                mat[i][j] := '1';
end;

end.
