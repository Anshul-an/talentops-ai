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
