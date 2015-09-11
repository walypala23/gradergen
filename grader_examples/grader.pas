uses NomeProblema;

var	fr, fw : text;

{ Declaring variables }
	N : Integer;
	M : Integer;
	S : Integer;
	P : array of Integer;
	from : array of Integer;
	too : array of Integer;
	length : array of Integer;
	H : Integer;
	W : Integer;
	R : array of array of Char;
	G : array of array of Char;
	B : array of array of Char;
	res : Integer;
	scelti : array of Integer;
	colore : array of Double;

{ iterators used in for loops }
	i0, i1: Integer;
	
begin
{$ifdef EVAL}
    assign(fr, 'input.txt');
    assign(fw, 'output.txt');
{$else}
    fr := input;
    fw := output;
{$endif}
    reset(fr);
    rewrite(fw);

	{ Reading input }
	readln(fr, N, M, S);
	Setlength(P, N);
	for i0 := 0 to N do
	begin
		read(fr, P[i0]);
	end;
	Setlength(from, M);
	Setlength(too, M);
	Setlength(length, M);
	for i0 := 0 to M do
	begin
		read(fr, from[i0], too[i0], length[i0]);
	end;
	readln(fr, H, W);
	Setlength(R, H, W);
	Setlength(G, H, W);
	Setlength(B, H, W);
	for i0 := 0 to H do
	begin
		for i1 := 0 to W do
		begin
			read(fr, R[i0][i1], G[i0][i1], B[i0][i1]);
		end;
	end;

	{ Calling functions }
	contapersone(M, from, too);
	sceglicolori(res, scelti, colore);

	{ Writing output }
	writeln(fw, res);
	for i0 := 0 to res do
	begin
		writeln(fw, scelti[i0], colore[i0]);
	end;
	writeln(fw);
	
	close(fr);
    close(fw);
end.
