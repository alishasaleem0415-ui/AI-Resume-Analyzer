def calculate_ats_score(resume_text, job_keywords):
    """
    Compare resume text against job keywords.
    Returns: score (int), matched (list), missing (list)
    """
    resume_lower = resume_text.lower()
    matched, missing = [], []

    for keyword in job_keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
        if keyword.lower() in resume_lower:
            matched.append(keyword)
        else:
            missing.append(keyword)

    if not job_keywords:
        return 0, [], []

    score = int((len(matched) / len(job_keywords)) * 100)
    return score, matched, missing
