from frheed.gui import show
import cProfile
import pstats

with cProfile.Profile() as pr:
    show()


stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()