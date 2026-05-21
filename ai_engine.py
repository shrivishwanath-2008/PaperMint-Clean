# # # from curses import flash
# # from email.mime import text
# # import os
# # import json
# # from pydoc import text
# # import re
# # from urllib import response
# # import google.generativeai as genai
# # from dotenv import load_dotenv

# # load_dotenv()
# # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # MODEL = "gemini-2.5-flash"
# # model = genai.GenerativeModel(MODEL)


# # def extract_tagged_field(text: str, tag: str) -> str:
# #     if not text:
# #         return ""

# #     start_tag = f"[{tag}]"
# #     end_tag = f"[/{tag}]"

# #     start_index = text.find(start_tag)

# #     if start_index == -1:
# #         return ""

# #     start_index += len(start_tag)

# #     end_index = text.find(end_tag, start_index)

# #     if end_index == -1:
# #         return ""

# #     return text[start_index:end_index].strip()

# # def normalize_generated_content(content: str) -> str:
# #     if not content:
# #         return ""

# #     normalized = str(content).strip()
# #     normalized = normalized.replace("**", "")
# #     normalized = normalized.replace("(empty)", "")
# #     normalized = normalized.replace("[empty]", "")

# #     if normalized.lower() == "empty":
# #         return ""

# #     return str(normalized).strip()


# # def generate_all(prompt: str, template_type: str):
# #     api_key = os.getenv("GEMINI_API_KEY")
# #     if not api_key:
# #         return None, None, None, "GEMINI_API_KEY is missing."

# #     system = f'''
# # Return ONLY this format:

# # [TITLE]
# # [/TITLE]

# # [AUTHOR]
# # [/AUTHOR]

# # [CONTENT]
# # [/CONTENT]

# # RULES:
# # - Must include ALL tags and close them
# # - Output must end with [/CONTENT]
# # - No markdown, no explanations
# # - LaTeX only inside CONTENT

# # Template: {template_type}

# # Resume:
# # - No title
# # - Sections: Education, Experience, Projects, Skills
# # - Use \\section*
# # - Use \\begin{{itemize}} \\item ... \\end{{itemize}}
# # '''

# #     text = None

# #     # ✅ retry system
# #     for attempt in range(2):
# #         try:
# #             response = model.generate_content(
# #                 f"{system}\n{prompt}",
# #                 generation_config={
# #                     "temperature": 0.6,
# #                     "max_output_tokens": 2000,
# #                 },
# #             )

# #             # extract safely
# #             if hasattr(response, "text") and response.text:
# #                 text = response.text

# #             if not text:
# #                 raise ValueError("Empty AI response")

# #             text = str(text)
# # if template_type == "resume":
# #     extra_rules = """
# # Resume rules:
# # - No title
# # - Use concise bullet points
# # - Use \\section*
# # - Use proper LaTeX
# # """
# # else:
# #     extra_rules = """
# # Article rules:
# # - Do NOT include:
# #   \\documentclass
# #   \\usepackage
# #   \\begin{document}
# #   \\end{document}
# #   \\maketitle
# # - Return BODY ONLY
# # """

# # system = f"""
# # Return ONLY this format:

# # [TITLE]
# # [/TITLE]

# # [AUTHOR]
# # [/AUTHOR]

# # [CONTENT]
# # [/CONTENT]

# # RULES:
# # - Must include all tags
# # - No markdown
# # - No explanations
# # - CONTENT must contain ONLY LaTeX body content

# # Template: {template_type}

# # {extra_rules}
# # """

# #             if not text.strip().endswith("[/CONTENT]"):
# #                 print("FIXING: adding closing tag")
# #                 text += "\n[/CONTENT]"
# #             break  # success

# #         except Exception as e:
# #             print(f"Attempt {attempt+1} failed:", e)
# #             text = None

# #     if not text:
# #         return None, None, None, "AI failed. Try again."

