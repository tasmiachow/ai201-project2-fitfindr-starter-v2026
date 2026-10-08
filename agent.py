"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
import re
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }

# ── query parser ──────────────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    """
    Parses user query into description, size, and max_price using regex and string splitting.
    """
    text = query.strip()

    # 1. Extract max_price (e.g. "under $30", "$30", "under 30 dollars")
    max_price = None
    price_match = re.search(r"(?:under|\$)\s*(\d+(?:\.\d{1,2})?)", text, re.IGNORECASE)
    if price_match:
        max_price = float(price_match.group(1))

    # 2. Extract size (e.g. "size M", "size W30 L30", "size S/M", "size 30")
    size = None
    size_match = re.search(r"\bsize\s+([A-Za-z0-9/\s]+?)(?=\s+under|\s+\$|\s+for|\s*$)", text, re.IGNORECASE)
    if size_match:
        size = size_match.group(1).strip()

    # 3. Clean query into description keywords
    clean_desc = text
    if price_match:
        clean_desc = re.sub(r"(?:under|\$)\s*\d+(?:\.\d{1,2})?", "", clean_desc, flags=re.IGNORECASE)
    if size_match:
        clean_desc = re.sub(r"\bsize\s+[A-Za-z0-9/\s]+", "", clean_desc, flags=re.IGNORECASE)

    # Clean up excess words like "looking for a", "under", "for"
    clean_desc = re.sub(r"\b(looking|for|a|an|under)\b", "", clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    return {
        "description": clean_desc or text,
        "size": size,
        "max_price": max_price,
    }
# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    # TODO: delete these two lines and build the loop.
    session = new_session(query, wardrobe)
    iterations = 0

    try:
        # Step 1: Track iteration limit
        iterations += 1
        trace.check_iterations(iterations)

        # Step 2: Parse query
        parsed = parse_query(query)
        session["parsed"] = parsed
        trace.step("parse_query", inputs={"query": query}, returned=parsed)

        # Step 3: Search listings
        results = search_listings(
            description=parsed["description"],
            size=parsed["size"],
            max_price=parsed["max_price"],
        )
        session["search_results"] = results
        trace.step("search_listings", inputs=parsed, returned=results)

        # Step 4: Branch Check — stop early if no listings match
        if not results:
            msg = (
                f"No items matched '{query}'. Try widening your budget, "
                "searching for a broader item type, or adjusting your size requirement."
            )
            session["error"] = msg
            return session

        # Step 5: Select top match
        selected = results[0]
        session["selected_item"] = selected

        # Step 6: Suggest Outfit
        iterations += 1
        trace.check_iterations(iterations)
        
        outfit = suggest_outfit(selected, session["wardrobe"])
        session["outfit_suggestion"] = outfit
        trace.step("suggest_outfit", inputs={"item": selected["title"]}, returned=outfit)

        # Step 7: Create Fit Card Caption
        iterations += 1
        trace.check_iterations(iterations)

        fit_card = create_fit_card(outfit, selected)
        session["fit_card"] = fit_card
        trace.step("create_fit_card", inputs={"outfit": outfit}, returned=fit_card)

    except ModelUnavailable as e:
        session["error"] = f"Model service unavailable: {e}"

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
