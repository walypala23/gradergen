const MAX_OUT_BUF = 4096 * 4;
var
    output_buffer : array[0..MAX_OUT_BUF-1] of char;
    idx_output_buffer : longint;
    output_stream : TFileStream;

procedure fast_write_char(x : char);
begin
    (* Write one char onto the buffer *)
    output_buffer[idx_output_buffer] := x;
    inc(idx_output_buffer);

    if idx_output_buffer = MAX_OUT_BUF then (* I'm at the end of the buffer, flush it *)
    begin
        output_stream.WriteBuffer(output_buffer, sizeof(output_buffer));

        idx_output_buffer := 0;
    end;
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

procedure fast_write_real(x : double);
begin
    (* TODO *)
    fast_write_char('4');
    fast_write_char('2');
    fast_write_char('.');
    fast_write_char('0');
end;

procedure init_fast_output(file_name : string);
var
    open_flag: word;
begin
    open_flag := fmCreate;
    if FileExists(file_name) then
        open_flag := fmOpenWrite;

    output_stream := TFileStream.Create(file_name, open_flag);
    output_stream.size := 0;
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
