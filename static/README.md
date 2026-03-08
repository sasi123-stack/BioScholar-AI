# Static Files

This folder contains static assets served by the API.

## favicon.ico / favicon.svg

The current favicon is a default SVG-based icon.

### To Replace with Your Logo:

1. **If you have an ICO file:** 
   - Place `favicon.ico` in this folder
   - Update endpoint in `app_minimal.py` to serve `.ico` instead of `.svg`

2. **If you have a PNG/JPG:**
   - Convert to ICO format (use online converter or PIL)
   - Save as `favicon.ico` in this folder

3. **If you have an SVG:**
   - Replace `favicon.svg` with your file
   - Keep the filename as `favicon.svg`

The favicon will be automatically served at:
- `/favicon.ico` (main endpoint)
- `/static/favicon.svg` (direct static access)

Changes will be live after pushing to git.
