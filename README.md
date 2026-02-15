# 🤖 Job Application Automation System

**AI-Powered Job Application Bot** - Automatically find, customize, and apply to jobs using intelligent automation.

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Your Information
Edit `.env` file:
```bash
# Your Information
USER_NAME=Your Full Name
USER_EMAIL=your@email.com
USER_PHONE=+1234567890
USER_ADDRESS=Your City, State
USER_LINKEDIN=https://linkedin.com/in/yourprofile
USER_PORTFOLIO=https://github.com/yourprofile

# Get FREE Gemini API Key: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash
```

### 3. Add Your Resume
Place your resume PDF at: `data/resumes/base_resume.pdf`

### 4. Run the Bot
```powershell
# Test with 1 company
.\run.bat --test --limit 1

# Run full automation
.\run.bat
```

---

## ✨ Features

### 🤖 AI-Powered Automation
- **Smart Resume Customization** - Uses Gemini AI to tailor your resume for each job
- **Adaptive Form Filling** - Intelligently fills ANY job application form
- **Career Page Detection** - Automatically finds career pages on company websites
- **Job Scraping** - Extracts relevant job listings
- **Email Extraction** - Finds HR contact emails

### 🎯 Intelligent Matching
- Filters jobs based on your skills and experience
- Matches job requirements with your profile
- Prioritizes relevant positions

### 📊 Tracking & Logging
- Excel log of all applications
- Detailed system logs
- Success/failure tracking
- Email collection

### 🌐 Universal Compatibility
Works with:
- ✅ Greenhouse, Lever, Workday (optimized)
- ✅ LinkedIn, Indeed
- ✅ Custom company websites
- ✅ **ANY job application form**

---

## 📁 Project Structure

```
JobApplyAutomation/
├── data/
│   ├── companies.csv          # Companies to apply to
│   ├── resumes/
│   │   └── base_resume.pdf    # Your resume
│   └── output/
│       ├── applications_log.xlsx
│       └── system_logs.txt
├── modules/
│   ├── browser_manager.py     # Browser automation
│   ├── career_finder.py       # Find career pages
│   ├── job_scraper.py         # Scrape job listings
│   ├── resume_modifier.py     # AI resume customization
│   ├── form_filler.py         # Fill application forms
│   ├── ai_form_analyzer.py    # AI form analysis
│   └── adaptive_form_filler.py # Smart form filling
├── .env                       # Your configuration
├── config.py                  # System configuration
├── main.py                    # Main application
└── run.bat                    # Run script
```

---

## 🎨 How It Works

```
1. Load Companies → 2. Find Career Page → 3. Scrape Jobs → 4. Filter Relevant
                                                                      ↓
6. Submit ← 5. Fill Form ← 4. Upload Resume ← 3. Customize Resume ← 2. Match
```

### Step-by-Step Process:

1. **Load Companies** - Reads `companies.csv`
2. **Find Career Page** - Intelligently locates the careers section
3. **Scrape Jobs** - Extracts all job listings
4. **Filter Jobs** - Matches with your skills/experience
5. **Customize Resume** - AI tailors resume for each job
6. **Fill Application** - AI analyzes and fills the form
7. **Review & Submit** - Pauses for your review
8. **Track Results** - Logs everything to Excel

---

## ⚙️ Configuration

### `.env` File Settings

```bash
# ============================================
# USER INFORMATION
# ============================================
USER_NAME=Viraj Sangani
USER_EMAIL=sanganiviraj263@gmail.com
USER_PHONE=+918128800325
USER_ADDRESS=Mumbai, Maharashtra, India
USER_LINKEDIN=https://www.linkedin.com/in/viraj-sangani/
USER_PORTFOLIO=https://github.com/virajsangani
YEARS_EXPERIENCE=1.8
CURRENT_TITLE=Software Engineer
USER_SKILLS=React Native, JavaScript, React, Node.js, SQL, AWS

# ============================================
# AI CONFIGURATION (FREE!)
# ============================================
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7

# ============================================
# AUTOMATION SETTINGS
# ============================================
HEADLESS=False              # Set True to hide browser
TIMEOUT=30000               # Page load timeout (ms)
MIN_DELAY=1                 # Min delay between actions (seconds)
MAX_DELAY=3                 # Max delay between actions (seconds)

# ============================================
# FILE PATHS
# ============================================
BASE_RESUME_PATH=data/resumes/base_resume.pdf
COMPANIES_CSV=data/companies.csv
OUTPUT_DIR=data/output
```

### `companies.csv` Format

```csv
company_name,company_url
Google,https://www.google.com
Meta,https://www.meta.com
Amazon,https://www.amazon.com
```

---

## 🔑 Get FREE Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

**Free Tier Limits:**
- 1,500 requests/day
- More than enough for job applications!

---

## 🎯 Commands

```powershell
# Test with 1 company
.\run.bat --test --limit 1

# Test with 3 companies
.\run.bat --test --limit 3

# Run full automation
.\run.bat

# Create sample companies file
.\run.bat --create-sample
```

