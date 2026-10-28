import math
import re
from html import escape
from hashlib import sha256
from io import BytesIO
from markdown_it import MarkdownIt
from loguru import logger

from .protocol import Paper


_MARKDOWN = MarkdownIt("commonmark", {"html": False})
_LATEX_MATH = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)", re.DOTALL)


def _render_latex(latex: str, inline_images: dict[str, bytes]) -> str:
    """Render supported LaTeX math as a CID image for email clients."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.mathtext import math_to_image

    content_id = f"math-{sha256(latex.encode('utf-8')).hexdigest()[:20]}"
    if content_id not in inline_images:
        image = BytesIO()
        math_to_image(
            f"${latex}$",
            image,
            prop=FontProperties(size=12),
            dpi=144,
            format="png",
            color="#333333",
        )
        inline_images[content_id] = image.getvalue()
    return (
        f'<img src="cid:{content_id}" alt="{escape(latex, quote=True)}" '
        'style="display:inline-block;vertical-align:-0.25em;height:1.4em;max-width:100%;width:auto;">'
    )


def _render_markdown(value: str | None, inline_images: dict[str, bytes]) -> str:
    """Render model-generated Markdown and inline math as email-safe HTML."""
    source = value or ""
    source = re.sub(r"(\*\*[^*\n]+?\*\*)(?=\S)", r"\1 ", source)
    source = re.sub(r"(?<!\*)\*[^*\n]+?\*(?!\*)(?=\S)", r"\g<0> ", source)

    math_replacements: dict[str, str] = {}

    def replace_math(match: re.Match[str]) -> str:
        latex = match.group(1).strip()
        if not latex:
            return match.group(0)
        placeholder = f"ZOTEROMATHPLACEHOLDER{len(math_replacements)}TOKEN"
        try:
            math_replacements[placeholder] = _render_latex(latex, inline_images)
        except Exception as error:
            logger.warning("Failed to render inline math expression: {}", error)
            math_replacements[placeholder] = f"<code>{escape(match.group(0))}</code>"
        return placeholder

    source = _LATEX_MATH.sub(replace_math, source)
    tokens = _MARKDOWN.parse(source)
    for token in tokens:
        if token.type == "paragraph_open":
            token.attrSet("style", "margin:0 0 8px 0;")
        elif token.type in {"bullet_list_open", "ordered_list_open"}:
            token.attrSet("style", "margin:4px 0;padding-left:22px;")
    rendered = _MARKDOWN.renderer.render(tokens, _MARKDOWN.options, {})
    for placeholder, html in math_replacements.items():
        rendered = rendered.replace(placeholder, html)
    return rendered


framework = """
<!DOCTYPE HTML>
<html>
<head>
  <style>
    .star-wrapper {
      font-size: 1.3em; /* 调整星星大小 */
      line-height: 1; /* 确保垂直对齐 */
      display: inline-flex;
      align-items: center; /* 保持对齐 */
    }
    .half-star {
      display: inline-block;
      width: 0.5em; /* 半颗星的宽度 */
      overflow: hidden;
      white-space: nowrap;
      vertical-align: middle;
    }
    .full-star {
      vertical-align: middle;
    }
  </style>
</head>
<body>

<div>
    __CONTENT__
</div>

<br><br>
<div>
To unsubscribe, remove your email in your Github Action setting.
</div>

</body>
</html>
"""

def get_empty_html():
  block_template = """
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
  <tr>
    <td style="font-size: 20px; font-weight: bold; color: #333;">
        No Papers Today. Take a Rest!
    </td>
  </tr>
  </table>
  """
  return block_template

def get_block_html(
    title: str,
    authors: str,
    rate: str,
    tldr: str,
    paper_url: str,
    affiliations: str = None,
    introduction: str = None,
    rating_urls: dict[int, str] | None = None,
    inline_images: dict[str, bytes] | None = None,
):
    rating_buttons = ""
    if rating_urls:
        rating_buttons = "<span style='font-size:13px;color:#555;padding-left:8px;'>Rate:</span>"
        rating_buttons += "".join(
            f'<a href="{escape(rating_urls[score], quote=True)}" '
            "style=\"display:inline-block;margin-left:4px;text-decoration:none;font-size:13px;font-weight:bold;"
            "color:#333;background-color:#eee;padding:8px 10px;border-radius:4px;\" "
            f'aria-label="Rate this paper {score} out of 5">{score}</a>'
            for score in range(1, 6)
            if score in rating_urls
        )

    inline_images = inline_images if inline_images is not None else {}
    tldr_html = _render_markdown(tldr, inline_images)
    introduction_html = _render_markdown(introduction, inline_images)

    block_template = """
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
    <tr>
        <td style="font-size: 20px; font-weight: bold; color: #333;">
            {title}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #666; padding: 8px 0;">
            {authors}
            <br>
            <i>{affiliations}</i>
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>Relevance:</strong> {rate}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0; line-height: 1.5;">
            <strong>TLDR:</strong><div>{tldr}</div>
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0; line-height: 1.5;">
            <strong>论文介绍:</strong><div>{introduction}</div>
        </td>
    </tr>

    <tr>
        <td style="padding: 8px 0;">
            <a href="{paper_url}" style="display: inline-block; text-decoration: none; font-size: 14px; font-weight: bold; color: #fff; background-color: #d9534f; padding: 8px 16px; border-radius: 4px;">Paper</a>
            {rating_buttons}
        </td>
    </tr>
</table>
"""
    return block_template.format(
        title=escape(title or ""),
        authors=escape(authors or ""),
        rate=escape(rate or ""),
        tldr=tldr_html,
        introduction=introduction_html,
        paper_url=escape(paper_url or "", quote=True),
        affiliations=escape(affiliations or ""),
        rating_buttons=rating_buttons,
    )

def get_stars(score:float):
    full_star = '<span class="full-star">⭐</span>'
    half_star = '<span class="half-star">⭐</span>'
    low = 6
    high = 8
    if score <= low:
        return ''
    elif score >= high:
        return full_star * 5
    else:
        interval = (high-low) / 10
        star_num = math.ceil((score-low) / interval)
        full_star_num = int(star_num/2)
        half_star_num = star_num - full_star_num * 2
        return '<div class="star-wrapper">'+full_star * full_star_num + half_star * half_star_num + '</div>'


def render_email(
    papers: list[Paper],
    rating_links: dict[str, dict[int, str]] | None = None,
    inline_images: dict[str, bytes] | None = None,
) -> str:
    inline_images = inline_images if inline_images is not None else {}
    parts = []
    if len(papers) == 0 :
        return framework.replace('__CONTENT__', get_empty_html())
    
    for p in papers:
        #rate = get_stars(p.score)
        rate = str(round(p.score, 1)) if p.score is not None else 'Unknown'
        author_list = [a for a in p.authors]
        num_authors = len(author_list)
        if num_authors <= 5:
            authors = ', '.join(author_list)
        else:
            authors = ', '.join(author_list[:3] + ['...'] + author_list[-2:])
        if p.affiliations is not None:
            affiliations = p.affiliations[:5]
            affiliations = ', '.join(affiliations)
            if len(p.affiliations) > 5:
                affiliations += ', ...'
        else:
            affiliations = 'Unknown Affiliation'
        parts.append(
            get_block_html(
                p.title,
                authors,
                rate,
                p.tldr,
                p.url,
                affiliations,
                introduction=p.introduction,
                rating_urls=(rating_links or {}).get(p.url),
                inline_images=inline_images,
            )
        )

    content = '<br>' + '</br><br>'.join(parts) + '</br>'
    return framework.replace('__CONTENT__', content)
