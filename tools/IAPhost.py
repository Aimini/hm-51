from abc import abstractmethod
import pathlib
from typing import Dict, Iterable, Union
from serial import Serial, SerialException
from serial.tools import list_ports
import argparse
from time import time

RETRY_HANDSHAKE = 5
RETRY_PROGRAMMING_A_PAGEF_AILED = 5

SEQ_HANDSHAKE = (0xFF,0xA5,0x5A,0xCC)

ROM_PAGE_SIZE = 128
ROM_SEQ_DISALBE_SDP =(
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x80, 0x5555),
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x20, 0x5555))
ROM_SEQ_ENALBE_SDP = (
    (0xAA, 0x5555),(0x55, 0x2AAA),(0xA0, 0x5555))
ROM_tWC = 5000 #5000 us

OPCODE_PROGRAMMING_PAGE = 0
OPCODE_PROGRAMMING_BYTE_ADDR_PAIR = 1
OPCODE_READ_BLOCK = 3
OPCODE_ECHO  = 4
OPCODE_EXIT  = 5
def decode_ihex(text):
    """
    convert intel hex file text to bytearray
        text: str
        dict:  map { start_addr: bytes}
    """
    lines = text.split('\n')

    segment_data = dict()
    for lineno, one in enumerate(lines):
        e = SyntaxError()
        e.lineno = lineno + 1
        e.text = one

        subp = one.strip()
        if one[0] != ':':
            e.msg = "unexcept start symbol '{}'.".format(one[0])
            e.offset = 0
            raise e

        subp = subp[1:]
        if subp == "00000001FF":
            # end of the file
            break

        # 用字符表示的二进制，忽略第0个固定的':'字符，每两个字符作为一个byte
        #     :     |   03    |     00-00     |   00    |02-0A-58|   99
        #    开头    数据长度    开始地址(大端)    类型      数据     校验和
        # （不用管）                          （只要管00）         （不用管)
        #                                    (01 end of file, see line 11)
        checksum = 0
        data_len = int(subp[0:2], 16)
        start_addr = int(subp[2:6], 16)
        data_type = int(subp[6:8], 16)
        checksum = data_len + (start_addr & 0xFF) + (start_addr >> 8) + data_type

        if data_type != 0x00:
            e.msg = "unexcept segment type {}.".format(data_type)
            e.offset = 6
            raise e

        buf = []
        for i in range(data_len):
            offset = 2 * i + 8
            od = int(subp[offset:offset + 2], 16)
            checksum += od
            buf.append(od)

        merged = False
        for segsaddr in list(segment_data.keys()):
            segd = segment_data[segsaddr]
            if segsaddr + len(segd) == start_addr:
                segd.extend(buf)
                merged = True
                break
            elif start_addr + data_len == segsaddr:
                segment_data.pop(segsaddr)
                buf.extend(segd)
                segment_data[start_addr] = buf
                merged = True
                break

        if not merged:
            segment_data[start_addr] = buf

        checksum = (0x100 - checksum) % 0x100
        filechk = int(subp[2 * data_len + 8:], 16)
        if checksum != filechk:
            e.msg = "wrong checksum {}, which expect {}.".format(filechk, checksum)
            e.offset = 2 * data_len + 8
            raise e

    return segment_data

def opcode_verifier(opcode):
    def wrapper(process_call):
        def wrapper(self, *args, **kwargs):
            self.send_int8(opcode)
            ret = process_call(self, *args, **kwargs)
            self.expect_int8(0xFF ^ opcode)
            return ret

        return wrapper

    return wrapper


class ProtocolCodecTimeoutException(Exception):
    pass
