"""Generate fictional sample resumes (DOCX + PDF) for the TalentOps demo."""
from pathlib import Path

from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sample_resumes"
OUT.mkdir(parents=True, exist_ok=True)

RESUMES = [
    {
        "file": "ananya_rao_backend.docx",
        "kind": "docx",
        "body": [
            "ANANYA RAO",
            "Bengaluru  |  ananya.rao.demo@example.com  |  +91 98450 11223  |  https://linkedin.com/in/ananya-rao-demo",
            "Current location: Bengaluru",
            "Preferred location: Bengaluru / Hyderabad",
            "Total experience: 6.5 years",
            "Current CTC: 24.0 LPA   Expected CTC: 32.0 LPA",
            "Notice period: 30 days",
            "Current company: Meru Labs",
            "Summary: Backend engineer shipping production FastAPI services, LLM extraction jobs, and Postgres data models.",
            "Skills: Python, FastAPI, Pydantic, PostgreSQL, Redis, Claude API, pytest, Docker, AWS",
            "Experience:",
            "Meru Labs — Senior Software Engineer (2023–present): Built document ingest APIs, prompt pipelines, webhook workers.",
            "Nimbus Retail — Software Engineer (2020–2023): Order service in Python, REST integrations.",
            "Previous employers: Nimbus Retail, Campus intern at PixelWorks",
            "Education: B.E. Computer Science, RV College of Engineering",
            "Certifications: AWS Developer Associate",
        ],
    },
    {
        "file": "rohan_mehta_fullstack.docx",
        "kind": "docx",
        "body": [
            "Rohan Mehta",
            "Mumbai |  rohan.mehta.demo@example.com | +91 98200 33445 | https://linkedin.com/in/rohan-mehta-demo",
            "Current location: Mumbai",
            "Preferred location: Mumbai / Remote",
            "Total experience: 4 years",
            "Current CTC: 16.5 LPA   Expected CTC: 22 LPA",
            "Notice period: 60 days",
            "Current company: Harbor Fintech",
            "Skills: JavaScript, React, Node.js, Python, FastAPI, MongoDB, REST APIs",
            "Experience:",
            "Harbor Fintech — Full Stack Engineer (2022–present)",
            "BrightCart — Junior Developer (2021–2022)",
            "Previous employers: BrightCart",
            "Education: B.Tech IT, VJTI Mumbai",
        ],
    },
    {
        "file": "priya_nair_data.docx",
        "kind": "docx",
        "body": [
            "PRIYA NAIR",
            "Hyderabad | priya.nair.demo@example.com | +91 90000 22110",
            "Current location: Hyderabad",
            "Preferred location: Hyderabad",
            "Total experience: 5 years",
            "Current CTC: 21 LPA  Expected CTC: 28 LPA",
            "Notice period: 45 days",
            "Current company: Helix Analytics",
            "Skills: Python, pandas, scikit-learn, SQL, LLM evaluation, Airflow",
            "Experience: Helix Analytics (2021–present); Data Analyst at Indigo Insights (2019–2021)",
            "Previous employers: Indigo Insights",
            "Education: M.Sc. Statistics, University of Hyderabad",
        ],
    },
    {
        "file": "kabir_singh_recruiter.docx",
        "kind": "docx",
        "body": [
            "Kabir Singh",
            "New Delhi | kabir.singh.demo@example.com | +91 98101 77889 | https://linkedin.com/in/kabir-singh-ta",
            "Current location: New Delhi",
            "Preferred location: Delhi NCR / Mumbai",
            "Total experience: 8 years",
            "Current CTC: 18 LPA  Expected CTC: 24 LPA",
            "Notice period: 30 days",
            "Current company: Northstar Search",
            "Skills: Executive search, Naukri, LinkedIn Recruiter, CEIPAL, Boolean sourcing, stakeholder management, offer negotiation",
            "Experience:",
            "Northstar Search — Principal Recruiter, Technology (2020–present). Closed CXO and specialist mandates.",
            "HireGrid — Senior Consultant (2016–2020). High-volume tech hiring.",
            "Previous employers: HireGrid",
            "Education: MBA HR, NMIMS",
            "Certifications: LinkedIn Recruiter Professional",
        ],
    },
    {
        "file": "meera_iyer_pm.docx",
        "kind": "docx",
        "body": [
            "Meera Iyer",
            "Pune | meera.iyer.demo@example.com | +91 98810 44556",
            "Current location: Pune",
            "Preferred location: Pune / Bengaluru",
            "Total experience: 7 years",
            "Current CTC: 29 LPA  Expected CTC: 38 LPA",
            "Notice period: 90 days",
            "Current company: Lotus Commerce",
            "Skills: Product management, roadmaps, SQL, stakeholder comms, A/B testing",
            "Previous employers: Kite Mobility, FreshStart internships",
            "Education: B.Tech + MBA, IIM Kozhikode",
        ],
    },
    {
        "file": "arjun_desai_devops.docx",
        "kind": "docx",
        "body": [
            "Arjun Desai",
            "Ahmedabad | arjun.desai.demo@example.com | +91 97250 66778",
            "Current location: Ahmedabad",
            "Preferred location: Remote / Bengaluru",
            "Total experience: 3 years",
            "Current CTC: 12 LPA  Expected CTC: 18 LPA",
            "Notice period: 15 days",
            "Current company: CloudNest",
            "Skills: Docker, Kubernetes, Terraform, AWS, CI/CD, Python scripting",
            "Previous employers: Campus placement at CloudNest only",
            "Education: B.E. ICT, DA-IICT",
        ],
    },
    {
        "file": "sana_qureshi_frontend.txt",
        "kind": "txt",
        "body": [
            "sana qureshi resume!!!!",
            "noida  sana.q.demo@example.com  9876543210",
            "Current location: Noida",
            "i do react and css. 2 years experience-ish",
            "Total experience: 2 years",
            "Current CTC: 8 LPA Expected CTC: 14 LPA",
            "Notice period: 60 days",
            "Current company: PixelForge",
            "Skills: React, CSS, HTML, figma, a bit of python",
            "Education: BCA",
        ],
    },
    {
        "file": "vikram_patel_finance.docx",
        "kind": "docx",
        "body": [
            "Vikram Patel",
            "Mumbai | vikram.patel.demo@example.com | +91 99300 12121",
            "Current location: Mumbai",
            "Preferred location: Mumbai",
            "Total experience: 9 years",
            "Current CTC: 26 LPA  Expected CTC: 34 LPA",
            "Notice period: 60 days",
            "Current company: Sterling Capital",
            "Skills: FP&A, Tally, Excel, MIS, collections, GST, CredFlow-adjacent AR processes",
            "Previous employers: Grant Thornton (articles), Sterling Capital",
            "Education: CA, ICAI",
        ],
    },
    {
        "file": "lakshmi_krishnan_java.pdf",
        "kind": "pdf",
        "body": [
            "Lakshmi Krishnan",
            "Chennai | lakshmi.krishnan.demo@example.com | +91 94440 90909 | https://linkedin.com/in/lakshmi-k-demo",
            "Current location: Chennai",
            "Preferred location: Chennai / Bengaluru",
            "Total experience: 11 years",
            "Current CTC: 31 LPA  Expected CTC: 40 LPA",
            "Notice period: 90 days",
            "Current company: Southern Grid Systems",
            "Skills: Java, Spring Boot, Kafka, Microservices, Oracle, leadership",
            "Previous employers: Infosys, Southern Grid Systems",
            "Education: B.E. ECE, Anna University",
        ],
    },
    {
        "file": "neha_kapoor_ml.pdf",
        "kind": "pdf",
        "body": [
            "Neha Kapoor",
            "Gurugram | neha.kapoor.demo@example.com | +91 98119 33440",
            "Current location: Gurugram",
            "Preferred location: Gurugram / Remote",
            "Total experience: 4.5 years",
            "Current CTC: 22 LPA  Expected CTC: 30 LPA",
            "Notice period: 30 days",
            "Current company: VectorMind",
            "Skills: Python, PyTorch, LLM fine-tuning, FastAPI, RAG, Claude, embeddings, pytest",
            "Previous employers: VectorMind, research intern IIT Delhi",
            "Education: M.Tech CS, IIT Delhi",
            "Certifications: DeepLearning.AI NLP",
        ],
    },
]


def write_docx(path: Path, lines: list[str]) -> None:
    doc = Document()
    for i, line in enumerate(lines):
        p = doc.add_paragraph(line)
        run = p.runs[0]
        run.font.size = Pt(16 if i == 0 else 11)
        if i == 0:
            run.bold = True
    doc.save(str(path))


def write_pdf(path: Path, lines: list[str]) -> None:
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(lines[0], styles["Title"]))
    story.append(Spacer(1, 12))
    for line in lines[1:]:
        story.append(Paragraph(line.replace("&", "&amp;"), styles["Normal"]))
        story.append(Spacer(1, 6))
    SimpleDocTemplate(str(path), pagesize=A4).build(story)


def main() -> None:
    for item in RESUMES:
        path = OUT / item["file"]
        if item["kind"] == "docx":
            write_docx(path, item["body"])
        elif item["kind"] == "pdf":
            write_pdf(path, item["body"])
        else:
            path.write_text("\n".join(item["body"]), encoding="utf-8")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
