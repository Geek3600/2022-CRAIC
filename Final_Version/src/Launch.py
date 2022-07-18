#!/usr/bin/python 
# -*- coding: utf-8 -*




import os

    
if __name__ == '__main__': 
    os.system('python Grab_AB.py &')
    os.system('python Push_AB.py &')
    

    os.system('python Grab_AC.py &')
    os.system('python Push_AC.py &')
    

    os.system('python Grab_BC.py &')
    os.system('python Push_BC.py &')
    

    os.system('python Grab_D.py &')
    os.system('python Push_D.py &')

    os.system('python Grab_DD.py &')
    os.system('python Push_DD.py &')
