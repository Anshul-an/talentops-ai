from app.parser import heuristic_parse


SAMPLE = """
Ananya Rao
Current location: Bengaluru
Preferred location: Bengaluru / Hyderabad
ananya.rao.demo@example.com
+91 98450 11223
https://linkedin.com/in/ananya-rao-demo
Total experience: 6.5 years
Current CTC: 24.0 LPA
Expected CTC: 32.0 LPA
Notice period: 30 days
Current company: Meru Labs
Skills: Python, FastAPI, Pydantic, PostgreSQL, Claude API, pytest
Education: B.E. Computer Science
Previous employers: Nimbus Retail
"""


def test_heuristic_extracts_core_fields():
    parsed = heuristic_parse(SAMPLE)
    assert parsed["email"] == "ananya.rao.demo@example.com"
    assert parsed["phone"].replace(" ", "").endswith("9845011223") or "98450" in parsed["phone"]
    assert parsed["total_experience_years"] == 6.5
    assert parsed["current_ctc"] == 24.0
    assert parsed["expected_ctc"] == 32.0
    assert parsed["notice_period_days"] == 30
    assert parsed["current_company"] == "Meru Labs"
    assert "Python" in (parsed["skills"] or [])
    assert parsed["full_name"]
    for key in [
        "full_name",
        "current_location",
        "preferred_location",
        "email",
        "phone",
        "linkedin_url",
        "total_experience_years",
        "current_ctc",
        "expected_ctc",
        "notice_period_days",
        "current_company",
        "skills",
        "education",
    ]:
        assert key in parsed


def test_messy_txt_skips_field_labels_for_name():
    raw = """sana qureshi resume!!!!
noida  sana.q.demo@example.com  9876543210
Current location: Noida
Sana Qureshi
Total experience: 2 years
Skills: React, CSS, HTML
"""
    parsed = heuristic_parse(raw)
    assert "location" not in (parsed["full_name"] or "").lower()
    assert parsed["email"] == "sana.q.demo@example.com"
