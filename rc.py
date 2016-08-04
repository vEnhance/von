import os

VON_BASE_PATH = "/home/evan/Documents/Oly-Math/Database/" # TODO for public, use better
VON_INDEX_NAME = "index.yaml"
EDITOR = os.environ.get('EDITOR','vim') #that easy!

SEPERATOR = '\n---\n'
NSEPERATOR = '\n' + SEPERATOR + '\n'

TAG_HINT_TEXT = """# Some hints for tags:
#
# ** Sources: @mine @obscure @rare @secret
# ** Problem Shape: @yesno @find @construct @bestpossible @hardanswer
# Quality: @favorite > @nice > @good > @ugly @work
# Philosophy: @instructive @reliable @justdoit @magic
# Philosophy': @smallcases @equalitycase @scouting @meta @dumb
# Philosophy'': @wishful @criticalclaim  @stronger @thinkbig
# Solution Method: @induct @manysolutions @magic @inefficient  @explicit @compute
# More tags: @pitfall @troll @intuitive @size @weak @maturity
# NT tags: @primes @p#adic @QR @pell @smallestprime @mods @fermat @zsig @cyclotomic @divis @order @christmas @CRT
# Algebra tags: @polynomial @trig @roots @calculus @continuity @irreducible @exactsum @manip
# Ineq tags: @holder @CDN @schur @AMGM @Titu @homogenize @dehomogenize @SOS @jensen @isofudge
# Combinatorics: @greedy @optimization @additivecombo @extreme @invariant @pigeonhole @parity @graph @adhoc @EV @combogeo @hall @grid @rigid
# Geometry tags
  # Part I and II: @anglechase @simtri @pop @homothety @cevalaus @trig @complex @bary @length
  # Part III: @inversion @polar @projective @harmonic @miquel @spiralsim @mixtilinear"""

USE_COLOR = True

# Color names {{{
TERM_COLOR = {}
TERM_COLOR["NORMAL"]          = ""
TERM_COLOR["RESET"]           = "\033[m"
TERM_COLOR["BOLD"]            = "\033[1m"
TERM_COLOR["RED"]             = "\033[31m"
TERM_COLOR["GREEN"]           = "\033[32m"
TERM_COLOR["YELLOW"]          = "\033[33m"
TERM_COLOR["BLUE"]            = "\033[34m"
TERM_COLOR["MAGENTA"]         = "\033[35m"
TERM_COLOR["CYAN"]            = "\033[36m"
TERM_COLOR["BOLD_RED"]        = "\033[1;31m"
TERM_COLOR["BOLD_GREEN"]      = "\033[1;32m"
TERM_COLOR["BOLD_YELLOW"]     = "\033[1;33m"
TERM_COLOR["BOLD_BLUE"]       = "\033[1;34m"
TERM_COLOR["BOLD_MAGENTA"]    = "\033[1;35m"
TERM_COLOR["BOLD_CYAN"]       = "\033[1;36m"
TERM_COLOR["BG_RED"]          = "\033[41m"
TERM_COLOR["BG_GREEN"]        = "\033[42m"
TERM_COLOR["BG_YELLOW"]       = "\033[43m"
TERM_COLOR["BG_BLUE"]         = "\033[44m"
TERM_COLOR["BG_MAGENTA"]      = "\033[45m"
TERM_COLOR["BG_CYAN"]         = "\033[46m"
if USE_COLOR is False:
	for key in TERM_COLOR.keys():
		TERM_COLOR[key] = ""
# }}}

def APPLY_COLOR(color_name, s):	
	return TERM_COLOR[color_name] + s + TERM_COLOR["RESET"]
