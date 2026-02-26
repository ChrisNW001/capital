# Pitfalls Research

**Domain:** Adding Gemini/Imagen visual generation to existing Python CLI pitchdeck tool
**Researched:** 2026-02-26
**Confidence:** HIGH (critical pitfalls), MEDIUM (integration pitfalls), HIGH (image API pitfalls)

---

## Critical Pitfalls

### Pitfall 1: Imagen Prompts Are English-Only

**What goes wrong:**
The Gemini Developer API (`google-genai` SDK, AI Studio key) rejects Imagen prompts in non-English languages with a content or parameter error. The `language` parameter that supports German (`de`) is a **Vertex AI-only feature** — it does not work via the Gemini Developer API. Since this project uses `GEMINI_API_KEY` (AI Studio / Developer API), all image generation prompts must be in English even when generating slides with German content.

**Why it happens:**
The official docs state "Imagen supports English only prompts at this time" for the Developer API. The language translation feature (`language: "de"`) exists only on Vertex AI. Developers reading general Imagen docs find the German language code example but don't notice the Vertex AI restriction note.

**How to avoid:**
- All prompts passed to `generate_images()` must be in English regardless of slide content language.
- If slide content is in German, the Gemini elaboration step must translate content to English before constructing the image prompt.
- Document this constraint explicitly in the design engine module docstring.
- Never pass raw German slide text directly into the Imagen prompt.

**Warning signs:**
- Prompt returns a content policy error or empty image list for non-English text
- Error messages like "The prompt couldn't be submitted" on prompts that contain German words
- Images with garbled or random character sequences in text areas

**Phase to address:**
Phase 1 (Design Engine Foundation) — must be a hard constraint in the elaboration step architecture, not a patch applied later.

---

### Pitfall 2: The 2-Step Pipeline Has No Validation Firewall Between Steps

**What goes wrong:**
Gemini elaborates a slide description into an Imagen prompt. If the elaborated prompt is too abstract, too long (>480 tokens), contains policy-triggering language from business content (e.g., "disruptive," competitor names, financial projections framed as claims), or hallucinates layout instructions the image model ignores, the Imagen call either fails or produces an image that looks nothing like the expected slide. Since the pipeline runs sequentially for 15 slides, one bad elaboration silently corrupts downstream slides and the user gets an incomplete deck with no clear error.

**Why it happens:**
Cascading failures in LLM chains compound early errors into system-wide failures. The elaboration step treats the XML design system as instruction — Gemini may "interpret" it rather than faithfully reproduce layout specs. Without an intermediate validation layer, the pipeline has no awareness of elaboration quality before spending API quota on generation.

**How to avoid:**
- Add a prompt validation step between elaboration and generation: check token count (max 480), check for known policy trigger patterns, check that key layout terms from the design system appear in the prompt.
- Implement per-slide try/except isolation — one failed slide should not abort the entire deck run.
- Log the elaborated prompt alongside each generated image for debugging.
- Set a `--dry-run` mode that runs elaboration for all slides and prints prompts without calling Imagen, allowing prompt inspection before spending generation quota.

**Warning signs:**
- Elaborated prompts longer than 480 tokens (measure before sending)
- Image output that omits key slide elements (title, chart, brand color)
- Intermittent failures affecting only specific slide types (e.g., "Traction" slide with metrics data)

**Phase to address:**
Phase 1 (Design Engine Foundation) — build the validation firewall into the pipeline architecture before any image generation is wired in.

---

### Pitfall 3: Imagen Content Filter Silently Drops Images Instead of Raising an Exception

**What goes wrong:**
When Imagen's content policy filter triggers, it does not always raise an exception. Instead, it returns fewer images than requested (`number_of_images=1` yields 0 results) or returns a response with no `generated_images` list. Code that doesn't check `len(response.generated_images)` before accessing index 0 raises an `IndexError` that looks like a bug rather than a policy rejection. Business content (competitive comparisons, financial projections, certain market size claims) can trigger filters unexpectedly.

**Why it happens:**
The API spec says "if fewer images than requested are returned, some generated output may be blocked." Developers assume one request = one result and write `image_bytes = response.generated_images[0].image.image_bytes` without a guard. This crashes with a misleading `IndexError`.

