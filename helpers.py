# Credits and Scores

def record_credit_change(description, amount):
    timestamp = datetime.datetime.now().strftime("%b %d, %H:%M")
    st.session_state.credit_history.insert(0, {
        "description": description,
        "amount": amount,
        "time": timestamp,
    })
    action = "earned" if amount > 0 else "used"
    st.session_state.notifications.insert(0, {
        "icon": "🪙",
        "message": f"{abs(amount)} credits {action} {description}.",
        "time": timestamp,
    })
    st.toast(f"{abs(amount)} credits {action} {description}.", icon="🪙", duration=3)

def calculate_credits(detail_score):
    base_value = 22
    detail_factor = detail_score * 2.5
    return int(base_value + detail_factor)

def estimate_value_score(resource_type, title, description, additional_details, file_names):
    evidence = " ".join([resource_type, title, description, *additional_details, *file_names]).lower()
    unique_words = set(re.findall(r"\b[a-z0-9]{3,}\b", evidence))
    score = 2

    if len(unique_words) >= 10:
        score += 1
    if len(unique_words) >= 25:
        score += 1
    if re.search(r"\b(?:18|19|20)\d{2}\b", evidence):
        score += 2
    if any(term in evidence for term in ("provenance", "oral history", "archive", "firsthand", "manuscript", "unpublished")):
        score += 1
    if any(term in evidence for term in ("important", "historical", "documented", "community", "field notes", "personal collection")):
        score += 1
    if file_names:
        score += 1
    if len(file_names) >= 3:
        score += 1

    score = min(score, 10)
    if score >= 8:
        assessment = "Strong specificity and supporting evidence"
    elif score >= 5:
        assessment = "Some useful context; more provenance may improve the estimate"
    else:
        assessment = "Limited supporting detail; add context or files for a stronger estimate"
    return score, assessment

def estimate_contribution(draft):
    value_score, assessment = estimate_value_score(
        draft["type"],
        draft["title"],
        draft["description"],
        draft["additional_details"],
        draft["file_names"]
    )
    estimated_credits = calculate_credits(value_score)
    draft["value_score"] = value_score
    draft["assessment"] = assessment
    draft["estimated_credits"] = estimated_credits
    return value_score, assessment, estimated_credits

# Search and AI

def prioritized_download_categories(query):
    normalized_query = re.sub(r"[^a-z0-9]+", " ", query.lower()).strip()
    category_search_terms = {
        "Old Buildings & Urban Heritage": (
            "building", "buildings", "heritage", "urban", "architecture",
            "architectural", "tong lau", "market", "markets", "streetscape",
            "historic", "historical",
        ),
        "Family Secret Food Recipes": (
            "recipe", "recipes", "cook", "cooking", "food", "kitchen",
        ),
        "Daily Life Hacks": (
            "hack", "hacks", "life hack", "daily life", "household tip",
            "household tips", "everyday trick", "everyday tricks",
        ),
    }
    return {
        category
        for category, search_terms in category_search_terms.items()
        if any(
            re.search(rf"\b{re.escape(term)}\b", normalized_query)
            for term in search_terms
        )
    }

def search_contributions(query, contributions):
    ignored_terms = {
        "the", "and", "for", "with", "from", "that", "this", "these", "those",
        "find", "show", "looking", "want", "need", "please", "anything", "about",
        "search", "resource", "resources", "data", "dataset", "datasets"
    }

    def normalized_terms(text):
        words = re.findall(r"\b[a-z0-9]+\b", text.lower())
        terms = {word for word in words if len(word) > 2 and word not in ignored_terms}
        for word in tuple(terms):
            if word.endswith("ies") and len(word) > 4:
                terms.add(word[:-3] + "y")
            elif word.endswith("s") and not word.endswith("ss") and len(word) > 4:
                terms.add(word[:-1])
        return terms

    query_terms = normalized_terms(query)
    if not query_terms:
        return []

    ranked_results = []
    for index, item in enumerate(contributions):
        title_terms = normalized_terms(item["title"])
        type_terms = normalized_terms(item["type"])
        description_terms = normalized_terms(item["description"])
        content_terms = normalized_terms(item.get("content", ""))
        score = sum(
            (4 if term in title_terms else 0)
            + (3 if term in type_terms else 0)
            + (2 if term in description_terms else 0)
            + (1 if term in content_terms else 0)
            for term in query_terms
        )
        if score:
            ranked_results.append((score, index, item))

    ranked_results.sort(key=lambda result: (-result[0], result[1]))
    return [item for _, _, item in ranked_results]

