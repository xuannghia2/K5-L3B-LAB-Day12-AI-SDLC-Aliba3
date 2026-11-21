"""Exact freshness arithmetic with plain JSON item dictionaries at module boundaries."""

import math
from fractions import Fraction

from .ids import sort_by_id
from .inventory import validate_fresh_items


class FreshnessLedger:
    def __init__(self, tuning, ids):
        self.t, self.ids = tuning["freshness"], ids
        self.rates = {location: Fraction(str(self.t[key])) / 60 for location, key in
                      (("hold", "gather_decay_per_s"), ("stock", "quan_decay_per_s"))}
        self.denominator = math.lcm(*(rate.denominator for rate in self.rates.values()))
        self.threshold = Fraction(str(self.t["spoiled_below"]))
        self.values = {}

    def _exact(self, value):
        exact = Fraction(str(value))
        grid = Fraction(round(exact * self.denominator), self.denominator)
        # Recover an exact tick-grid value after JSON float roundtrip, only if
        # it has exactly the same floating representation as the supplied value.
        return grid if float(grid) == float(value) else exact

    def attach(self, items):
        result = validate_fresh_items(items)
        for item in result:
            self.ids.reserve(item["id"])
            self.values[item["id"]] = self._exact(item["fresh"])
        return result

    def new(self, kind, fresh=None):
        value = self.t["initial"] if fresh is None else fresh
        item = {"id": self.ids.new("I"), "kind": kind, "fresh": value}
        self.values[item["id"]] = self._exact(value)
        return item

    def decay(self, items, location):
        events = []
        for item in sort_by_id(items):
            ident = item["id"]
            previous = self.values.get(ident, self._exact(item["fresh"]))
            current = max(Fraction(0), previous - self.rates[location])
            self.values[ident] = current
            item["fresh"] = float(current)
            if previous >= self.threshold and current < self.threshold:
                events.append(("spoiled", {"item_id": ident, "kind": item["kind"], "location": location}))
        return events

    def spoiled(self, item):
        return self.values.get(item["id"], self._exact(item["fresh"])) < self.threshold


def copy_items(items, *, sorted_ids=False):
    return [dict(item) for item in (sort_by_id(items) if sorted_ids else items)]
