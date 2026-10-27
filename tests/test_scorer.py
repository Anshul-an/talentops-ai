from app.scorer import heuristic_score


JD = {
    "title": "Senior Backend Engineer",
    "jd_text": "Python FastAPI Pydantic PostgreSQL Claude LLM pytest Docker production APIs",
}


def test_threshold_tags_ai_fit():
    strong = {
        "skills": "Python, FastAPI, Pydantic, PostgreSQL, Claude API, pytest, Docker",
        "total_experience_years": 6.5,
        "previous_employers": "Nimbus Retail, Meru Labs",
    }
    result = heuristic_score(strong, JD, threshold=70)
    assert result["fitment_score"] >= 70
    assert result["status"] == "Screened - AI Fit"
    assert result["summary_bullets"].count("•") == 3


def test_low_overlap_below_threshold():
    weak = {
        "skills": "Tally, GST, Excel",
        "total_experience_years": 2,
        "previous_employers": "A, B, C, D",
    }
    result = heuristic_score(weak, JD, threshold=70)
    assert result["status"] == "Sourced - Below Threshold"
    assert result["fitment_score"] < 70


def test_scorer_clamp_upper_limit():
    from app.scorer import heuristic_score
    cand = {
        "full_name": "Overqualified Candidate",
        "skills": "python fastapi docker kubernetes aws react vue angular go rust java c++",
        "total_experience_years": 15,
        "current_location": "Bengaluru",
        "certifications": "AWS Solutions Architect, PMP, Kubernetes CKAD",
    }
    job = {"title": "Tech Lead", "jd_text": "Bengaluru python fastapi docker kubernetes aws"}
    res = heuristic_score(cand, job, 70.0)
    assert 0.0 <= res["fitment_score"] <= 100.0


def test_scorer_none_skills():
    from app.scorer import heuristic_score
    cand = {"full_name": "No Skills", "skills": None, "total_experience_years": None}
    job = {"title": "Dev", "jd_text": "Python engineer"}
    res = heuristic_score(cand, job, 70.0)
    assert isinstance(res["fitment_score"], float)


def test_location_match_bonus():
    from app.scorer import heuristic_score
    cand_match = {"full_name": "A", "skills": "python", "current_location": "Bengaluru"}
    cand_no_match = {"full_name": "B", "skills": "python", "current_location": "Chennai"}
    job = {"title": "Dev", "jd_text": "Python engineer based in Bengaluru"}
    score_match = heuristic_score(cand_match, job, 70.0)["fitment_score"]
    score_no_match = heuristic_score(cand_no_match, job, 70.0)["fitment_score"]
    assert score_match >= score_no_match


def test_employment_gap_penalty():
    from app.scorer import heuristic_score
    cand_gap = {"full_name": "A", "skills": "python", "career_gap_months": 12}
    cand_no_gap = {"full_name": "B", "skills": "python", "career_gap_months": 0}
    job = {"title": "Dev", "jd_text": "Python engineer"}
    score_gap = heuristic_score(cand_gap, job, 70.0)["fitment_score"]
    score_no_gap = heuristic_score(cand_no_gap, job, 70.0)["fitment_score"]
    assert score_no_gap >= score_gap