def get_ai_setting(name, default=""):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def get_ai_models():
    configured_models = get_ai_setting("RARITYBARTER_MODELS")
    if configured_models:
        model_ids = [model.strip() for model in configured_models.split(",") if model.strip()]
        return {
            next((label for label, model_id in OPENROUTER_MODEL_OPTIONS.items() if model_id == model), model): model
            for model in model_ids
        }
    if "openrouter.ai" in get_ai_api_base_url().lower():
        return OPENROUTER_MODEL_OPTIONS
    return AI_MODEL_OPTIONS

def get_ai_api_key():
    return (
        get_ai_setting("OPENROUTER_API_KEY")
        or get_ai_setting("OPENAI_API_KEY")
        or get_ai_setting("RARITYBARTER_API_KEY")
    )

def get_ai_api_base_url():
    configured_base_url = get_ai_setting("RARITYBARTER_API_BASE_URL")
    if configured_base_url:
        return configured_base_url.rstrip("/")
    if get_ai_setting("OPENROUTER_API_KEY"):
        return "https://openrouter.ai/api/v1"
    return "https://api.openai.com/v1"

def build_resource_context(resources, user_name):
    context = []
    for item in resources[:6]:
        resource = {
            "id": item["id"],
            "title": item["title"],
            "type": item["type"],
            "description": item["description"][:1200],
            "status": item["status"],
            "contributor": item["contributor_id"],
        }
        if user_name in item.get("unlocked_by", []):
            resource["unlocked_content"] = item.get("content", "")[:3000]
        context.append(resource)
    return context

def get_cited_resource_ids(response_text, contributions):
    resources_by_id = {item["id"]: item for item in contributions}
    cited_ids = re.findall(r"\[#(\d+)\]", response_text)
    return list(dict.fromkeys(
        int(resource_id) for resource_id in cited_ids
        if int(resource_id) in resources_by_id
    ))

def generate_local_search_response(query, resources):
    if not resources:
        if re.search(r"\b(hi|hello|hey)\b", query.lower()):
            return (
                "Hi! I can help you explore the resources shared on RarityBarter. "
                "What topic, place, time period, or format are you looking for?"
            )
        return (
            f"I couldn't find a resource matching \"{query}\" in the current collection. "
            "Try another topic, place, time period, or format."
        )

    if len(resources) == 1:
        opening = "Sure, here's the closest match."
    else:
        opening = f"I found {len(resources)} resources that may fit. Here are the closest matches:"

    summaries = [
        f"- [#{item['id']}] **{item['title']}** ({item['type']}, {item['status']}): "
        f"{item['description']}"
        for item in resources[:4]
    ]
    closing = "Would you like to narrow these down by topic, place, period, or resource type?"
    return "\n\n".join([opening, *summaries, closing])