# #     # extract fields
# #     title = extract_tagged_field(text, "TITLE")
# #     author = extract_tagged_field(text, "AUTHOR")
# #     content = extract_tagged_field(text, "CONTENT")

# #     if not content:
# #         print("FALLBACK: using raw text")
# #         content = text

# #     content = normalize_generated_content(content)

# #     if not content:
# #         print("FALLBACK: using raw text")
# #         content = text

# #     return title, author, content, None

# import os
# import re

# import google.generativeai as genai
# from dotenv import load_dotenv


# # ---------------- SETUP ---------------- #

# load_dotenv()

# genai.configure(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# MODEL = "gemini-2.5-flash"

# model = genai.GenerativeModel(MODEL)


# # ---------------- HELPERS ---------------- #

# def extract_tagged_field(text: str, tag: str) -> str:
#     """
#     Safely extract content between tags.
#     """

#     if not text:
#         return ""

#     start_tag = f"[{tag}]"
#     end_tag = f"[/{tag}]"

#     start_index = text.find(start_tag)

#     if start_index == -1:
#         return ""

#     start_index += len(start_tag)

#     end_index = text.find(end_tag, start_index)

#     if end_index == -1:
#         return ""

#     return text[start_index:end_index].strip()


# def normalize_generated_content(content: str) -> str:
#     """
#     Remove common garbage from AI output.
#     """

#     if not content:
#         return ""

#     content = str(content).strip()

#     replacements = [
#         "**",
#         "(empty)",
#         "[empty]"
#     ]

#     for item in replacements:
#         content = content.replace(item, "")

#     if content.lower() == "empty":
#         return ""

#     return content.strip()


# def build_system_prompt(template_type: str) -> str:

#     if template_type == "resume":

#         extra_rules = r"""
# Resume rules:
# - No title
# - Use concise bullet points
# - Use \section*
# - Use valid LaTeX only
# - Use itemize properly
# """

#     else:

#         extra_rules = r"""
# Article rules:
# - Return ONLY LaTeX BODY content
# - Do NOT include:
#   \documentclass
#   \usepackage
#   \begin{document}
#   \end{document}
#   \maketitle
#   \title
#   \author
#   \date
#   \geometry
# """

#     return f"""
# Return ONLY this exact format:

# [TITLE]
# Your title here
# [/TITLE]


# [CONTENT]
# LaTeX body content here
# [/CONTENT]

# RULES:
# - Must include ALL tags
# - Must close ALL tags
# - No markdown
# - No explanations
# - CONTENT must contain ONLY LaTeX body content
# - Never include full LaTeX document structure

# Template: {template_type}

# {extra_rules}
# """


# # ---------------- MAIN GENERATION ---------------- #

# def generate_all(prompt: str, template_type: str):

#     api_key = os.getenv("GEMINI_API_KEY")

#     if not api_key:
#         return None, None, None, "GEMINI_API_KEY is missing."

#     system_prompt = build_system_prompt(template_type)

#     try:

#         response = model.generate_content(
#             f"{system_prompt}\n\nUSER REQUEST:\n{prompt}",
#             generation_config={
#                 "temperature": 0.2,
#                 "max_output_tokens": 2500,
#             },
#         )

#         text = ""

#         if hasattr(response, "text") and response.text:
#             text = str(response.text)

#         if not text.strip():
#             return None, None, None, "AI returned empty response."

#         # emergency closing tag fix
#         if "[/CONTENT]" not in text:
#             print("FIXING: adding closing tag")
#             text += "\n[/CONTENT]"

#         print("\n========== RAW AI OUTPUT ==========\n")
#         print(text)
#         print("\n===================================\n")

#         # extract sections
#         title = extract_tagged_field(text, "TITLE")
#         author = extract_tagged_field(text, "AUTHOR")
#         content = extract_tagged_field(text, "CONTENT")

#         # validate content extraction
#         if not content.strip():
#             return None, None, None, "AI failed to generate CONTENT section."

