var exec_base = ptr(0xA0000000);
var exec_size = 0x1000000;
var instr_addr;
var xenia_offset = 0x100000000;
var postureControlOffsets = [0x50, 0x50, 0xDC];
var amigoOffsets = [0x50, 0x50, 0x140]; //after, 0x24 != 0 is player
var playerObjPtrs = [];
var playeridx = -1;
console.log("Starting");

function swap32(val) {
    return ((val & 0xFF) << 24)
           | ((val & 0xFF00) << 8)
           | ((val >> 8) & 0xFF00)
           | ((val >> 24) & 0xFF);
}
function onPtrRecv(val){
    var pointer = ptr(val.payload);
    console.log("Received " + pointer);
    var curr_ptr = pointer;
    for(var i = 1; i < postureControlOffsets.length; i++) {
        var be_val = curr_ptr.add(postureControlOffsets[i]).readU32();
        curr_ptr = ptr(swap32(be_val)).add(xenia_offset);
        console.log("level " + i + ": " + curr_ptr);
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
//mov eax, 821E8C50 is the pattern
Memory.scan(exec_base, exec_size,"B8 50 8C 1E 82" ,{onMatch(address, size) {
    console.log("Match found at "+ address);
    instr_addr = address;
    Interceptor.attach(instr_addr, {
        onEnter(args) {
            var base = this.context.rsi.add(0x48).readPointer(); //r5
            console.log("Base: " + base);
            var r5ptr = ptr(swap32(base.add(xenia_offset).readU32())).add(xenia_offset+0x50);
            send(r5ptr)
        }
    });
    return 'stop';
}});
recv('findptr',val => onPtrRecv(val))