def generate_ai_response(query, model, previous_messages, resources, user_name):
    api_key = get_ai_api_key()
    resource_context = build_resource_context(resources, user_name)
    if not api_key:
        return generate_local_search_response(query, resources)

    system_message = (
        "You are RarityBarter's friendly, natural conversational assistant. Respond to greetings and "
        "general questions conversationally; do not force every reply to be a search result. For a "
        "resource-related question, recommend relevant records below and cite each one using its "
        "exact ID format [#ID] and exact title. Only cite records included below, and only when "
        "they are relevant; never invent resource details. If no record fits, say that clearly and "
        "continue helping generally or ask a useful follow-up question. Unlocked content is included "
        "only when the current user has access to it.\n\n"
        f"Resource records: {json.dumps(resource_context, ensure_ascii=False)}"
    )
    messages = [{"role": "system", "content": system_message}]
    for message in previous_messages[-8:]:
        role = "assistant" if message["sender"] == "AI" else "user"
        messages.append({"role": role, "content": message["text"]})
    messages.append({"role": "user", "content": query})

    base_url = get_ai_api_base_url()
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if "openrouter.ai" in base_url.lower():
        request_headers["X-Title"] = "RarityBarter"
        site_url = get_ai_setting("OPENROUTER_SITE_URL")
        if site_url:
            request_headers["HTTP-Referer"] = site_url
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps({"model": model, "messages": messages}).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        return f"The AI service returned HTTP {error.code}: {detail or error.reason}"
    except (urllib.error.URLError, TimeoutError) as error:
        return f"Could not connect to the AI service: {error}"
    except (json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError):
        return "The AI service returned an unexpected response. Check the configured endpoint and model."

# Actions and Downloads

def get_user_action(item_id):
    return st.session_state.user_actions.setdefault(item_id, {
        "liked": False,
        "disliked": False,
        "reported": False,
        "report_reason": ""
    })

def trigger_like(item_id):
    action = get_user_action(item_id)
    for item in st.session_state.contributions:
        if item["id"] == item_id:
            if action["liked"]:
                item["likes"] = max(0, item["likes"] - 1)
                action["liked"] = False
                st.toast("Like removed.", icon="❤️")
            else:
                if action["disliked"]:
                    item["dislikes"] = max(0, item["dislikes"] - 1)
                    action["disliked"] = False
                item["likes"] += 1
                action["liked"] = True
                st.toast("Liked resource! Contributor received reputation bonus.", icon="❤️")

def trigger_dislike(item_id):
    action = get_user_action(item_id)
    for item in st.session_state.contributions:
        if item["id"] == item_id:
            if action["disliked"]:
                item["dislikes"] = max(0, item["dislikes"] - 1)
                action["disliked"] = False
                st.toast("Dislike removed.", icon="👎")
            else:
                if action["liked"]:
                    item["likes"] = max(0, item["likes"] - 1)
                    action["liked"] = False
                item["dislikes"] += 1
                action["disliked"] = True
                st.toast("Feedback recorded.", icon="👎")

def trigger_report(item_id, report_reason):
    action = get_user_action(item_id)
    if action["reported"]:
        return
    for item in st.session_state.contributions:
        if item["id"] == item_id:
            item["status"] = "Reported/Unverified"
            item["dislikes"] += 5
            action["reported"] = True
            action["report_reason"] = report_reason
            st.toast("Data reported as potentially false. Contributor credits & trust penalized.", icon="🚩")

def get_download_payload(item):
    download_file = item.get("download_file")
    if download_file:
        file_path = Path(__file__).resolve().parent / download_file
        mime_type, _ = mimetypes.guess_type(file_path.name)
        if mime_type is None:
            raise ValueError(f"Cannot determine the media type for {file_path.name}.")
        return {
            "file_name": file_path.name,
            "data": file_path.read_bytes(),
            "mime": mime_type
        }

    safe_title = re.sub(r"[^a-z0-9]+", "_", item["title"].lower()).strip("_") or "resource"
    content = "\n".join([
        item["title"],
        f"Type: {item['type']}",
        f"Description: {item['description']}",
        "",
        item["content"]
    ])
    return {
        "file_name": f"{safe_title}_resource.txt",
        "data": content.encode("utf-8"),
        "mime": "text/plain"
    }

def unlock_resource(item_id, cost):
    if st.session_state.user["credits"] >= cost:
        st.session_state.user["credits"] -= cost
        for item in st.session_state.contributions:
            if item["id"] == item_id:
                item["unlocked_by"].append(st.session_state.user["name"])
                record_credit_change(f"to unlock {item['title']}", -cost)
        st.success(f"Unlocked! {cost} credits deducted.")
        st.rerun()
    else:
        st.error("Insufficient credits balance! Contribute data to earn more.")