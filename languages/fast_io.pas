uses Classes;

const MAXBUF = 4096 * 4;
var
    total_bytes_read, bytes_read : int64;
    buffer : array [0..MAXBUF] of char;
    idx_buffer : longint;
    file_stream : TFileStream;

function read_fast_char() : char;
begin
    (* Take one byte out of the buffer *)
    read_fast_char := buffer[idxBuffer];

    if idx_buffer = MAXBUF then (* I'm at the end of the buffer, read another buffer *)
    begin
        if total_bytes_read <= file_stream.Size then (* We haven't reached EOF *)
        begin
            bytes_read := file_stream.Read(buffer, sizeof(Buffer));
            inc(total_bytes_read, bytes_read);
        end;

        idx_buffer := 0;
    end
    else (* The buffer has not ran out of bytes, yet *)
    begin
        inc(idx_buffer);
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
        c := read_fast_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := read_fast_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := read_fast_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_int := -res;
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
        c := read_fast_char();
    until (c = '-') or (('0' <= c) and (c <= '9'));

    if c = '-' then
    begin
        negative := True;
        c := read_fast_char();
    end;

    repeat
        res := res * 10 + ord(c) - ord('0');
        c := read_fast_char();
    until not (('0' <= c) and (c <= '9'));

    if negative then
        fast_read_int := -res;
    else
        fast_read_int := res;
end;

procedure init_fast_io(input_name : string);
begin
    file_stream := TFileStream.Create(input_name, fmOpenRead);
    file_stream.Position := 0;
    bytes_read := file_stream.Read(buffer, sizeof(Buffer));
    inc(total_bytes_read, bytes_read);
    idx_buffer := 0;
end;
