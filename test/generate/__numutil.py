import random
import itertools
class numutil:
    @staticmethod
    def  signn(val,l):
        '''
        convert val to n-bit sign value
            val:int
                value to convert
            ret:
                corresponding value
        '''
        mask = 2**l - 1;
        ret = val & mask
        if ret >= 2**(l - 1):
            ret = -2**l + ret
        return ret

    @staticmethod
    def sign64(val):
        '''
        convert val to 64-bit sign value
            val:int
                value to convert
            ret:
                corresponding value
        '''
        return numutil.signn(val,64)

    @staticmethod
    def sign32(val):
        '''
        convert val to 32-bit sign value
            val:int
                value to convert
            ret:
                corresponding value
        '''
        return  numutil.signn(val,32)

    @staticmethod
    def sign16(val):
        '''
        convert val to 16-bit sign value
            val:int
                value to convert
            ret:
                corresponding value
        '''
        return numutil.signn(val,16)

    @staticmethod
    def sign8(val):
        '''
        convert val to 8-bit sign value
            val:int
                value to convert
            ret:
                corresponding value
        '''
        return numutil.signn(val,8)

    @staticmethod
    def bound(bit_len,using_signed = False):
        if using_signed:
            max_limit = 2**(bit_len - 1)
            min_value = -2**(bit_len - 1)
        else:
            max_limit = 2**bit_len
            min_value = 0
        middle_value = int((max_limit + min_value)/2)
        return list(itertools.chain(range(min_value,min_value + 4),range(middle_value - 4, middle_value + 4),range(max_limit - 4,max_limit)))
    
    @staticmethod
    def bound_s16():
        return numutil.bound(16,True)

    @staticmethod
    def u32():
        return random.choice(range(2**32)) 

    @staticmethod
    def u16():
        return random.choice(range(2**16))

    @staticmethod
    def s16():
        return random.choice(range(-2**15,2**15))
        
    @staticmethod
    def s8():
        return random.choice(range(-2**8,2**8))

    @staticmethod
    def below(x):
        return random.choice(range(x))

    @staticmethod
    def align_word(x):
        return (x >> 2) << 2

    @staticmethod
    def sx8(x):
        return f"0x{x:0>8X}"

    @staticmethod
    def sx4(x):
        return f"0x{x:0>4X}"

    @staticmethod
    def sx2(x):
        return f"0x{x:0>2X}"

    # create a random jump index list
    # next_index = list[current_index]
    @staticmethod
    def jl(k):
        jump_seq = list(range(k)) # indicate jump sequence, for example
                                  # [1,4,3,2] is meaning   1 -> 4 -> 3 -> 2 -> 1
        jump_link = list(range(k)) # get next index from current index list[1] = 4, list[4] = 3

        
        random.shuffle(jump_seq)
        l = len(jump_seq)
        for i in range(l):
            jump_link[jump_seq[i]] = jump_seq[(i + 1) % l]
            
        # print(jump_seq)
        # print(jump_link)
        return jump_link