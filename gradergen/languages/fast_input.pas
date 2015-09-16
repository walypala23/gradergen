const MAX_IN_BUF = 4096 * 4;
var
    total_bytes_read, bytes_read : int64;
    input_buffer : array[0..MAX_IN_BUF-1] of char;
    idx_input_buffer : longint;
    input_stream : TFileStream;

function fast_read_next_char(): Char;
begin
    (* Take one char out of the buffer *)
    fast_read_next_char := input_buffer[idx_input_buffer];
    inc(idx_input_buffer);

    if idx_input_buffer = MAX_IN_BUF then (* I'm at the end of the buffer, read another buffer *)
    begin
        if total_bytes_read <= input_stream.Size then (* We haven't reached EOF *)
        begin
            bytes_read := input_stream.Read(input_buffer, sizeof(input_buffer));
            inc(total_bytes_read, bytes_read);
        end;

        idx_input_buffer := 0;
    end;
end;

(* Returns first non whitespace character *)
function fast_read_char() : char;
var c: Char;
begin
    c := fast_read_next_char();
    while (ord(c) = $0020) or (ord(c) = $0009) or
          (ord(c) = $000a) or (ord(c) = $000b) or
          (ord(c) = $000c) or (ord(c) = $000d) do
        c := fast_read_next_char();

    fast_read_char := c;
end;

function fast_read_int() : longint;
var res : longint;
    c : char;
    negative : boolean;
begin
    res := 0;
    negative := False;

    repeat
        c := fast_read_next_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := fast_read_next_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := fast_read_next_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_int := -res
    else
        fast_read_int := res;
end;

function fast_read_longint() : int64;
var res : int64;
    c : char;
    negative : boolean;
begin
    res := 0;
    negative := False;

    repeat
        c := fast_read_next_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := fast_read_next_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := fast_read_next_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_longint := -res
    else
        fast_read_longint := res;
end;

function fast_read_real() : double;
begin
    (* TODO *)
    fast_read_real := 42.0;
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
