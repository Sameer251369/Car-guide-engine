# Car Guide Media — Fix Car Listing + Build On-Road Price Calculator

## Context

We have a verified master dataset extracted from `India_Car_Master_Database_2026_Statewise_OnRoad_Prices.pdf`:

- **301 unique cars** (`india_car_models_301.json`) — brand, car name, body type, fuel type
- **36 states/UTs** (`india_states_28.json`) — name + 2-letter code, including Jammu & Kashmir, Ladakh, Delhi, Chandigarh, Puducherry, Andaman & Nicobar, Lakshadweep, and Dadra & Nagar Haveli and Daman & Diu
- **8,428 state-wise price rows** (`india_car_master_2026.json` / `.csv`) — one row per (car × state), each with `start_ex_inr`, `top_ex_inr`, `start_otr_inr`, `top_otr_inr`

3 cars (Force Motors Gurkha EV, Renault Arkana, Volkswagen Golf) are unlaunched and have `null` prices in all 28 states ("TBA") — 84 of the 8,428 rows. Handle this explicitly; don't silently drop them.

This is a **precomputed lookup table**, not a flat tax percentage — rates vary by state, price band, and fuel (EVs get materially lower effective rates in every state). Do not try to reverse-engineer a single "% road tax per state" constant; import the table and interpolate against it.

---

## Part 1 — Diagnose and fix why not all 301 cars show in the UI

Work through this checklist against the actual codebase (don't guess — check each one):

1. **Backend query**: Does the car list endpoint have an unbounded default page size, or a `.filter()` that unintentionally excludes rows (e.g. `price__isnull=False`, `is_active=True` with a stale flag, a `.distinct()` bug after a join, or a `LIMIT`/slice left over from testing)?
2. **Serializer**: Does any field raise/skip silently when a related price row is `None` (the 3 TBA cars)? Confirm the serializer returns cars with `price: null` rather than raising an exception that DRF swallows into a 500 mid-pagination.
3. **Pagination**: If using DRF `PageNumberPagination`/`LimitOffsetPagination`, confirm the frontend actually loops through all pages rather than rendering only page 1. Check `count` vs rendered length in the browser network tab.
4. **Duplicate keys / unique constraint**: If cars were imported more than once with a slightly different slug/name, some may be silently overwritten or produce React key collisions that suppress rendering (same `key` prop → only last one paints).
5. **Frontend fetch**: Confirm the fetch/query hook isn't capped (`useState` initial slice, `.slice(0, N)` left in from a placeholder, or a `take: 20` on a react-query call).

Report back exactly which of these was the cause before writing the fix — don't paper over it with a higher limit number without knowing why the old one existed.

---

## Part 2 — Import the real dataset

Replace any placeholder/seed car data with the verified files:

1. `india_states_28.json` → seed a `State` model (`name`, `code`) — exactly these 28, no more, no less.
2. `india_car_models_301.json` → seed/reconcile the `Car` model (`brand`, `name`, `body_type`, `fuel_type`). Match against existing DB rows by `(brand, name)` — update in place rather than duplicating if a car already exists.
3. `india_car_master_2026.json` / `.csv` → new `StateOnRoadPrice` model:

```python
class StateOnRoadPrice(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="state_prices")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="car_prices")
    start_ex_showroom = models.BigIntegerField(null=True, blank=True)   # paise-free INR, null = TBA
    top_ex_showroom = models.BigIntegerField(null=True, blank=True)
    start_on_road = models.BigIntegerField(null=True, blank=True)
    top_on_road = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("car", "state")
```

Write a management command (`import_car_master.py`) that upserts from the JSON — idempotent, safe to re-run, logs a summary count of created/updated/skipped rows at the end so a partial import is visible immediately instead of failing silently.

---

## Part 3 — On-road price calculator logic

Given a car and a state, the calculator should:

1. Look up the `StateOnRoadPrice` row for `(car, state)`.
2. If the user hasn't specified a variant price, or picks "starting price" / "top variant", return `start_on_road` / `top_on_road` directly — no computation needed, these are already the verified figures.
3. If the user enters a **custom ex-showroom price** between `start_ex_showroom` and `top_ex_showroom` (e.g. a specific variant not separately listed), **linearly interpolate** the on-road price rather than reapplying a flat percentage:

```python
def estimate_on_road(row, user_ex_price):
    if row.start_ex_showroom is None:
        return None  # TBA car — show "Price to be announced" in UI
    if row.top_ex_showroom == row.start_ex_showroom:
        return row.start_on_road
    ratio = (user_ex_price - row.start_ex_showroom) / (row.top_ex_showroom - row.start_ex_showroom)
    ratio = max(0, min(1, ratio))  # clamp — don't extrapolate past the known band
    return round(row.start_on_road + ratio * (row.top_on_road - row.start_on_road))
```

4. If `user_ex_price` falls outside the known `[start_ex_showroom, top_ex_showroom]` band, clamp to the nearest known figure and flag it in the response (`"note": "estimated from nearest known variant"`) rather than extrapolating silently — extrapolated tax slabs are unreliable at price-band boundaries.
5. For the 3 TBA cars, disable price entry entirely in the UI for those state/car combos and show "Price to be announced" instead of a broken calculation.

### Mandatory disclaimer (use this exact text under every calculator result)

> Estimated on-road price = ex-showroom + state road tax + ₹600 registration + ₹400 HSRP + ₹500 FASTag + estimated comprehensive insurance + ₹1,000 miscellaneous charges. Excludes TCS, loan/hypothecation charges, accessories, dealer handling, discounts, city-specific municipal charges, and special imported/CBU rules. EV road-tax waivers are applied where reported. Actual on-road price can differ by city, RTO, variant, insurer, and state notification — please verify with your local RTO/dealer before purchase.

---

## Part 4 — Lead capture

Keep the existing lead-capture flow attached to the calculator, but capture `state` and `car` as structured fields (not just a free-text note) so leads are filterable by state and model in the dashboard — this is directly useful for the monetization angle already scoped.

---

## Part 5 — QA checklist before calling this done

- [ ] Car list UI shows exactly 301 cars (or 298 fully-priced + 3 flagged "Price TBA", your call on which — but state the number and confirm it matches)
- [ ] State dropdown has exactly these 28 states, alphabetical, with codes matching `india_states_28.json`
- [ ] Selecting any car + any state returns a price within 1 second, sourced from `StateOnRoadPrice`, not recomputed from scratch
- [ ] Custom price entry between start/top interpolates correctly (spot-check 2–3 cars against the source PDF)
- [ ] TBA cars don't crash the calculator or produce `₹NaN` / `₹null`
- [ ] Disclaimer text renders under every result
- [ ] Re-running the import command doesn't duplicate rows
