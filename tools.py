"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re


# ── Tool 1: search_listings ───────────────────────────────────────────────────

'''stopwords are useless buffer words'''

_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "in", "of", "to", "on", "at", "by", "is", "it"
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    """Extract tokens from size string safely."""
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]  # Fixed: added () to upper()
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    """Check if the wanted size matches the listing size."""
    if not wanted:
        return True
    
    listing_tokens = _size_tokens(listing_size)
    if not listing_tokens:
        return False

    wanted_tokens = _size_tokens(wanted)

    # 1. Direct exact token match (e.g. 'M' in {'S', 'M'})
    if wanted_tokens & listing_tokens:
        return True

    # 2. Allow 'ONE SIZE' / 'OS' for category matches
    # (Category compatibility is handled during scoring/filtering)
    if any("ONE" in t or t == "OS" for t in listing_tokens):
        return True

    # 3. Match waist/numeric sizes cleanly (e.g. 'W30 L30' matching 'W30' or '30')
    clean_wanted = {re.sub(r"^[WL]", "", t) for t in wanted_tokens if re.search(r"\d+", t)}
    clean_listing = {re.sub(r"^[WL]", "", t) for t in listing_tokens if re.search(r"\d+", t)}

    if clean_wanted and clean_listing:
        return bool(clean_wanted & clean_listing)

    return False

def _get_listing_text(item: dict) -> str:
    """Combine all searchable textual fields from a listing."""
    fields = [
        item.get("title", ""),
        item.get("description", ""),
        item.get("category", ""),
        " ".join(item.get("style_tags", [])),
        " ".join(item.get("colors", [])),
        item.get("brand") or ""
    ]
    return " ".join(fields)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
    listings = load_listings()

    # 1. Price Filter (Inclusive)
    if max_price is not None:
        listings = [item for item in listings if item.get("price", 0) <= max_price]

    # 2. Size Filter
    if size:
        listings = [item for item in listings if _size_matches(size, item.get("size", ""))]

    # 3. Score listings by keyword overlap
    query_keywords = _keywords(description)
    if not query_keywords:
        return []

    scored_listings = []
    for item in listings:
        # Give higher weight to matches in title and category over accessories/tags
        title_keywords = _keywords(item.get("title", ""))
        category_keywords = _keywords(item.get("category", ""))
        all_item_words = _keywords(_get_listing_text(item))

        # Core overlap
        overlap_score = len(query_keywords & all_item_words)

        # Bonus weight if query keywords explicitly hit title or category
        if query_keywords & title_keywords:
            overlap_score += 1
        if query_keywords & category_keywords:
            overlap_score += 1

        # Drop anything scoring zero
        if overlap_score > 0:
            item_copy = item.copy()
            item_copy["score"] = overlap_score
            scored_listings.append(item_copy)

    # 4. Sort by score descending and cap at SEARCH_RESULT_LIMIT
    scored_listings.sort(key=lambda x: x["score"], reverse=True)

    results = []
    limit = getattr(config, "SEARCH_RESULT_LIMIT", 10)
    for item in scored_listings[:limit]:
        item.pop("score", None)
        results.append(item)

    return results

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    return ""


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # TODO: replace this with your implementation
    return ""