#         # clean content
#         content = normalize_generated_content(content)

#         # reject malformed outputs
#         forbidden = [
#             "[TITLE]",
#             "[/TITLE]",
#             "[AUTHOR]",
#             "[/AUTHOR]",
#             "[CONTENT]",
#             "[/CONTENT]"
#         ]

#         for item in forbidden:
#             if item in content:
#                 return None, None, None, "Malformed AI response."

#         if not content.strip():
#             return None, None, None, "Generated content was empty."

#         return (
#             title.strip(),
#             author.strip(),
#             content.strip(),
#             None
#         )

#     except Exception as e:

#         print("AI ERROR:", str(e))

#         return None, None, None, str(e)

import os
import re

import google.generativeai as genai
from dotenv import load_dotenv


# ---------------- SETUP ---------------- #

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-flash-latest"

model = genai.GenerativeModel(MODEL)


# ---------------- HELPERS ---------------- #

def extract_tagged_field(text: str, tag: str) -> str:

    if not text:
        return ""

    pattern = rf"\[{tag}\](.*?)\[/{tag}\]"

    match = re.search(
        pattern,
        text,
        re.DOTALL
    )

    if not match:
        return ""

    return match.group(1).strip()


def normalize_generated_content(content: str) -> str:

    if not content:
        return ""

    content = str(content).strip()

    garbage = [
        "**",
        "(empty)",
        "[empty]"
    ]

    for item in garbage:
        content = content.replace(item, "")

    return content.strip()


def build_system_prompt(template_type: str) -> str:

    if template_type == "resume":

        extra_rules = r"""
Resume rules:
- No title
- Use concise bullet points
- Use \section*
- Use itemize
- Use proper LaTeX
"""

    else:

        extra_rules = r"""
Article rules:
- Return ONLY LaTeX BODY content
- Do NOT include:

  \documentclass
  \usepackage
  \begin{document}
  \end{document}
  \maketitle
  \title
  \author
  \date
- Never include author names
- Never include department names
- Never include bylines
"""

    return f"""
Return ONLY this exact format:

[TITLE]
Your title
[/TITLE]

[AUTHOR]

[/AUTHOR]

[CONTENT]
LaTeX body content
[/CONTENT]

RULES:
- Must include ALL tags
- Must close ALL tags
- No markdown
- No explanations
- CONTENT must contain ONLY valid LaTeX body content
- Never include full LaTeX document structure

Template: {template_type}

{extra_rules}
"""


# ---------------- MAIN ---------------- #

def generate_all(prompt: str, template_type: str):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None, None, None, "Missing GEMINI_API_KEY."

    try:

        system_prompt = build_system_prompt(template_type)

        response = model.generate_content(
            f"{system_prompt}\n\nUSER REQUEST:\n{prompt}",
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 4000,
            }
        )

        text = ""

        if hasattr(response, "text"):
            text = str(response.text)

        if not text.strip():
            return None, None, None, "Empty AI response."

        if "[/CONTENT]" not in text:
            print("FIXING: adding closing tag")
            text += "\n[/CONTENT]"

        print("\n========== RAW AI OUTPUT ==========\n")
        print(text)
        print("\n===================================\n")

        title = extract_tagged_field(text, "TITLE")
        author = extract_tagged_field(text, "AUTHOR")
        content = extract_tagged_field(text, "CONTENT")

        if not content.strip():
            return None, None, None, "AI failed to generate content."

        content = normalize_generated_content(content)

        forbidden = [
            "[TITLE]",
            "[/TITLE]",
            "[AUTHOR]",
            "[/AUTHOR]",
            "[CONTENT]",
            "[/CONTENT]"
        ]

        for item in forbidden:
            if item in content:
                return None, None, None, "Malformed AI response."

        return (
            title.strip(),
            author.strip(),
            content.strip(),
            None
        )

    except Exception as e:

        print("AI ERROR:", str(e))

        return None, None, None, str(e)