const text = "&lt;h2&gt;COVID-19 Treatment&lt;/h2&gt;\\n&lt;p&gt;Some text.&lt;/p&gt;\\n&lt;table border=\"1\"&gt;&lt;tr&gt;&lt;td&gt;Data&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;";

let html = text;

const safeTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'ul', 'ol', 'li', 'sup', 'sub', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'b', 'strong', 'i', 'em', 'u', 'span', 'div'];

safeTags.forEach(tag => {
    // Revive opening tags (including any attributes)
    const openRegex = new RegExp(`&lt;${tag}(&gt;|\\s+.*?&gt;)`, 'gi');
    html = html.replace(openRegex, (match, p1) => {
        const attrs = p1.substring(0, p1.length - 4); // strip '&gt;'
        return `<${tag}${attrs}>`;
    });
    
    // Revive closing tags
    const closeRegex = new RegExp(`&lt;\\/${tag}&gt;`, 'gi');
    html = html.replace(closeRegex, `</${tag}>`);
});

console.log(html);
