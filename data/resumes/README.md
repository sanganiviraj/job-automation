
# IMPORTANT: Place Your Resume Here

This folder should contain your base resume in PDF format.

## Instructions:

1. **Create your resume PDF** using your preferred tool (Word, Google Docs, LaTeX, etc.)

2. **Save it as:** `base_resume.pdf`

3. **Place it in this folder:** `data/resumes/base_resume.pdf`

## Alternative:

If you want to use a different filename or location:

1. Update the `.env` file:
   ```
   BASE_RESUME_PATH=data/resumes/your_custom_name.pdf
   ```

## Resume Tips:

- Keep it to 1-2 pages
- Use a clean, professional format
- Include:
  - Contact information
  - Professional summary
  - Work experience
  - Education
  - Skills
  - Projects (if applicable)
  - Certifications (if applicable)

## AI Customization:

The system will:
- Extract text from your PDF
- Customize approximately 20% based on job description
- Highlight relevant skills and experience
- Maintain your original formatting structure
- Create a new PDF for each application

## Note:

The AI customization requires an OpenAI API key. If you don't have one:
- The system will use your base resume for all applications
- You can still use all other automation features
