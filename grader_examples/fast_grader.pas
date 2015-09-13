uses NomeSorgenteContestant;

{ TODO: languages/fast_io.pas }
var	
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
	init_fast_io();

	{ Reading input }
	N := fast_read_int();
	M := fast_read_int();
	S := fast_read_int();
	Setlength(P, N);
	for i0 := 0 to N do
	begin
		P[i0] := fast_read_int();
	end;
	Setlength(from, M);
	Setlength(too, M);
	Setlength(length, M);
	for i0 := 0 to M do
	begin
		from[i0] := fast_read_int();
		too[i0] := fast_read_int();
		length[i0] := fast_read_int();
	end;
	H := fast_read_int();
	W := fast_read_int();
	Setlength(R, H, W);
	Setlength(G, H, W);
	Setlength(B, H, W);
	for i0 := 0 to H do
	begin
		for i1 := 0 to W do
		begin
			R[i0][i1] := fast_read_char();
			G[i0][i1] := fast_read_char();
			B[i0][i1] := fast_read_char();
		end;
	end;

	{ Calling functions }
	contapersone(M, from, too);
	sceglicolori(res, scelti, colore);

	{ Writing output }
	fast_write_int(res);
	fast_write_char(' ');
	fast_write_char('\n');
	for i0 := 0 to res do
	begin
		fast_write_int(scelti[i0]);
		fast_write_char(' ');
		fast_write_real(colore[i0]);
		fast_write_char(' ');
		fast_write_char('\n');
	end;
	for i0 := 0 to H do
	begin
		for i1 := 0 to W do
		begin
			fast_write_char(R[i0][i1]);
			fast_write_char(' ');
		end;
		fast_write_char('\n');
	end;
	
	close_fast_io();
end.