**How to avoid:**
- Always check `if not response.generated_images:` after each `generate_images()` call.
- Set `include_rai_reason=True` in `GenerateImagesConfig` to get a reason string when images are blocked.
- Implement a fallback: on filter rejection, simplify the prompt (remove named entities, numbers, competitor references) and retry once before surfacing a user-facing error.
- Surface a clear error: "Slide N image blocked by content filter — simplified prompt also rejected. Manual review needed."

**Warning signs:**
- `IndexError` on `response.generated_images[0]` — first debugging clue that filter triggered
- Filter rate increases when slides contain market size figures, named competitors, or aggressive growth claims
- `include_rai_reason` returns a reason string rather than None

**Phase to address:**
Phase 2 (Imagen Integration) — build this guard at the generation call site, not as a later patch.

---

### Pitfall 4: SDK Confusion — `google-generativeai` Is Dead, Only `google-genai` Works

**What goes wrong:**
Anyone searching PyPI or Stack Overflow finds two Google AI Python packages: `google-generativeai` (old) and `google-genai` (new). The old SDK reached end-of-life on November 30, 2025. Imagen 4 models (`imagen-4.0-generate-001`, `imagen-4.0-ultra-generate-001`, `imagen-4.0-fast-generate-001`) are not available in the deprecated SDK. If `pyproject.toml` installs `google-generativeai`, the import path (`import google.generativeai as genai`) is different from the new SDK (`from google import genai`), and image generation calls fail with `AttributeError` or `404 NOT_FOUND` on the model ID.

**Why it happens:**
The two packages have nearly identical names and the old one still installs cleanly. Old tutorials and Stack Overflow answers up to mid-2025 reference `google-generativeai`. The new unified SDK only reached GA in May 2025.

**How to avoid:**
- Install only `google-genai` (not `google-generativeai`) in `pyproject.toml`.
- Use the canonical import: `from google import genai` and `client = genai.Client(api_key=...)`.
- Do not mix old and new SDK patterns in the same module.
- Add a comment in `pyproject.toml` noting the deprecation to prevent future developers from "fixing" the package name.

**Warning signs:**
- `ImportError: cannot import name 'GenerateImagesConfig' from 'google.generativeai'`
- `404 NOT_FOUND: models/imagen-4.0-generate-001 is not found for API version v1beta`
- Both packages installed simultaneously (pip freeze shows both)

**Phase to address:**
Phase 1 (Design Engine Foundation) / dependency setup — must be correct before any code is written.

---

### Pitfall 5: 4K PNG Memory Accumulation Crashes CLI Mid-Deck

**What goes wrong:**
A 15-slide deck with 4K PNGs (3840×2160) can consume 450–750 MB of RAM if all images are held in memory simultaneously (each uncompressed 4K image is ~25 MB in-memory as RGB pixel data, plus Pillow metadata). Without explicit memory management, the CLI process grows unconstrained across the slide generation loop and can crash on machines with <2 GB free RAM before any images are written to disk.

**Why it happens:**
Developers write a loop that collects all `image_bytes` objects into a list for later ZIP assembly. Pillow's memory leak issues (documented in issues #3610, #5797, #6448) mean `Image.close()` does not always release memory immediately. Each iteration adds to the heap without releasing previous images.

**How to avoid:**
- Write each PNG to disk immediately after generation, before moving to the next slide.
- Use context managers for all Pillow operations: `with Image.open(BytesIO(img_bytes)) as img:`.
- Process slides sequentially, never holding more than one decoded image in memory at once.
- Use `gc.collect()` after writing each image if memory pressure is observed during testing.
- For the ZIP assembly step, stream files from disk rather than re-loading all images into memory.

**Warning signs:**
- Process memory grows monotonically throughout the slide generation loop (observe with `psutil`)
- `MemoryError` or `OSError: [Errno 12] Cannot allocate memory` on larger decks
- Crash occurs consistently at the same slide number (memory threshold)

