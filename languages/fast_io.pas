uses Classes;

const MAXBUF = 4096 * 4;
var
    TotalBytesRead, BytesRead : int64;
    Buffer : array [0..MAXBUF] of char;
    idxBuffer : longint;
    FileStream : TFileStream;

function getChar() : char;
begin
    getChar := Buffer[idxBuffer];
    if idxBuffer = MAXBUF then (* Sono all'ultimo carattere: leggo un altro pezzo di roba *)
    begin
        if TotalBytesRead <= FileStream.Size then (* Il file NON e' ancora terminato *)
        begin
            BytesRead := FileStream.Read(Buffer, sizeof(Buffer));
            inc(TotalBytesRead, BytesRead);
        end;
        idxBuffer := 0;
    end else
        inc(idxBuffer);
end;

function nextInt() : longint;
var res : longint;
    c : char;
begin
    res := 0;
    repeat
        c := getChar();
    until ('0' <= c) and (c <= '9');
    repeat
        res := res * 10 + ord(c) - ord('0');
        c := getChar();
    until not (('0' <= c) and (c <= '9'));
    nextInt := res;
end;

procedure initFastinput(inputName : string);
begin
    FileStream := TFileStream.Create(inputName, fmOpenRead);
    FileStream.Position := 0;
    BytesRead := FileStream.Read(Buffer, sizeof(Buffer));
    inc(TotalBytesRead, BytesRead);
    idxBuffer := 0;
end;
