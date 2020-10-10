

def is_uncondition(par):
    return par == 'J'

def is_compare_jump(par):
    return par in ('JGT', 'JEQ','JLT')

def is_condtion(par):
    return par in ('JGT', 'JEQ','JLT', 'JBIT', 'JALUF', 'JNALUF')