class AbstractProtocolCodec:
    def __init__(self, tWC) -> None:
        self._rval = None
        self._tWC = tWC

    @abstractmethod
    def send_intn(self, val: int, nbytes: int):
        '''
        send val as n bytes
        '''
        pass

    @abstractmethod
    def read_intn(self, n: int) -> int:
        '''
            read n bytes to form an int
        '''
        pass

    def send_int8(self, val: int):
        self.send_intn(val, 1)

    def send_int16(self, val: int):
        self.send_intn(val, 2)

    def send_int32(self, val: int):
        self.send_intn(val, 4)

    def send_intn_array(self, data, lenbytes=1, intbytes=1):
        self.send_intn(len(data), lenbytes)
        for d in data:
            self.send_intn(d, intbytes)


    def expect_intn(self, val:int, n: int) -> bool:
        self._rval = self.read_intn(n)
        return val == self._rval

    def expect_int8(self,val:int) -> bool:
        return self.expect_intn(val, 1)

    def expect_int16(self,val:int) -> bool:
        return self.expect_intn(val, 2)

    def expect_int32(self,val:int) -> bool:
        return self.expect_intn(val, 4)

    def expect_intn_array(self, data: Iterable[int], intbytes=1):
        for i, val in enumerate(data):
            if not self.expect_intn(val, intbytes):
                return i
        return None



    def handshake_knockdoor(self, code0, code1):
        while True:
            # S: hello? anyone here?
            self.send_int8(code0)
            if self.expect_int8(0xFF ^ code0):
                # C: sure, I'm here
                # S: fine, next question!
                break
        
        self.send_int8(code1)
        while True:
            if self.expect_int8(0xFF ^ code1):
                return True
            if self._rval == 0xFF ^code0:
                continue
            return False
                

    def handshake_seq(self, seq):
        for code in seq:
            self.send_int8(code)
            if not self.expect_int8(0xFF ^ code):
                return False
        return True
    

    def handshake(self, seq):
        while True:
            while not self.handshake_knockdoor(seq[0],seq[1]):
                pass
            if self.handshake_seq(seq[2:]):
                return

    @opcode_verifier(OPCODE_PROGRAMMING_PAGE)
    def programming_page(self, start_addr, data):
        self.send_int8(len(data))
        self.send_int16(start_addr)
        for b in data:
            self.send_int8(b)
        self.send_int16(self._tWC)

    @opcode_verifier(OPCODE_PROGRAMMING_BYTE_ADDR_PAIR)
    def programming_byte_address_pair(self, seq):
        self.send_int8(len(seq))
        for data, addr in seq:
            self.send_int8(data)
            self.send_int16(addr)
        self.send_int16(self._tWC)

    def disableSDP(self):
        self.programming_byte_address_pair(ROM_SEQ_DISALBE_SDP)

    def enableSDP(self):
        self.programming_byte_address_pair(ROM_SEQ_ENALBE_SDP)

    def expect_block(self, start_address, data):
        self.send_int8(OPCODE_READ_BLOCK)
        self.send_int16(start_address)
        self.send_int16(len(data))
        r = self.expect_intn_array(data)
        return r if r is None else start_address + r

    def echo(self, data):
        self.send_int8(OPCODE_ECHO)
        self.send_intn_array(data, 1, 1)
        self.expect_intn_array(data)
        
    def exit(self):
        self.send_int8(OPCODE_EXIT)