---

## 🤖 AI-Powered Features

### 1. **Adaptive Form Filling**
The system uses AI to understand and fill ANY form:

- **Analyzes page structure** - Understands what fields are present
- **Intelligent field mapping** - Maps your data to form fields
- **Multi-strategy approach** - Tries multiple methods to fill each field
- **ATS detection** - Optimized for Greenhouse, Lever, Workday, etc.
- **Universal compatibility** - Works with unknown/custom forms

### 2. **Smart Resume Customization**
AI tailors your resume for each job:

- Highlights relevant skills
- Emphasizes matching experience
- Optimizes keywords for ATS
- Maintains authenticity

### 3. **Intelligent Job Matching**
Filters jobs based on:

- Your skills and experience
- Job requirements
- Location preferences
- Seniority level

---

## 📊 Output & Tracking

### Excel Log (`applications_log.xlsx`)
Tracks:
- Company name
- Job title
- Application URL
- Status (Success/Failed/Manual)
- Timestamp
- Notes

### System Logs (`system_logs.txt`)
Detailed logs of:
- Every action taken
- Errors encountered
- Form fields filled
- API calls made

---

## 🛠️ Troubleshooting

### Issue: Browser not starting
**Solution:**
```powershell
playwright install chromium
```

### Issue: Gemini API error
**Solution:**
1. Check API key is correct in `.env`
2. Verify model is `gemini-2.0-flash`
3. Check you haven't exceeded free tier (1,500/day)

### Issue: Forms not filling
**Solution:**
1. Check user data is complete in `.env`
2. System will pause for manual review if needed
3. Check logs for specific errors

### Issue: No jobs found
**Solution:**
1. Check company URL is correct
2. Verify career page exists
3. Adjust job filtering criteria in `config.py`

---

## 🔒 Safety Features

### Manual Review
- System fills forms automatically
- **Pauses before submitting**
- Gives you time to review
- You control final submission

### Detailed Logging
- Every action is logged
- Easy to track what happened
- Debug issues quickly

### Graceful Failures
- Continues even if one company fails
- Provides clear error messages
- Never crashes unexpectedly

---

## 📈 Success Metrics

The system tracks:
- ✅ Applications submitted
- ✅ Forms filled successfully
- ✅ Resumes customized
- ✅ Emails collected
- ⚠️ Manual interventions needed
- ❌ Failed applications

---

## 💡 Tips for Best Results

### 1. Complete Your Profile
Fill all fields in `.env` for better form filling

### 2. Use Quality Resume
- PDF format
- ATS-friendly formatting
- Updated with latest experience

### 3. Start Small
Test with 1-3 companies first:
```powershell
.\run.bat --test --limit 3
```

### 4. Monitor First Runs
Watch how the system handles different forms

### 5. Keep API Key Safe
Never commit `.env` to version control

---

## 🚀 Advanced Usage

### Custom Job Filtering
Edit `config.py`:
```python
JOB_KEYWORDS = [
    'software engineer',
    'react native',
    'mobile developer'
]

EXCLUDED_KEYWORDS = [
    'senior',
    'lead',
    'manager'
]
```

### Adjust AI Creativity
In `.env`:
```bash
GEMINI_TEMPERATURE=0.9  # More creative
GEMINI_TEMPERATURE=0.5  # More conservative
```

### Headless Mode
For faster automation:
```bash
HEADLESS=True
```

---

## 📝 Requirements

- Python 3.10+
- Windows OS
- Internet connection
- FREE Gemini API key

---

## 🎉 What Makes This Special

### Traditional Bots ❌
- Hardcoded for specific websites
- Break when sites update
- Can't handle new websites
- Manual updates needed

### This AI-Powered Bot ✅
- Adapts to ANY website
- Works with site updates
- Handles unknown forms
- Self-improving with AI

---

## 🤝 Support

### Common Issues
1. **Unicode errors** - All emojis have been replaced with ASCII
2. **Browser errors** - Run `playwright install chromium`
3. **API errors** - Check API key and model name
4. **Form filling** - System will pause for manual review

### Logs Location
- System logs: `data/output/system_logs.txt`
- Applications: `data/output/applications_log.xlsx`

---

## 📜 License

This project is for educational and personal use.

---

## 🎯 Summary

You have a **fully functional, AI-powered job application automation system** that:

1. ✅ Uses **FREE Gemini AI**
2. ✅ Works with **ANY website**
3. ✅ **Intelligently fills forms**
4. ✅ **Customizes resumes** for each job
5. ✅ **Tracks everything** automatically

**Ready to automate your job search! 🚀**

---

## 📞 Quick Reference

```powershell
# Setup
pip install -r requirements.txt
playwright install chromium

# Configure
# Edit .env with your information
# Add resume to data/resumes/base_resume.pdf

# Run
.\run.bat --test --limit 1

# Check results
# Excel: data/output/applications_log.xlsx
# Logs: data/output/system_logs.txt
```

**That's it! Start applying to jobs automatically! 🎊**
