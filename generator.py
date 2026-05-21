import os
import subprocess
from string import Template

from fastapi import HTTPException


def create_pdf(content, filename, template_type, title, author):

    template_dir = "latex_templates"

    template_file = os.path.join(
        template_dir,
        f"{template_type}.tex"
    )

    if not os.path.exists(template_file):
        template_file = os.path.join(
            template_dir,
            "article.tex"
        )

    output_dir = os.path.abspath("generated")

    os.makedirs(output_dir, exist_ok=True)

    tex_file = os.path.join(output_dir, f"{filename}.tex")
    pdf_file = os.path.join(output_dir, f"{filename}.pdf")
    log_file = os.path.join(output_dir, f"{filename}.log")

    try:

        with open(template_file, "r", encoding="utf-8") as f:
            template = Template(f.read())

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to load template: {str(e)}"
        )

    tex_code = template.substitute(
        content=content or "",
        title=title or "",
        author=author or "",
        date=""
    )

    print("\n========== GENERATED TEX ==========\n")
    print(tex_code)
    print("\n===================================\n")

    try:

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_code)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to write TEX file: {str(e)}"
        )

    try:

        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                os.path.basename(tex_file)
            ],
            cwd=output_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("\n========== PDFLATEX STDOUT ==========\n")
        print(result.stdout)

        print("\n========== PDFLATEX STDERR ==========\n")
        print(result.stderr)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to run pdflatex: {str(e)}"
        )

    if result.returncode != 0:

        error_message = "LaTeX compilation failed."

        if os.path.exists(log_file):

            with open(
                log_file,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as log:

                error_message = log.read()[-4000:]

        raise HTTPException(
            status_code=500,
            detail=error_message
        )

    if not os.path.exists(pdf_file):

        raise HTTPException(
            status_code=500,
            detail="PDF was not created."
        )

    if os.path.getsize(pdf_file) < 500:

        raise HTTPException(
            status_code=500,
            detail="Generated PDF is empty."
        )

    with open(pdf_file, "rb") as f:

        header = f.read(4)

    if header != b"%PDF":

        raise HTTPException(
            status_code=500,
            detail="Invalid PDF generated."
        )

    return pdf_file