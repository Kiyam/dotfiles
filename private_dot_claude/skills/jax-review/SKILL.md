---
name: jax-review
description: Review, debug, and write idiomatic JAX code following best practices. Use this whenever the task involves JAX — precision/dtypes, PRNGKey handling, jit/vmap/scan, custom_vjp, NaN gradients, GPU/TPU memory, pytrees, or "why is my JAX slow / wrong / out of memory / recompiling / non-differentiable". Trigger it both for reviewing existing JAX code and for writing new JAX from scratch, and for any JAX numerics question even phrased casually ("my gradient is NaN", "jit recompiles every call", "JAX eats all my GPU memory").
---

# JAX Review & Implementation

JAX is unforgiving in specific, recurring ways: silent dtype choices, traced-value control flow, async dispatch, and gradients that go NaN where the math is fine. Apply these checks when **writing new JAX code** or **reviewing existing code**. When implementing, write code that already satisfies these by construction rather than producing something to be fixed later.

## Precision and dtypes — decide deliberately

JAX defaults to **float32**. This is correct for most deep learning, but wrong for numerical work (linear solves, FFTs, accumulations, ill-conditioned problems) where you'd reach for double in NumPy. So the rule is: **match precision to the workload, on purpose.**

- If float64 is needed, enable it **before any array is created**:
  ```python
  import jax
  jax.config.update("jax_enable_x64", True)
  ```
  or set `JAX_ENABLE_X64=1` in the environment. Setting it after arrays exist silently does nothing. Verify with `jnp.zeros(1).dtype`.
- For training, consider `bfloat16`/`float16` mixed precision deliberately rather than by accident — keep a float32 master copy of params, cast inside the forward pass.
- Watch **silent downcasts**: a stray Python float or float32 constant pulled into an expression can demote the whole thing. Pin dtypes on constants in precision-sensitive paths.

## Randomness — PRNGKey discipline

JAX RNG is stateless and explicit. The recurring bugs:
- **Never reuse a key.** Same key → identical "random" draws. Split: `key, subkey = jax.random.split(key)`.
- Splitting the *same* key twice yields the *same* children — thread keys through, don't re-split a stale one.
- Prefer the typed-key API (`jax.random.key(seed)`) over legacy `PRNGKey` for new code; it catches misuse.
- Inside a `scan`/`vmap`, split a batch of keys up front (`jax.random.split(key, N)`) and map over them — don't derive keys inside the loop body from a carried scalar seed.

## Control flow and `jit`

- Python `if`/`for` on **traced** values fails or silently bakes in a constant. Use `jax.lax.cond`, `jax.lax.select`, `jax.lax.scan`, `jax.lax.fori_loop`.
- Replace long Python loops with `lax.scan` — an unrolled Python loop builds a giant graph and compile time explodes (a very common cause of "jit takes forever"). `scan` compiles the body once.
- **Recompilation every call** = input shape or a static argument changed, or Python scalars are passed where arrays belong. Mark genuinely-static args with `static_argnums`; avoid passing Python scalars that vary. Re-tracing each call silently destroys performance.
- Debug prints inside jit: `jax.debug.print("{}", x)` — plain `print` runs at trace time and shows tracers, not values.

## NaN gradients — the classic traps

Forward value finite, gradient NaN. Almost always:
- **`sqrt`, `log`, `pow`, `norm` at 0** — derivative blows up even where the value is defined. Use the *double-where* trick:
  ```python
  safe_x = jnp.where(x > 0, x, 1.0)
  out = jnp.where(x > 0, jnp.sqrt(safe_x), 0.0)
  ```
  A single `where` is not enough — the bad branch is still evaluated and propagates a NaN gradient. Mask the **input** too.
- Saturating `clip`/`where` then differentiating through the saturated region.
- Turn on `jax.config.update("jax_debug_nans", True)` to halt at the first NaN and localize it (disable in production — it forces host syncs).
- For genuinely non-differentiable or numerically nasty ops, define a clean `jax.custom_vjp` rather than fighting autodiff.

## Memory and performance (GPU/TPU)

- JAX **preallocates ~75% of GPU memory** on first use. To share the device or see the true footprint: `XLA_PYTHON_CLIENT_PREALLOCATE=false` and/or `XLA_PYTHON_CLIENT_MEM_FRACTION=.5`.
- **Host–device sync kills throughput.** Any `print(array)`, `.item()`, `float(x)`, `if array > 0`, or `np.asarray(x)` in a hot loop forces a sync. Keep everything on-device; pull results out once at the end.
- Backward-pass OOM → `jax.checkpoint` (a.k.a. `jax.remat`) on the expensive sub-function to trade compute for memory.
- Time with `jax.block_until_ready()` around the section — dispatch is async, so naïve timing measures dispatch, not compute.
- `donate_argnums` lets XLA reuse input buffers for large arrays not needed afterwards.

## Pytrees and shapes

- Custom containers must be registered pytrees or `jit`/`grad` won't traverse them — use `flax.struct.dataclass` or `chex.dataclass` for parameter bundles.
- `vmap` `in_axes`/`out_axes` mismatches give confusing rank errors — annotate explicitly when batching.
- Shapes are static under jit: dynamic-shape outputs (e.g. boolean-masked selection) don't work; restructure to fixed shapes with masks.

## Idiom and structure

- Pure functions: no side effects, no in-place mutation (`x.at[i].set(v)` returns a new array).
- Prefer `vmap` over manual batching dimensions; prefer `scan` over accumulating in a Python list.
- Keep `jit` boundaries at the largest sensible unit (whole step/epoch body), not wrapped around every tiny function.

## Review output format

When reviewing, order findings:
1. **Correctness bugs** (precision, RNG reuse, NaN-prone ops, impure mutation) — these change results silently; lead with them.
2. **Performance** (recompilation, host sync, Python loops, memory).
3. **Style/robustness** (pytree registration, explicit dtypes, jit boundaries, asserts).

Give the concrete fix with a snippet, not just the diagnosis — name the exact line and the exact replacement.