**Phase to address:**
Phase 2 (Imagen Integration) — design the generation loop with write-immediately semantics from the start.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hold all images in memory, then ZIP | Simpler loop logic | OOM crash on full 15-slide decks; unrecoverable state | Never — write-to-disk immediately is not significantly more complex |
| Single monolithic `design` function | Faster to prototype | Cannot unit test elaboration separate from generation; makes rate limit retries impossible to isolate | Never for production code |
| Skip per-slide error handling, let exceptions bubble | Less boilerplate | One content-filtered slide aborts entire deck run, user loses all work | Never — slides are independent units |
| Hardcode design system XML inline | Avoids file I/O complexity | Cannot swap/update design systems; XML changes require code changes | MVP only, must be file-loaded before shipping |
| Use `img2pdf` directly without intermediate Pillow step | Simpler for PNG-to-PDF | Cannot apply any post-processing (watermarks, resizing, compression); breaks future logo overlay feature | Only if PDF assembly is a pure pass-through and zero post-processing is ever needed |
| Skip progress reporting for the 15-slide generation loop | Saves ~30 lines | User sees no output for 5-10 minutes — looks like a hang; likely to Ctrl+C | Never — this is a CLI tool |
| Ignore `GEMINI_API_KEY` absence until first API call | Lazy initialization | Confusing error buried in stack trace mid-run; user doesn't know why it failed | Never — check at command entry like existing `ANTHROPIC_API_KEY` pattern |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Gemini API (elaboration) | Using `google-generativeai` (deprecated SDK) | Install and import only `google-genai`; use `from google import genai` |
| Imagen API (generation) | Assuming `generate_images()` always returns one image | Always check `len(response.generated_images) > 0` before indexing |
| Imagen API | Not catching `ClientError` for 429 rate limit | Catch `google.genai.errors.ClientError`, check status code, implement exponential backoff |
| Imagen API | Sending German-language prompts directly | Translate content to English before constructing image prompt; Gemini Developer API is English-only |
| Imagen API | Prompts exceeding 480 tokens | Measure token count before sending; truncate or summarize elaborated prompts |
| Imagen API | Requesting 4K via pixel dimensions | Use `aspect_ratio="16:9"` + `output_image_size="2K"` (API-controlled sizing); do not try to specify `3840x2160` directly in GenerateImagesConfig |
| Anthropic + Google dual SDK | Sharing a single module for both clients | Keep `engine/narrative.py` (Anthropic) and `engine/design.py` (Google) completely separate; each owns its client init and error types |
| `.env` key loading | Assuming `load_dotenv()` at top of `cli.py` covers all subprocesses | `load_dotenv()` is already called at CLI entry — verify it runs before any engine module initialization; GEMINI_API_KEY check should mirror the ANTHROPIC_API_KEY pattern in `cli.py` |
| Reportlab PDF assembly | Embedding uncompressed 4K PNGs | Compress images before embedding; large uncompressed images make reportlab PDFs 200+ MB |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential Gemini elaboration + Imagen generation with no per-slide timeout | Total run time 8-15 minutes for 15 slides; user cannot interrupt cleanly | Set a per-slide timeout (e.g., 60s for elaboration, 120s for generation); surface progress per slide | Every run — this is the baseline behavior, not a scale issue |
| Reloading all 3 design system XMLs from disk for every slide | Not noticeable for 1-2 runs | Disk I/O accumulates; XML parsing is repeated 15x unnecessarily | At development time when iterating on prompts |
| PDF assembly loading all 15 4K PNGs back into Pillow from disk simultaneously | Works on 16 GB RAM machines | `MemoryError` on machines with <4 GB free | Always on constrained CI or low-memory dev machines |
| Not caching the elaborated prompt template (design system context) across slides | Extra Gemini tokens per slide | Ephemeral prompt caching for the design system XML (same pattern as existing `narrative.py`) saves significant cost | After >5 decks generated — cache pays for itself |
| Generating all slides before saving any output | Full pipeline completes before any file is written | Write each PNG to disk immediately; produce partial ZIP on interrupt | Whenever user Ctrl+C mid-run — loses all work |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing `.env` with both `ANTHROPIC_API_KEY` and `GEMINI_API_KEY` | Both API keys compromised; billing liability for both providers | `.env` is in `.gitignore` (already set); verify this covers the new key too |
| Logging elaborated prompts that contain company financial data | Sensitive company metrics appear in log files or stdout in plaintext | Use DEBUG-level logging only; never print raw company data outside of the existing `--verbose` flow |
| Passing slide `bullets` and `metrics` verbatim into Imagen prompts | Company-confidential metrics embedded in generation API requests sent to Google | Use abstracted visual descriptions ("a bar chart showing growth") rather than actual metric values in Imagen prompts |
| No quota guard for generation loop | Runaway loop exhausts daily Imagen quota (5-20 requests/day on free tier) in a single run | Check quota-exhaustion (429) at the start of the loop; offer `--slides 1-5` range flag for partial generation |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No per-slide progress during 10-minute generation run | User has no feedback; assumes tool is hung; Ctrl+C | Rich progress bar with current slide number: "Generating slide 7/15: Traction..." |
| Dumping raw stack trace on content filter rejection | Confusing error for non-technical founders | Catch `ClientError`, map to "Slide N was blocked by Google's content filter — try regenerating or editing slide content" |
| Overwriting existing output files without warning | User loses previous generation run | Check if output directory exists and is non-empty; prompt before overwriting or add `--force` flag |
| Exiting with code 0 when some slides failed content filter | Automation scripts assume success | Exit with non-zero code when any slide generation fails; report partial success clearly |
| No indication of total file size before ZIP/PDF assembly | User surprised by 200+ MB PDF | Print estimated output size before assembly: "Assembling 15 slides (~180 MB PDF)..." |
| Mixing Rich console output with PDF binary stdout | Garbled terminal if user pipes output | Never write binary output to stdout; always use file paths |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Image generation loop:** Often missing per-slide error isolation — verify that a single content-filter rejection on slide 7 does not abort slides 8-15.
- [ ] **GEMINI_API_KEY check:** Often missing at CLI entry — verify it raises a user-friendly error before any API call is made, matching the `ANTHROPIC_API_KEY` pattern in `cli.py`.
- [ ] **English-only constraint:** Often missing in elaboration step — verify that the elaborated prompt contains no German words before calling `generate_images()`.
- [ ] **Image write-to-disk:** Often missing immediate persistence — verify that each slide PNG is written to a temp directory before the next slide begins, not after all 15 complete.
- [ ] **PDF output size:** Often uncompressed — verify that PNG images are JPEG-converted or compressed before PDF embedding; a 15-slide 4K uncompressed PDF should not exceed 100 MB.
- [ ] **Rate limit handling:** Often missing exponential backoff — verify that 429 errors are retried with delay, not raised immediately to the user.
- [ ] **Aspect ratio for A4 brochure:** Often missed — verify that the A4 design system uses `aspect_ratio="3:4"` (not "16:9") and that the output path naming reflects the format.
- [ ] **Design system loading:** Often hardcoded in tests — verify that design system XML files are loaded from the `profiles/` or a dedicated `design_systems/` directory, not embedded as string literals.
- [ ] **Partial output cleanup:** Often missing — verify that temp files from a failed run are cleaned up, not left in a broken state in the output directory.
- [ ] **SynthID watermark disclosure:** Imagen embeds a SynthID watermark in all generated images — verify the user documentation mentions this; investor decks may require disclosure.

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong SDK installed (`google-generativeai`) | LOW | `pip uninstall google-generativeai && pip install google-genai`; update imports |
| All slides failed content filter | MEDIUM | Enable `include_rai_reason=True`, identify triggering content; rewrite elaboration prompts to use abstract visual descriptions instead of literal business content |
| Memory crash mid-deck generation | LOW | Slides written to disk before crash are recoverable; add `--resume` flag or re-run with `--slides N-15` range |
| PDF is 300+ MB (uncompressed 4K PNGs) | LOW | Re-run PDF assembly with JPEG compression at 85% quality; typical reduction is 5-10x |
| German text garbled in generated images | HIGH | Shift strategy: move all slide text to a post-processing overlay step (Pillow text rendering with Inter font) rather than asking Imagen to render text; this is the production-grade approach anyway |
| Daily Imagen quota exhausted | HIGH | Wait 24 hours (free tier); upgrade to pay-as-you-go; implement `--slides` range flag so quota can be distributed across sessions |
| Elaborated prompts consistently ignore design system layout | MEDIUM | Switch elaboration from Gemini to a structured Python template builder that produces deterministic prompt segments; use Gemini only for creative description of content, not for layout specification |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Wrong SDK (`google-generativeai` vs `google-genai`) | Phase 1: Dependency Setup | `pip show google-genai` shows installed; `from google import genai` imports cleanly |
| English-only Imagen prompts | Phase 1: Design Engine Foundation | Unit test with German slide content verifies elaborated prompt contains no German words |
| No validation firewall between elaboration and generation | Phase 1: Design Engine Foundation | Integration test with >480-token prompt verifies truncation occurs before `generate_images()` call |
| Content filter silent empty response | Phase 2: Imagen Integration | Unit test mocking `response.generated_images = []` verifies graceful error, not `IndexError` |
| No per-slide error isolation | Phase 2: Imagen Integration | Test that injecting an exception on slide 7 still produces slides 1-6 |
| 4K PNG memory accumulation | Phase 2: Imagen Integration | Peak RSS memory test across 15-slide mock generation stays under 500 MB |
| GEMINI_API_KEY missing error | Phase 1: Design Engine Foundation | Integration test with no `GEMINI_API_KEY` verifies friendly error message, exit code 1 |
| Uncompressed PDF size | Phase 3: PDF/ZIP Export | Assert PDF output for 15-slide 4K deck is under 100 MB |
| No progress reporting | Phase 2: Imagen Integration | Manual smoke test: 15-slide run shows per-slide status updates |
| Rate limit / 429 handling | Phase 2: Imagen Integration | Unit test mocking 429 `ClientError` verifies retry with backoff, not immediate failure |
| A4 aspect ratio mismatch | Phase 2 or Phase 3 | Assert A4 brochure design system uses `aspect_ratio="3:4"` in GenerateImagesConfig |
| Sensitive data in image prompts | Phase 1: Design Engine Foundation | Code review of elaboration prompt confirms metrics use abstract descriptions |

