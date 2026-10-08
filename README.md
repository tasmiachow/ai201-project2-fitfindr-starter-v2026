# FitFindr
## Tasmia Chowdhury 
> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is an app that allows users to ask for a specific article of clothing and also help you plan your fits. Our agent searches listings, works out what it would go with, and writes a caption for it.
---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Goes through our listings in data and returns items that match the user's query.
- **Inputs:** 
          description: string (User inputs a description of something they would like)
          size: string (small - large, etc) 
          max_price: float 

<!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:**  it returns a list[dict] --  A list of matching listing dicts, best match first. 
- **When it has nothing:** In the case the list is empty, it will stop the loop and ask the user to try for another item, since we don't have anything in our inventory that matches. 



### `suggest_outfit`

- **What it does:** Given a thrifted matched item and the user's wardrobe, suggest one outfit.
- **Inputs:** new_item: dict, wardrobe: dict
- **Returns:** A string suggesting an outfit with the new item and clothes the user already has in their wardrobe.
- **When it has nothing:** Returns a string saying it cannot suggest an outfit and the reason. Maybe the user only has shirts and is trying to buy another shirt. Stops the loop. 

### `create_fit_card`

- **What it does:** Write a short caption someone would actually post about the find.
- **Inputs:** outfit:  (str) the outfit suggestion string from suggest_outfit().
               new_item:  (dict) the listing dict for the item.
- **Returns:**  A two-to-four sentence caption. (str)
- **When it has nothing:** If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list ([]), append a message to the session indicating no matching items were found and terminate the workflow early without calling further tools. Otherwise, take the top matching listing (results[0]) and pass it to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex and string splitting (extracting keywords, size strings, and max price limits from the user's input).<!-- regex, string splitting, or asking the model — say which -->

**What moves through the session:** 

1. search_listings(description, size, max_price) returns a list of listing dicts (or [] if no matches).

2. If non-empty, results[0] (a listing dictionary containing fields like id, title, price, platform, size, brand) is extracted as new_item.

3. suggest_outfit(new_item=results[0], wardrobe=wardrobe) uses results[0] and the user's wardrobe dictionary to generate styling suggestions as an outfit string.

4. create_fit_card(outfit=outfit, new_item=results[0]) uses the generated outfit text along with results[0] to produce a social media caption string.

5. The session stores the results (selected item details, outfit text, and fit card caption) to present to the user.<!-- which fields, in what order -->

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask "A oversized flannel shirt that is XL under $30"

```
Output: 
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings
      in:  dict with keys: description, size, max_price
      out: 5 items: Oversized Flannel Shirt — Plaid Red/Black, Vintage Polo Shirt — Forest Green, Oversized Crewneck Sweatshirt — Vintage Navy … +2 more
[3] suggest_outfit
      in:  dict with keys: item
      out: Here are 2 complete outfit ideas using the red/black oversized flannel and your current wardrobe:  ### Outfit …
[4] create_fit_card
      in:  dict with keys: outfit
      out: Channeling effortless 90s skater energy with this Oversized Flannel Shirt in Plaid Red/Black scored on thredUp…

  Found:    Oversized Flannel Shirt — Plaid Red/Black — $22.0 on thredUp

  Outfit:   Here are 2 complete outfit ideas using the red/black oversized flannel and your current wardrobe:

### Outfit 1: Casual & Grunge-Leaning
* **Base Top:** White ribbed tank top
* **New Item:** Oversized Flannel Shirt (worn open as a layering piece)
* **Bottoms:** Baggy straight-leg jeans, dark wash
* **Shoes:** Chunky white sneakers
* **Accessories:** Black crossbody bag
* **Vibe:** Effortless, 90s skater-off-duty. The white tank keeps it crisp underneath the heavy red and black plaid, while the baggy dark-wash jeans and chunky sneakers lean into a relaxed, streetwear-inspired silhouette. 

### Outfit 2: Edgy Layered Streetwear
* **Base Top:** Black cropped zip hoodie
* **New Item:** Oversized Flannel Shirt (worn layered *over* the hoodie)
* **Bottoms:** Wide-leg khaki trousers
* **Shoes:** Black combat boots
* **Accessories:** Brown leather belt & Black crossbody bag
* **Vibe:** High-low texture mixing with an urban edge. Layering the open flannel over the black cropped hoodie creates a cool contrast in proportions against the structured wide-leg khakis, and the combat boots tie the whole utilitarian look together.

### Fit Card
Fit card: Channeling effortless 90s skater energy with this Oversized Flannel Shirt in Plaid Red/Black scored on thredUp for just $22.0. Whether I am layering it open over a crisp white tank or throwing it over a cropped hoodie, it instantly ties the whole grunge aesthetic together. Sustainable style has never looked so cozy.


**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]



```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

```
**Outfit 1: Casual & Effortless Casual**
*   **Top:** White ribbed tank top
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   **Vibe:** A classic, 90s-inspired off-duty look. Tucking the white ribbed tank into the medium-wash 501s creates a clean silhouette, while the vintage black denim jacket adds a cool double-denim contrast. Finished off with chunky white sneakers and the black crossbody, this is the ultimate comfortable yet put-together everyday uniform.

**Outfit 2: Edgy & Laid-Back**
*   **Top:** Oversized grey crewneck sweatshirt
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt, Black crossbody bag
*   **Vibe:** A relaxed, grunge-leaning streetwear aesthetic. Cinching the medium-wash 501s with the brown leather belt adds a nice touch of contrast when you do a "half-tuck" with the oversized grey crewneck. Pairing the denim with black combat boots grounds the look with a tough edge, making it perfect for weekend errands or going out to a casual venue.




```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

```
Nothing beats the effortless vibe of classic denim and fresh kicks for a day out. I am obsessed with how these Vintage Levi's 501 Jeans in medium wash fit every single time. Snagged this staple piece on depop for just $38.0 and I will definitely be living in them all season long.
---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave AI my search_listings implementation and asked why accessory items (like belts, hats, and bags) were still appearing in results when searching for specific pants/bottoms like vintage jeans with a specific size (W30 L30).
- *What came back:* AI identified that my _size_matches function was returning True for any item marked One Size / OS unconditionally. This caused One Size accessories to pass the size filter even when a explicit waist size like W30 L30 was requested.
- *What I changed:* I updated _size_matches so that One Size listings are only considered matches if the user did not specify a numeric/waist size requirement (has_numeric_wanted), properly filtering out irrelevant accessories when exact sizes are specified.

**Moment 2**

- *What I asked for:* I asked why calling suggest_outfit threw TypeError: generate() got an unexpected keyword argument 'system_prompt' when testing with the Gemini API.
- *What came back:* AI explained that the project's custom generate() wrapper function in generate.py does not accept system_prompt as a keyword argument.
- *What I changed:* I refactored both suggest_outfit and create_fit_card in tools.py to embed the system instructions directly at the top of the prompt string and called generate(prompt=prompt) with a single argument instead.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
