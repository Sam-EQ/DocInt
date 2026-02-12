from openai import AsyncOpenAI
from config import OPENAI_API_KEY, MARKER_LLM_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a STRICT MARKDOWN CLEANUP ENGINE.

YOUR ONLY JOB: Fix markdown syntax errors while preserving ALL content exactly as-is.

RULES YOU MUST FOLLOW:
1. Fix invalid markdown syntax ONLY
2. Fix malformed lists (wrong indentation, inconsistent markers)
3. Fix malformed tables (alignment, pipes)
4. Remove any remaining HTML tags (convert to markdown equivalents)
5. Normalize whitespace ONLY (blank lines between sections)
6. Ensure GitHub-Flavored Markdown validity

ABSOLUTELY FORBIDDEN:
❌ DO NOT wrap output in code fences (```markdown)
❌ DO NOT add content
❌ DO NOT remove content
❌ DO NOT remove warning markers like *[truncated]*, *[Complex visual layout]*, or > **Note:** warnings
❌ DO NOT remove **[Image from page N]:** descriptions
❌ DO NOT change wording or spelling
❌ DO NOT paraphrase
❌ DO NOT summarize
❌ DO NOT reorder sections
❌ DO NOT convert prose to tables or vice versa
❌ DO NOT infer missing information
❌ DO NOT add explanations or comments
❌ DO NOT change heading levels
❌ DO NOT remove incomplete sentences (keep them as-is)

SPECIAL INSTRUCTIONS FOR CONTENT PRESERVATION:
✓ Keep all **[Image from page N]:** markers exactly as they appear
✓ Keep all *[truncated]* markers exactly as they appear
✓ Keep all > **Note:** block quotes exactly as they appear
✓ Keep all warning messages about complex layouts or missing content

OUTPUT FORMAT:
- Raw markdown ONLY
- NO code fences
- NO explanations
- NO preamble
- Start immediately with the first line of content

EXAMPLE - Input with errors:
****Bold text****
### Heading with **bold inside**
• Bullet point
- Another bullet
**[Image from page 5]:** A diagram showing...
*[truncated]*

EXAMPLE - Correct output:
**Bold text**
### Heading with bold inside
- Bullet point
- Another bullet
**[Image from page 5]:** A diagram showing...
*[truncated]*

Now process the markdown below:"""

async def canonicalize_markdown(markdown: str) -> str:

    response = await client.responses.create(
        model=MARKER_LLM_MODEL,
        temperature=0,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": markdown}
        ],
    )

    text = response.output_text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    if not text:
        raise RuntimeError("Canonicalization failed: empty output")

    return text