---

## Sources

- [Google Imagen API — Configure Aspect Ratio](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/configure-aspect-ratio)
- [Google Imagen Responsible AI Guidelines](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/responsible-ai-imagen)
- [Gemini API — Generate Images with Imagen](https://ai.google.dev/gemini-api/docs/imagen)
- [Google AI Studio Rate Limits — Imagen free tier limits](https://www.aifreeapi.com/en/posts/google-ai-studio-image-generation-limits)
- [Imagen API Rate Limit 429 despite unused quota](https://discuss.google.dev/t/quota-limit-with-imagen-error-code-429-despite-unused-quota/181091)
- [google-genai Python SDK — Official GitHub](https://github.com/googleapis/python-genai)
- [google-generativeai — Deprecated, EOL November 30 2025](https://github.com/google-gemini/deprecated-generative-ai-python)
- [Vertex AI — Set text prompt language (German support is Vertex-only)](https://cloud.google.com/vertex-ai/generative-ai/docs/image/set-text-prompt-language)
- [python-genai Issue #967 — imagen-3.0-fast model not found for API version v1beta](https://github.com/googleapis/python-genai/issues/967)
- [Pillow memory leak issues #3610, #5797, #6448](https://github.com/python-pillow/Pillow/issues/3610)
- [Avoiding Cascading Failure in LLM Prompt Chains](https://dev.to/experilearning/avoiding-cascading-failure-in-llm-prompt-chains-9bf)
- [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [AI image generators and non-Latin text rendering failure (Medium)](https://medium.com/@markus_brinsa/why-ai-fails-with-text-inside-images-and-how-it-could-change-b0ed18cd5a18)
- [Gemini API — Troubleshooting Guide](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [ReportLab memory issues with image-heavy PDFs](https://reportlab-users.reportlab.narkive.com/fhNk29ma/writing-smaller-image-only-pdfs)
- [Python zipfile — streaming limitations](https://news.ycombinator.com/item?id=23198233)
- [Imagen 4 Preview API Reference — aspect ratios, output sizes](https://docs.aimlapi.com/api-references/image-models/google/imagen-4-preview)

---
*Pitfalls research for: Adding Gemini/Imagen visual generation to pitchdeck Python CLI*
*Researched: 2026-02-26*
