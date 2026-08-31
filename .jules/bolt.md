## 2025-05-20 - Pre-compile regex in WebFieldRule
**Learning:** Pre-compiling `re.compile` patterns in `WebFieldRule.__post_init__` using `object.__setattr__` for `frozen=True` dataclasses with `field(init=False, repr=False, compare=False)` avoids per-iteration regex compilation overhead during web extraction without modifying `__eq__` or `__repr__`.
**Action:** Always pre-compile regex patterns at rule instantiation time when processing repeating document or text extraction streams.
