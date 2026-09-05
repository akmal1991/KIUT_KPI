"""Shared co-authorship scoring rules for the faculty submission flow.

Mirrors the same three distribution policies used across the KPI matrix:
SOLO (one author, full points), FLAT_TEAM (every attached member gets the
full amount, capped at max_co_authors total members), and WEIGHTED_SPLIT
(lead gets 100%, each co-author gets category.co_author_share_percent,
capped at max_co_authors co-authors beyond the lead).
"""


def max_total_authors(category):
    """How many people (lead included) may be attached to one submission."""
    if category.distribution == category.Distribution.SOLO:
        return 1
    if category.distribution == category.Distribution.FLAT_TEAM:
        return category.max_co_authors or 1
    return 1 + (category.max_co_authors or 0)


def estimate_score(category, is_lead, academic_year=None):
    """Points a single author (lead or co-author) earns for this category."""
    base = category.get_coef(academic_year)
    if category.distribution == category.Distribution.WEIGHTED_SPLIT and not is_lead:
        return round(base * (category.co_author_share_percent / 100), 2)
    return round(base, 2)
