import re

from app.services.text_cleanup import normalize_extracted_text


def clean_context_text(text: str) -> str:
    cleaned_text = normalize_extracted_text(text).replace("\n", " ")

    cleaned_text = re.sub(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*-\s*", r"\1 is ", cleaned_text, count=1)
    cleaned_text = cleaned_text.replace(" | ", ", ")
    cleaned_text = re.sub(r"\s*,\s*", ", ", cleaned_text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)

    return cleaned_text.strip()


def split_into_sentences(text: str) -> list[str]:
    normalized_text = clean_context_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", normalized_text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def extract_keywords(text: str) -> set[str]:
    stop_words = {
        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "is",
        "are",
        "the",
        "his",
        "her",
        "their",
        "about",
        "tell",
        "me",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "a",
        "an",
    }

    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {
        word
        for word in words
        if len(word) >= 3 and word not in stop_words
    }


def normalize_sentence(sentence: str) -> str:
    cleaned_sentence = " ".join(sentence.split()).strip(" -")

    if not cleaned_sentence:
        return ""

    cleaned_sentence = re.sub(r"\s+([,.;:!?])", r"\1", cleaned_sentence)

    if cleaned_sentence and cleaned_sentence[0].islower():
        cleaned_sentence = cleaned_sentence[0].upper() + cleaned_sentence[1:]

    if cleaned_sentence[-1] not in ".!?":
        cleaned_sentence = f"{cleaned_sentence}."

    return cleaned_sentence


def choose_indefinite_article(phrase: str) -> str:
    first_character = phrase[:1].lower()

    if first_character in {"a", "e", "i", "o", "u"}:
        return "an"

    return "a"


def extract_subject_from_question(question: str) -> str | None:
    match = re.search(
        r"\b(?:what|who)\s+is\s+([a-zA-Z0-9][a-zA-Z0-9 !&'._-]*)\??$",
        question.strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    subject = " ".join(match.group(1).split()).strip(" ?.")

    return subject or None


def build_definition_style_answer(question: str, candidate_sentences: list[str]) -> str | None:
    subject = extract_subject_from_question(question)

    if not subject:
        return None

    for sentence in candidate_sentences:
        normalized_sentence = normalize_sentence(sentence)

        if not normalized_sentence:
            continue

        sentence_without_period = normalized_sentence.rstrip(".!?")
        lowered_sentence = sentence_without_period.lower()
        lowered_subject = subject.lower()

        if lowered_subject in lowered_sentence and " is " in lowered_sentence:
            return normalized_sentence

        primary_clause = sentence_without_period.split(",")[0].strip()

        if not primary_clause:
            continue

        if " is " in primary_clause.lower():
            return normalize_sentence(primary_clause)

        words = primary_clause.split()

        if len(words) >= 3 and words[-1][:1].isupper():
            descriptor = " ".join(words[:-1]).strip().lower()
            location = words[-1]

            if descriptor:
                article = choose_indefinite_article(descriptor)
                return f"{subject} is {article} {descriptor} based in {location}."

        article = choose_indefinite_article(primary_clause.lower())
        return f"{subject} is {article} {primary_clause.lower()}."

    return None


def is_informative_sentence(sentence: str) -> bool:
    lowered_sentence = sentence.lower()
    blocked_fragments = (
        "queryselector",
        "addEventlistener",
        "modulepreload",
        "__vite__",
        "function(",
        "object.keys(",
        "for(var",
        "const ",
        "return ",
    )

    if any(fragment.lower() in lowered_sentence for fragment in blocked_fragments):
        return False

    return len(sentence.split()) >= 5


def dedupe_chunks(chunks: list[str]) -> list[str]:
    deduped_chunks: list[str] = []
    seen_chunks: set[str] = set()

    for chunk in chunks:
        cleaned_chunk = clean_context_text(chunk)
        dedupe_key = cleaned_chunk.lower()

        if not cleaned_chunk or dedupe_key in seen_chunks:
            continue

        seen_chunks.add(dedupe_key)
        deduped_chunks.append(cleaned_chunk)

    return deduped_chunks


def build_natural_fallback_answer(sentences: list[str], max_sentences: int = 3) -> str:
    normalized_sentences: list[str] = []
    seen_sentences: set[str] = set()

    for sentence in sentences:
        normalized_sentence = normalize_sentence(sentence)

        if not normalized_sentence:
            continue

        dedupe_key = normalized_sentence.lower()

        if dedupe_key in seen_sentences:
            continue

        if not is_informative_sentence(normalized_sentence):
            continue

        seen_sentences.add(dedupe_key)
        normalized_sentences.append(normalized_sentence)

        if len(normalized_sentences) >= max_sentences:
            break

    if not normalized_sentences:
        return (
            "I could not find a clear answer to that in the available website content. "
            "Please leave your contact details and the team will get back to you."
        )

    return " ".join(normalized_sentences)


def build_extractive_answer(
    question: str,
    context_chunks: list[str],
    max_sentences: int = 3,
) -> str:
    context_chunks = dedupe_chunks(context_chunks)
    question_keywords = extract_keywords(question)

    if not context_chunks:
        return (
            "I could not find enough information to answer that. "
            "Please leave your contact details and the team will get back to you."
        )

    all_sentences: list[str] = []

    for chunk in context_chunks:
        all_sentences.extend(split_into_sentences(chunk))

    scored_sentences: list[tuple[int, str]] = []

    for sentence in all_sentences:
        sentence_keywords = extract_keywords(sentence)
        score = len(question_keywords & sentence_keywords)

        if score > 0:
            scored_sentences.append((score, sentence))

    if not scored_sentences:
        return (
            "I could not find a clear answer to that in the available website content. "
            "Please leave your contact details and the team will get back to you."
        )

    scored_sentences.sort(key=lambda item: item[0], reverse=True)

    selected_sentences = [
        sentence
        for _, sentence in scored_sentences[:max_sentences]
    ]

    definition_style_answer = build_definition_style_answer(
        question=question,
        candidate_sentences=selected_sentences,
    )

    if definition_style_answer:
        return definition_style_answer

    return build_natural_fallback_answer(
        selected_sentences,
        max_sentences=max_sentences,
    )


def answer_support_score(answer: str, context_chunks: list[str]) -> int:
    answer_keywords = extract_keywords(answer)

    if not answer_keywords:
        return 0

    best_score = 0

    for chunk in context_chunks:
        chunk_keywords = extract_keywords(chunk)
        best_score = max(best_score, len(answer_keywords & chunk_keywords))

    return best_score
