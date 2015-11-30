unit nome_sorgente_contestant;

interface

type
    charmatrix = array of array of char;

procedure cerca(N : longint; var mat : charmatrix; var A : longint; var B : longint; var C : longint);

implementation
procedure cerca(N : longint; var mat : charmatrix; var A : longint; var B : longint; var C : longint);
var
    i, j, k : longint;
begin
    for i:=0 to N-1 do
        for j:=i+1 to N-1 do
            for k:=j+1 to N-1 do
            begin
                if ((mat[i][j] = '1') and (mat[j][k] = '1') and (mat[k][i] = '1')) or
                   ((mat[i][k] = '1') and (mat[k][j] = '1') and (mat[j][i] = '1')) then
                begin
                    A := i+1;
                    B := j+1;
                    C := k+1;
                    exit
                end;
            end;
    A := -1;
    B := -1;
    C := -1;
end;

end.
