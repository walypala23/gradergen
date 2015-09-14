uses nome_sorgente_contestant, Classes;

const MAXBUF = 4096 * 4;
var
    total_bytes_read, bytes_read : int64;
    input_buffer, output_buffer : array[0..MAXBUF-1] of char;
    idx_input_buffer, idx_output_buffer : longint;
    input_stream, output_stream : TFileStream;

function fast_read_char() : char;
begin
    (* Take one char out of the buffer *)
    fast_read_char := input_buffer[idx_input_buffer];
    inc(idx_input_buffer);

    if idx_input_buffer = MAXBUF then (* I'm at the end of the buffer, read another buffer *)
    begin
        if total_bytes_read <= input_stream.Size then (* We haven't reached EOF *)
        begin
            bytes_read := input_stream.Read(input_buffer, sizeof(input_buffer));
            inc(total_bytes_read, bytes_read);
        end;

        idx_input_buffer := 0;
    end;
end;

procedure fast_write_char(x : char);
begin
    (* Write one char onto the buffer *)
    output_buffer[idx_output_buffer] := x;
    inc(idx_output_buffer);

    if idx_output_buffer = MAXBUF then (* I'm at the end of the buffer, flush it *)
    begin
        output_stream.WriteBuffer(output_buffer, sizeof(output_buffer));

        idx_output_buffer := 0;
    end;
end;

function fast_read_int() : longint;
var res : longint;
    c : char;
    negative : boolean;
begin
    res := 0;
    negative := False;

    repeat
        c := fast_read_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := fast_read_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := fast_read_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_int := -res
    else
        fast_read_int := res;
end;

procedure fast_write_int(x : longint);
begin
    if x < 0 then (* Write the sign, then the number *)
    begin
        fast_write_char('-');
        fast_write_int(-x);
    end
    else (* Write the number recursively *)
    begin
        if x >= 10 then
            fast_write_int(x div 10);
        fast_write_char(chr(ord('0') + x mod 10));
    end;
end;

function fast_read_longint() : int64;
var res : int64;
    c : char;
    negative : boolean;
begin
    res := 0;
    negative := False;

    repeat
        c := fast_read_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := fast_read_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := fast_read_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_longint := -res
    else
        fast_read_longint := res;
end;

procedure fast_write_longint(x : int64);
begin
    if x < 0 then (* Write the sign, then the number *)
    begin
        fast_write_char('-');
        fast_write_longint(-x);
    end
    else (* Write the number recursively *)
    begin
        if x >= 10 then
            fast_write_longint(x div 10);
        fast_write_char(chr(ord('0') + x mod 10));
    end;
end;

function fast_read_real() : double;
begin
    fast_read_real := 42.0;
end;

procedure fast_write_real(x : double);
begin
    fast_write_char('4');
    fast_write_char('2');
    fast_write_char('.');
    fast_write_char('0');
end;

procedure init_fast_input(file_name : string);
begin
    input_stream := TFileStream.Create(file_name, fmOpenRead);
    input_stream.Position := 0;
    bytes_read := input_stream.Read(input_buffer, sizeof(input_buffer));
    inc(total_bytes_read, bytes_read);
    idx_input_buffer := 0;
end;

procedure close_fast_input;
begin
    input_stream.Free;
end;

procedure init_fast_output(file_name : string);
begin
    output_stream := TFileStream.Create(file_name, fmCreate);
    idx_output_buffer := 0;
end;

procedure close_fast_output;
begin
    if idx_output_buffer > 0 then (* Gotta flush them bytez *)
    begin
        (* TODO: check if this is OK also when using unicode data *)
        output_stream.Write(output_buffer, idx_output_buffer * sizeof(output_buffer[0]))
    end;

    output_stream.Free;
end;
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
	init_fast_input('input.txt');
	init_fast_output('output.txt');

	{ Reading input }
	N := fast_read_int();
	M := fast_read_int();
	S := fast_read_int();
	Setlength(P, N);
	for i0 := 0 to N-1 do
	begin
		P[i0] := fast_read_int();
	end;
	Setlength(from, M);
	Setlength(too, M);
	Setlength(length, M);
	for i0 := 0 to M-1 do
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
	for i0 := 0 to H-1 do
	begin
		for i1 := 0 to W-1 do
		begin
			R[i0][i1] := fast_read_char();
			G[i0][i1] := fast_read_char();
			B[i0][i1] := fast_read_char();
		end;
	end;

	{ Calling functions }
	res := contapersone(M, from, too);
	Setlength(scelti, res);
	Setlength(colore, res);
	sceglicolori(res, scelti, colore);

	{ Writing output }
	fast_write_int(res);
	fast_write_char(chr(10));
	for i0 := 0 to res-1 do
	begin
		fast_write_int(scelti[i0]);
		fast_write_char(' ');
		fast_write_real(colore[i0]);
		fast_write_char(chr(10));
	end;
	for i0 := 0 to H-1 do
	begin
		for i1 := 0 to W-1 do
		begin
			fast_write_char(R[i0][i1]);
		end;
		fast_write_char(chr(10));
	end;
	
	close_fast_input();
	close_fast_output();
end.
