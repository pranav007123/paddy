import os

path = 'd:/marian 4th sem/project/zip/paddy/templates/shop/'
for filename in os.listdir(path):
    if filename.endswith('.html'):
        full_path = os.path.join(path, filename)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace base extends
        new_content = content.replace("{% extends 'base.html' %}", "{% extends 'shop/shop_base.html' %}")
        new_content = new_content.replace('{% extends "base.html" %}', "{% extends 'shop/shop_base.html' %}")
        
        # Check for static file references?
        # Maybe I should also replace static paths? The source used media/paddy etc.
        # But shop templates likely referred to their own static.
        
        if content != new_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {filename}')
