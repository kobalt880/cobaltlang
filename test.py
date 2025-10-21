from cobalt_lang import *

cobalt = CobaltLang()
cobalt.interprent(
'''
int iter_count = 101

func update-vars int ost = i % 2, comp even = ost -- 0
func condition if even then show i else #
func merge call update-vars, call condition
repeat iter_count times call merge

''')
