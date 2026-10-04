# RarityBarter

**RarityBarter** is a community-driven peer-to-peer platform designed for trading, discovering, and preserving rare, niche, and high-value resources—such as historic urban heritage photos, family secret recipes, daily life hacks, and oral histories or archival documents.

By utilizing a tokenized credit system, metadata-based quality scoring, and AI-powered natural language discovery, RarityBarter incentivizes users to share rich primary-source materials while maintaining trust through community verification and feedback.

---

## Features

* **Credit & Valuation System:**
  * **Dynamic Credit Scoring:** Estimates credit rewards based on content detail, word count, temporal markers (years/dates), provenance keywords, and attached files.
  * **Credit Economy:** Users earn credits by submitting contributions and spend credits to unlock community resources.
  * **Transaction History & Notifications:** Tracks credit earnings, spendings, and live notifications in real time.

* **Search & AI Assistance:**
  * **Local Term Search:** Search contributions using keyword stemming, normalized term matching, and field-weighted relevance scoring (title, type, description, and content).
  * **Prioritized Categories:** Auto-detects query intent for categories such as *Old Buildings & Urban Heritage*, *Family Secret Food Recipes*, and *Daily Life Hacks*.
  * **AI Conversational Search:** Integrates with OpenRouter or OpenAI APIs to answer queries conversationally, cite specific resource IDs (`[#ID]`), and respect user resource unlock permissions.
  * **Fallback Search:** Provides structured local summaries if no AI API key is configured or available.

* **Moderation & Community Feedback:**
  * **Like & Dislike:** Reward contributors with reputation bonuses or signal poor quality.
  * **Reporting System:** Flags potentially false or deceptive data, updates status to *Reported/Unverified*, and applies credit and trust penalties.

* **Resource Unlocking & Downloads:**
  * **Content Unlocking:** Deducts credits to grant user access to protected resource content.
  * **Dynamic Payloads:** Downloads physical/attached files directly or dynamically generates formatted `.txt` files from resource metadata and unlocked content.

---

## File Structure

```
raritybarter/
├── app.py              # Main Streamlit UI and application interface
└── helpers.py          # Core business logic: credits, search, AI, actions, and downloads

```

---

## Project Architecture (`helpers.py`)

### 1. Credits & Scoring

* `record_credit_change(description, amount)`: Logs credit usage/earnings, adds a user notification, and displays a Streamlit toast.
* `calculate_credits(detail_score)`: Calculates total credits earned from a quality score.
* `estimate_value_score(...)`: Evaluates word length, temporal indicators, provenance terminology, and attached files to generate a score (1–10) and assessment message.
* `estimate_contribution(draft)`: Applies valuation scoring to draft submissions.

### 2. Search & AI Integration

* `prioritized_download_categories(query)`: Maps specific search terms to relevant contribution categories.
* `search_contributions(query, contributions)`: Filters stop words, normalizes stems, and ranks matching contributions.
* `get_ai_models()`, `get_ai_api_key()`, `get_ai_api_base_url()`: Resolves API credentials and model parameters for OpenRouter/OpenAI endpoints.
* `generate_ai_response(...)`: Sends conversational prompts with resource context to the AI API, or defaults to `generate_local_search_response()` if no key is provided.

### 3. Moderation & File Handling

* `trigger_like(item_id)` / `trigger_dislike(item_id)`: Manages user likes, dislikes, and community reputation adjustments.
* `trigger_report(item_id, report_reason)`: Flags items as unverified and penalizes the contributor.
* `unlock_resource(item_id, cost)`: Deducts user credits and grants access to resource content.
* `get_download_payload(item)`: Prepares direct binary downloads or formats fallback plain text files.

---

## Getting Started

### Prerequisites

* Python 3.9+
* Streamlit

### Environment Variables / Secrets Configuration

Configure AI integration using environment variables or Streamlit secrets (`.streamlit/secrets.toml`):

* `OPENROUTER_API_KEY` or `OPENAI_API_KEY` or `RARITYBARTER_API_KEY`
* `RARITYBARTER_MODELS` *(Optional comma-separated list of models)*
* `RARITYBARTER_API_BASE_URL` *(Optional custom API base URL)*
* `OPENROUTER_SITE_URL` *(Optional referer URL for OpenRouter)*

### Running the App

```
streamlit run app.py
```