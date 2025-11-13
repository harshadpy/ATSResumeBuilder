import re
from utils.parser import parse_resume


def test_parse_basic_fields():
    text = (
        "John Doe\nEmail: john@example.com\nPhone: +1 234 567 8900\n"
        "LinkedIn: https://linkedin.com/in/johndoe\n"
        "GitHub: https://github.com/johndoe\n"
        "Skills: Python, Machine Learning, SQL, Pandas, Numpy, Docker\n"
        "Education\nB.S. in Computer Science, ABC University, 2018 - 2022\n"
        "Experience\nSoftware Engineer\nAcme Corp\nJan 2023 - Present\n- Built ML pipelines\n- Improved ETL performance\n"
    )
    data = parse_resume(text)
    assert data["personal_info"]["name"] != "Not found"
    assert re.match(r".+@.+\\..+", data["personal_info"]["email"]) is not None
    assert len(data["skills"]) >= 5
    assert data["education"]
    assert data["experience"]

