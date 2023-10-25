var exec_base = ptr(0xA0000000);
var exec_size = 0x1000000;
var instr_addr;
var xenia_offset = 0x100000000;
var postureControlOffsets = [0xE4, 0x50, 0xDC];
var amigoOffsets = [0xE4, 0x50, 0x140]; //after, 0x24 != 0 is player
console.log("Starting");

function swap32(val) {
    return ((val & 0xFF) << 24)
           | ((val & 0xFF00) << 8)
           | ((val >> 8) & 0xFF00)
           | ((val >> 24) & 0xFF);
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
            sleep(500);
            var playerObjPtr = base.add(xenia_offset).readU32(); //[r5]
            playerObjPtr = swap32(playerObjPtr);
            playerObjPtr = ptr(playerObjPtr).add(xenia_offset);
            console.log(playerObjPtr);
            var stateMachinePtr = swap32(playerObjPtr.add(amigoOffsets[0]).readU32());
            stateMachinePtr = ptr(stateMachinePtr).add(xenia_offset);
            console.log(stateMachinePtr);
            var characterContextPtr = swap32(stateMachinePtr.add(amigoOffsets[1]).readU32());
            characterContextPtr = ptr(characterContextPtr).add(xenia_offset);
            console.log(characterContextPtr);
        }
    });
    return 'stop';
}});


