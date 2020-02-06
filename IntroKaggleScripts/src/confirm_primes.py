import math

def is_prime(p):
    for divisor in range(2, int(math.sqrt(p))+1 ):
        if p % divisor == 0:
            return False
    return True

def main():
    fin = open('fin.txt')
    for n, line in enumerate(fin):
        p = int(line.strip())
        if not is_prime(p):
            print "ERROR ***", p, "is NOT prime ***"
        if n % (100*1000) == 0:
            print "checked line:", n, "(prime", p, ")"

main()

