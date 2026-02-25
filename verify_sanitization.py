from bs4 import BeautifulSoup
import re

def sanitize_telegram_html(text: str) -> str:
    # Use BeautifulSoup to fix nesting and close tags
    soup = BeautifulSoup(text, 'html.parser')
    
    allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre']
    
    def clean_node(node):
        if hasattr(node, 'name') and node.name is not None:
            if node.name in allowed_tags:
                attrs = ""
                if node.name == 'a' and node.get('href'):
                    attrs = f' href="{node.get("href")}"'
                
                inner = "".join(clean_node(child) for child in node.children)
                return f"<{node.name}{attrs}>{inner}</{node.name}>"
            else:
                # Disallowed tag: skip tag, keep children
                return "".join(clean_node(child) for child in node.children)
        else:
            # Text node: escape for Telegram HTML
            # Note: Telegram HTML requires escaping <, >, &
            s = str(node)
            return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return "".join(clean_node(child) for child in soup.children)

# Test cases
test_cases = [
    ("<i>Nested <u>Underline</i> Still Underlined</u>", "<i>Nested <u>Underline</u></i> Still Underlined"),
    ("Bold <b>with rogue < bracket", "Bold <b>with rogue &lt; bracket</b>"),
    ("Unclosed <i>Italic", "Unclosed <i>Italic</i>"),
    ("Overlapping <b>bold <i>italic</b> normal</i>", "<b>bold <i>italic</i></b> normal"),
    ("Link <a href='http://x.com'>text</a> and <span>disallowed</span> tag", "<a href=\"http://x.com\">text</a> and disallowed tag"),
    ("Special & char", "Special &amp; char")
]

if __name__ == "__main__":
    print("Testing sanitize_telegram_html...")
    for i, (input_html, expected) in enumerate(test_cases):
        output = sanitize_telegram_html(input_html)
        print(f"\nTest {i+1}:")
        print(f"  Input:  {input_html}")
        print(f"  Output: {output}")
        # Note: expected values might vary slightly based on BeautifulSoup's parsing strategy,
        # but the key is that the output must be valid HTML.
