# DISC Assessment Integration Guide

This guide explains how to integrate the Python-based DISC personality assessment into your Technical Profiles system (React/Node.js/PostgreSQL).

## Option 1: Python Microservice (Recommended)

Run the Python logic as a microservice using the provided `api.py` (FastAPI).

### 1. Start the Python API
```bash
pip install -r requirements.txt
python api.py
```
The API will be available at `http://localhost:8000`.

### 2. Call the API from Express.js
You can use `fetch` or `axios` in your Node.js backend to communicate with the Python service.

```javascript
// Example Express.js route handler
async function evaluateDisc(req, res) {
  const userAnswers = req.body.answers; // Expecting { "0": 5, "1": 3, ... }

  try {
    const response = await fetch('http://localhost:8000/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: userAnswers })
    });

    if (!response.ok) {
      throw new Error('Failed to evaluate DISC assessment');
    }

    const result = await response.json();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

## Option 2: Standalone Python Script
If you prefer not to have a running service, you can invoke the Python logic as a child process, though this is less efficient.

## Option 3: Porting to TypeScript
The core logic in `disc_core.py` is pure math and can be ported to TypeScript for a 100% native Node.js implementation. The `reportlab` PDF generation would need to be replaced with a library like `pdfkit` or `jsPDF`.

## Key Files for Integration
- `disc_core.py`: Contains scoring, normalization, and vector calculation logic.
- `api.py`: FastAPI implementation exposing the logic via HTTP.
- `questions.json`: The source of truth for assessment questions.
- `disc_descriptions.json`: Definitions of personality profiles and combinations.
- `strengths.json`: Complementary strengths assessment data.