class ByteIOProtocolCodec(AbstractProtocolCodec):
    def __init__(self, IOobj, tWC, timeout = 2):
        '''
        IOobj must be a object have function 'read' and 'write',
        it's should work like a binary file object, 'read' must return
        a bytes-like, write must accept a bytes-like object.
        timeout: float
            time(second) to wait device, if we can't read any byte from
            it in timeout float, we assume the deivce have some problem
            and raise an ProtocolCodecTimeout to you.
        '''
        super().__init__(tWC)
        IOobj.read  # have read attribute
        IOobj.write  # have write attribute
        self._IO = IOobj
        self._timeout = timeout
    
    def device(self):
        return self._IO

    def _IOread(self, n):
        now = time()
        buf = bytearray()
        left = n
        while left != 0:
            buf.extend(self._IO.read(left))
            next_left = n - len(buf)
            #new byte in ,refresh timeout start point
            if next_left != left:
                now = time()
            left = next_left

            if time() - now > self._timeout:
                raise ProtocolCodecTimeoutException("device read timeout.")
        return buf

    def _IOwrite(self, b):
        self._IO.write(b)

    def send_intn(self, val: int, nbytes: int):
        '''
        send val as n bytes int with little endianness

            val:int
                value to send
            nbytes:int
                how many bytes to store val
        '''
        d = bytearray(val.to_bytes(nbytes, 'little'))
        self._IOwrite(d)

    def read_intn(self, n: int):
        '''
        send val as n bytes int with little endianness

            val:int
                value to send
            nbytes:int
                how many bytes to store val
        '''
        
        return int.from_bytes(self._IOread(n), 'little')

class DumpProtocolCodec(AbstractProtocolCodec):
    def __init__(self,tWC, sent_stream, expected_received_stream):
        '''
        dump the sent byte stream to the file "input_bytes"
        dump the expected received byte  stream to the file "expected_output_bytes"
        timeout: float
            time(second) to wait device, if we can't read any byte from
            it in timeout float, we assume the deivce have some problem
            and raise an ProtocolCodecTimeout to you.
        '''
        super().__init__(tWC)
        self.sent_stream = sent_stream
        self.received_stream = expected_received_stream
        self.sent_count = 0
        self.received_count = 0

    def send_intn(self, val: int, nbytes: int):
        d = val.to_bytes(nbytes, 'little')
        self.sent_count += len(d)
        self.sent_stream.write(d)

    def read_intn(self, n: int):
        pass
   
    def expect_intn(self, val:int, nbytes: int) -> bool:
        self._rval = val
        d = val.to_bytes(nbytes, 'little')
        self.received_count += len(d)
        self.received_stream.write(d)
        return True

def write_continuous_segment(device:AbstractProtocolCodec, start_addr, datas, retry):
    print(">> writing at 0x{:0>4X}-0x{:0>4X}, 0x{:0>4X} bytes...".format(start_addr, start_addr + len(datas) - 1, len(datas)))
     
    buffer = bytearray()
    page_address = start_addr

    for offset, d  in enumerate(datas):
        buffer.append(d)
        start_addr += 1

        if start_addr % ROM_PAGE_SIZE == 0 or \
         offset == len(datas) - 1 and len(buffer) != 0:
            while True:
                device.programming_page(start_addr=page_address, data=buffer)
                failed_address = device.expect_block(page_address, buffer)
                if failed_address is None:
                    break
                else:
                    print("[ERROR] get wrong byte at", failed_address)
                    
                retry -= 1
                if retry == 0:
                    print("[ERROR] already retry", retry, "times, give up.")
                    exit(-2)
                    # return start_addr, offset

            buffer.clear()
            page_address = start_addr

    print('[OK]')
    return None

def check_block(device, start, data):
    print(">>>> verifying  0x{:0>4X}-0x{:0>4X}, 0x{:0>4X} bytes...".format(start, start + len(data) - 1, len(data)))
    failed_address = device.expect_block(start, data)
    if failed_address is None:
        print("[OK]")
    else:
        print("[ERROR] get wrong byte at", failed_address)
        exit(-1)

def programming_file(device:AbstractProtocolCodec, data: Union[Dict, Iterable[int]], retry = 5):
    print(">> disable SDP")
    device.disableSDP()
    print("[OK]")

    if isinstance(data, Dict):
        for start_address, segment in data.items():
            write_continuous_segment(device, start_address, segment, retry)

    else:
        data = list(data)
        write_continuous_segment(device, 0, data, retry)

    print(">> enable SDP")
    device.enableSDP()
    print("[OK]")

    # check if SDP enabled
    if isinstance(data, Dict):
            for start_address, segment in data.items():
                test_data = [0xFF ^ _ for _ in segment[0:1]]
                device.programming_page(start_address, test_data)
                device.expect_block(start_address, segment[0:1])
                break
    else:
        test_data = [0xFF ^ _ for _ in segment[0:1]]
        device.programming_page(start_address, test_data)
        device.expect_block(start_address, data[0:1])
        
    if isinstance(data, Dict):
        for start_address, segment in data.items():
            check_block(device, start_address, segment)
    else:
        check_block(device, 0, data)

