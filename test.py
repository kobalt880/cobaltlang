from cobalt_lang import *

cobalt = CobaltLang()
cobalt.interprent(
'''
str message = Input 10 numbers. if number divides to 2, programm write ":)"
str smile = :)

func upd-vars int-input input, int cost = input % 2, comp write = cost -- 0
func condition if write then show smile else #
func merge call upd-vars, call condition

show message
repeat 10 times call merge

''')
