import os, glob, re

base = 'frontend'
for f in glob.glob(f'{base}/**/*.html', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    depth = len(f.split(os.sep)) - 2
    if depth < 0: depth = 0
    prefix = '../' * depth if depth > 0 else './'
    if 'pages' not in f and 'index.html' in f: prefix = './'
    
    script_tag = f'<script src="{prefix}js/components.js"></script>'
    
    if 'navbar-container' not in content:
        content = re.sub(r'<nav.*?</nav>', '<div id="navbar-container"></div>', content, flags=re.DOTALL)
    
    if 'footer-container' not in content:
        if '<footer' in content:
            content = re.sub(r'<footer.*?</footer>', '<div id="footer-container"></div>', content, flags=re.DOTALL)
        else:
            content = content.replace('</body>', '<div id="footer-container"></div>\n</body>')
            
    if 'components.js' not in content:
        content = content.replace('</body>', f'{script_tag}\n</body>')
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Done injecting components')
