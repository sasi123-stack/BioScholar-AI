# Biomedical Search Engine - Frontend

A modern, responsive web interface for the Biomedical Search Engine.

## Features

- **Search Documents**: Search PubMed articles and clinical trials using hybrid search (keyword + semantic)
- **Question Answering**: Ask questions and get AI-powered answers with confidence scores
- **User Authentication**: Login/Sign-up to save your research history
- **Reading List**: Bookmark articles and export bibliographies
- **Advanced Filters**: Control search behavior with customizable parameters
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 📘 Documentation

For detailed instructions on how to use the website, please refer to the **[User Guide](USER_GUIDE.md)**.

## Quick Start

### Option 1: Using Python HTTP Server

```bash
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080

### Option 2: Using Node.js HTTP Server

```bash
cd frontend
npx http-server -p 8080
```

Then open: http://localhost:8080

### Option 3: Direct File Access

Simply open `index.html` in your web browser.

## Prerequisites

The backend API must be running on `http://localhost:8000`. Start it with:

```bash
cd ..
python -m uvicorn src.api.app:app --reload
```

## Usage

### Search Tab

1. Enter your search query (e.g., "COVID-19 treatment", "diabetes management")
2. Select source (All Sources, PubMed, or Clinical Trials)
3. Adjust search balance slider (Keyword ← → Semantic)
4. Enable/disable AI reranking
5. Click "Search" or press Enter

### Question Answering Tab

1. Enter your question (e.g., "What is the treatment for COVID-19?")
2. Select source
3. Choose number of answers (1, 3, or 5)
4. Click "Get Answer" or press Enter

## Configuration

To change the API endpoint, edit `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling
├── app.js          # JavaScript application logic
└── README.md       # This file
```

## Features Breakdown

### Search Features
- Hybrid search with adjustable keyword/semantic balance
- Cross-encoder reranking for improved relevance
- Multiple source filtering
- Real-time results with relevance scores
- Result metadata display (authors, dates, IDs)

### QA Features
- Natural language question answering
- Multiple answer retrieval
- Confidence scoring (High/Medium/Low/Very Low)
- Supporting evidence passages
- Source attribution

### UI Features
- Tab-based navigation
- Loading states and spinners
- Empty state messages
- Error handling and display
- Responsive grid layout
- Status indicators
- Statistics panel

## Troubleshooting

**API Connection Issues:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API health endpoint: http://localhost:8000/api/v1/health

**No Results:**
- Check if documents are indexed
- Try different search terms
- Adjust search parameters

**Slow Performance:**
- Models are CPU-based, first query may be slow
- Subsequent queries use cached models
- Consider reducing max_results

## Development

To modify the frontend:

1. Edit HTML structure in `index.html`
2. Update styles in `styles.css`
3. Modify behavior in `app.js`
4. Refresh browser to see changes

No build step required!

## Future Enhancements

- Document detail modal
- Search history
- Export results
- Advanced filters
- Dark mode
- Visualization of embeddings
- Batch question processing
- PDF export
