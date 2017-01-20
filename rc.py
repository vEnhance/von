import os

VON_BASE_PATH  = os.path.join(os.environ.get("HOME", ""), "Dropbox/OlyBase/")
VON_INDEX_NAME = "index"
VON_INDEX_PATH = os.path.join(VON_BASE_PATH, VON_INDEX_NAME)
VON_CACHE_NAME = "cache"
VON_CACHE_PATH = os.path.join(VON_BASE_PATH, VON_CACHE_NAME)

EDITOR = os.environ.get('EDITOR','vim') # that easy!

SEPERATOR = '\n---\n'
NSEPERATOR = '\n' + SEPERATOR + '\n'

TAG_HINT_TEXT = """# Some hints for tags:
#
# *** Difficulty: @trivial @aleph @bet @dalet @gimel @zayin @yod @kurumi
# *** Sources: @mine @obscure @rare @secret @exam @blind @well
# *** Problem Shape: @yesno @find @construct @bestpossible @hardanswer @aime
# (here @well means I spent a lot of time on the problem myself)
#
# Quality: @favorite > @nice > @good > @ugly @work
# Philosophy: @instructive @reliable @justdoit @magic @contrived
# Philosophy': @smallcases @equalitycase @scouting @meta @dumb
# Philosophy'': @wishful @criticalclaim @stronger @thinkbig
# Solution Method: @induct @manysolutions @magic @inefficient @explicit @compute
# More tags: @pitfall @troll @intuitive @size @weak @maturity
#
# NT:    @primes @p-adic @QR @pell @smallestprime @mods @euclid
#        @fermat @zsig @cyclotomic @divis @order @christmas @CRT
# Alg:   @polynomial @trig @roots @calculus @genfunc
#        @continuity @irreducible @exactsum @manip
# FE:    @cauchy @pointwise @cancel @symmetry @bump @isolated
# Ineq:  @holder @CDN @schur @AMGM @Titu @homogenize
#        @dehomogenize @SOS @jensen @isofudge @nEV
# Combo: @greedy @optimization @additivecombo @extreme @invariant
#        @free @pigeonhole @parity @graph @adhoc @EV @global @local
#        @hall @grid @rigid @perturb @algorithm @linalg @combogeo
# Geometry tags
  # Part I and II: @anglechase @simtri @pop @homothety @config
  #                @cevalaus @trig @complex @bary @length
  # Part III:      @inversion @polar @projective @harmonic
  #                @miquel @spiralsim @mixtilinear"""

USE_COLOR = True
KEY_CHAR = 'C~'

DIFFS= ['trivial', 'aleph', 'bet', 'dalet', 'gimel', 
		'zayin', 'yod', 'kurumi']