def main():
    argparser = argparse.ArgumentParser(
        description="a toolbox contain 7400 tester, AT28C programmer and"
                    "customer(myself) hardware tester")
    argparser.add_argument('-s', '--sent-bytes-dump-file', dest='sent_bytes_dump_file',
                           help='simulate a promgramming process, store the sent bytes to the file', action='store',
                           type=argparse.FileType('wb'), default=None)
    argparser.add_argument('-r', '--expected-received-bytes-dump-file', dest='expected_received_bytes_dump_file',
                           help='simulate a promgramming process, store the expected received bytes to the file', action='store',
                           type=argparse.FileType('wb'), default=None)
    argparser.add_argument('-p', '--port', dest='port', help='target port', action='store')
    argparser.add_argument('-b', '--baudrate', dest='baudrate',
                           help='target baudrate', action='store',
                           type=int, default=62500)
    argparser.add_argument('-f', '--file', dest='file',
                            help='the ROM file, the file with suffix of "hex" or "ihex" will be decoded as intel hex format'
                            ', otherwise it will be read as binary.', action='store')
    argparser.add_argument( '--test', dest='test',
                           nargs=2, type=lambda s: int(s, 0), 
                            metavar=('START_ADDR','END_ADDR'),
                           help='test the ROM by filling it with generated data, first int is start address'
                                ', second argument is end address. end address is als included', action='store')
    argparser.add_argument('-t', '--timeout', dest='timeout',
                           help='target baud rate', action='store',
                           type=float, default=1)


    p = argparser.parse_args()
    
    
    print(">> connecting device...")
    if  p.sent_bytes_dump_file is None and  p.expected_received_bytes_dump_file is None:
        print("chose a real device.")
        s = Serial(port = p.port,baudrate = p.baudrate, timeout = p.timeout)    
        s = ByteIOProtocolCodec(s, ROM_tWC, p.timeout)
        
    
    else:
        print("chose 'dumping to file'.")
        s = DumpProtocolCodec(ROM_tWC, p.sent_bytes_dump_file, p.expected_received_bytes_dump_file)
    print("[OK]")
    
    print(">> handshaking...")
    for i in range(RETRY_HANDSHAKE):
        try:
            s.handshake(SEQ_HANDSHAKE)
            break
        except ProtocolCodecTimeoutException as e:
            print("[INFO] no response, retry.")

        if i + 1 == RETRY_HANDSHAKE:
            print("[ERROR] handshake failed after retrying {} times.".format(RETRY_HANDSHAKE))
            exit(-1)
    print("[OK]")

    print(">> proramming the ROM...")
    data = None
    if p.test:
        start_address = p.test[0]
        end_address = p.test[1]
        print('test the ROM at range 0x{:4>0X}-0x{:4>0X}'.format(start_address ,end_address))
        data = []
        for i in range(end_address - start_address + 1):
            i %= 257
            data.append((i) % 256)
        data = {start_address : data}
        

        
    else:
        if  pathlib.Path(p.file).suffix in ('.hex', '.ihex'):
            print('load ihex file "{}"'.format(p.file))
            with open(p.file, 'r') as f:
                data = decode_ihex(f.read())
        else:
            print('load binary file "{}"'.format(p.file))
            with open(p.file, "rb") as f:
                data = f.read()

    programming_file(s, data)
    s.exit()
    print("[END]")



if __name__ == '__main__':
    main()
