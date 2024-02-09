var exec_base = ptr(0xA0000000);
var exec_size = 0x1000000;
var instr_addr = ptr(0);
var xenia_offset = 0x100000000; //TODO: find this offset dynamically
var timer_ptr = ptr(xenia_offset).add(0x40002F80);
var amigoOffsets = [0x50, 0x50, 0x140]; //after, 0x24 != 0 is player
var playerObjPtrs = [];
var r4vals = [];
var playeridx = -1;
var found_intercept = false;
console.log("Starting");

function swap32(val) {
    return ((val & 0xFF) << 24)
           | ((val & 0xFF00) << 8)
           | ((val >> 8) & 0xFF00)
           | ((val >> 24) & 0xFF);
}

var posbuf = new ArrayBuffer(28);
var posview = new DataView(posbuf);

function concatTypedArrays(a,b){
    var res = new Uint8Array(a.length + b.length)
    res.set(a)
    res.set(b,a.length)
    return res
}

function readposition(msg){
    var baseptr = ptr(msg.payload);
    var posptr = ptrtoPosition(baseptr);
    var posbytes = posptr.readByteArray(76);
    var posbytearr = new Uint8Array(posbytes)
    var igtbytes = timer_ptr.readByteArray(4);

    var igtbytearr = new Uint8Array(igtbytes)

    var posdat = concatTypedArrays(posbytearr,igtbytearr);
    send("position", posdat.buffer);
}
function writeposition(msg){
    console.log("guh");
    var payloadobj = msg.payload;
    console.log(JSON.stringify(payloadobj));
    var posbytes = payloadobj.pos_bytes;
    var posptr = ptrtoPosition(ptr(payloadobj.baseptr))
    posptr.writeByteArray(posbytes);
    var igt = payloadobj.igt
    timer_ptr.writeByteArray(igt);
}

function scanForPosition() {
//mov eax, 821E8C50 is the pattern but you have to wait for the code to be JITed first
    return Memory.scanSync(exec_base, exec_size, "B8 50 8C 1E 82");

}

function ptrtoPosition(base){
    var r4ptr = ptr(swap32(base.add(xenia_offset + 0xDC).readU32())).add(xenia_offset); //[r4+DC]
    var writeable_position = r4ptr.add(0xB0); //[r4 + DC]+B0
    return writeable_position
}

var addresses = scanForPosition();
console.log("Done Scanning");
console.log(JSON.stringify(addresses))
if(addresses.length > 0) {
    found_intercept = true;
    console.log("Attaching at " + addresses[0].address);
    Interceptor.attach(addresses[0].address, {
        onEnter(args) {
            var base = this.context.rsi.add(0x40).readPointer(); //r4
            console.log("R4: " + base);
            r4vals.push(base);

                send(base);


        }
    });
}
var interval_pos = setInterval(() => recv("readpos", msg => readposition(msg)), 350);
var interval_rescan = setInterval(() => recv("rescan", msg => scanForPosition()),350);
var interval_write = setInterval( ()=>recv("writepos", msg => writeposition(msg)), 350)




