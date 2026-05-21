import os
import re
import uuid

from fastapi import FastAPI, Request, Form
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    JSONResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from generator import create_pdf
from ai_engine import generate_all


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# ---------------- ROUTES ---------------- #

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):

    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )


@app.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):

    return templates.TemplateResponse(
        "app.html",
        {"request": request}
    )


# ---------------- HELPERS ---------------- #

def clean_filename(text: str):

    if not text:
        return "document"

    text = str(text).strip().lower()

    text = re.sub(r"[^a-z0-9 ]", "", text)

    cleaned = "_".join(text.split())

    return cleaned[:40] or "document"


def fix_title(title: str, prompt: str):

    if not title:
        return "document"

    title = str(title).strip()

    if title.lower() in ["empty", "document", "title"]:

        if "resume" in prompt.lower():
            return "resume"

        return "document"

    return title[:80]


def extract_body(content: str):

    match = re.search(
        r"\\begin\{document\}(.*?)\\end\{document\}",
        content,
        re.DOTALL
    )

    if match:
        return match.group(1)

    return content


def remove_forbidden_commands(content: str):

    patterns = [

        r"\\documentclass.*?\}",
        r"\\usepackage.*?\}",
        r"\\geometry.*?\}",
        r"\\begin\{document\}",
        r"\\end\{document\}",
        r"\\maketitle",
        r"\\title\{.*?\}",
        r"\\author\{.*?\}",
        r"\\date\{.*?\}",
    ]

    for pattern in patterns:

        content = re.sub(
            pattern,
            "",
            content,
            flags=re.DOTALL
        )

    return content


def fix_common_latex(content: str):

    content = re.sub(
        r"(?m)^item ",
        r"\\item ",
        content
    )

    lines = []

    for line in content.splitlines():

        if "\\section*" in line and not line.strip().endswith("}"):
            line += "}"

        lines.append(line)

    content = "\n".join(lines)

    open_braces = content.count("{")
    close_braces = content.count("}")

    if open_braces > close_braces:
        content += "}" * (open_braces - close_braces)

    return content


def auto_close_environments(content: str):

    environments = [
        "itemize",
        "enumerate",
        "align",
        "equation"
    ]

    for env in environments:

        begins = len(
            re.findall(
                rf"\\begin\{{{env}\}}",
                content
            )
        )

        ends = len(
            re.findall(
                rf"\\end\{{{env}\}}",
                content
            )
        )

        while ends < begins:

            content += f"\n\\end{{{env}}}"

            ends += 1

    return content


def clean_latex(content: str):

    if not content:
        return ""

    content = str(content)

    garbage_markers = [
        "This is pdfTeX",
        "LaTeX Error",
        "Emergency stop",
        "Transcript written on"
    ]

    for marker in garbage_markers:

        if marker in content:
            content = content.split(marker)[0]

    content = extract_body(content)

    content = remove_forbidden_commands(content)

    content = fix_common_latex(content)

    content = re.sub(
        r"\\\[[^\]]*$",
        "",
        content,
        flags=re.DOTALL
    )

    content = re.sub(
        r"\\[a-zA-Z]*$",
        "",
        content
    )

    while content.count("{") > content.count("}"):
        content = content[:-1]

    content = auto_close_environments(content)

    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip()


# ---------------- PDF GENERATION ---------------- #

@app.post("/generate-ui")
async def generate_ui(
    content: str = Form(...),
    template_type: str = Form("article"),
):

    title, author, latex_content, error = generate_all(
        content,
        template_type
    )

    if error:

        return JSONResponse(
            {
                "ok": False,
                "error": error
            },
            status_code=200
        )

    if not latex_content:

        return JSONResponse(
            {
                "ok": False,
                "error": "Empty AI content."
            },
            status_code=200
        )

    if template_type == "resume":
        latex_content = latex_content.strip()
    else:
        latex_content = clean_latex(latex_content)

    print("\n========== FINAL LATEX ==========\n")
    print(latex_content)
    print("\n=================================\n")

    if len(latex_content.strip()) < 10:

        return JSONResponse(
            {
                "ok": False,
                "error": "Generated LaTeX became empty."
            },
            status_code=200
        )

    if template_type == "resume":
        title = "resume"
    else:
        title = fix_title(title, content)

    temp_filename = f"temp_{uuid.uuid4().hex}"

    pdf_path = create_pdf(
        content=latex_content,
        filename=temp_filename,
        template_type=template_type,
        title=title,
        author=author or ""
    )

    final_filename = f"{clean_filename(title)}.pdf"

    print("PDF PATH:", pdf_path)
    print("PDF SIZE:", os.path.getsize(pdf_path))

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=final_filename
    )