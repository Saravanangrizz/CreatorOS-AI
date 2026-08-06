# 🚀 CreatorOS AI

## Overview

CreatorOS AI is an **AI-powered content creation platform** that helps YouTube creators transform a single content idea into a complete publishing package.

Instead of using multiple tools for research, script writing, SEO, thumbnail planning, and publishing, CreatorOS AI combines everything into one streamlined workflow powered by specialized AI agents.

---

# The Problem

Creating quality YouTube content requires many repetitive tasks:

* Finding trending topics
* Researching the subject
* Writing scripts
* Creating thumbnail ideas
* Optimizing SEO
* Planning publication

Most creators switch between several AI tools and websites to complete these steps, making the process slow and fragmented.

---

# Our Solution

CreatorOS AI automates the entire workflow using a **multi-agent architecture**.

Each AI agent is responsible for one specific task, and together they generate a complete creator-ready package from a single topic.

```
Topic
   │
   ▼
Trend Analysis
   │
   ▼
Research
   │
   ▼
Script Writing
   │
   ▼
Thumbnail Strategy
   │
   ▼
SEO Optimization
   │
   ▼
Publishing Plan
```

This structured approach produces organized and consistent results while keeping the workflow simple for creators.

---

# AI Agents

### 📈 Trend Analyst

Finds trending content ideas, keywords, and audience opportunities.

### 🔍 Research Agent

Builds a structured outline and gathers key information about the topic.

### ✍️ Script Writer

Creates an engaging script with a strong hook, detailed sections, and a call to action.

### 🎨 Thumbnail Strategist

Suggests thumbnail concepts, color psychology, and clickability improvements.

### 🚀 SEO Specialist

Generates optimized titles, descriptions, tags, hashtags, and video chapters.

### 📅 Publishing Planner

Recommends the best publishing time, upload checklist, and weekly promotion strategy.

---

# Key Features

* Multi-agent AI workflow
* Modern and responsive user interface
* Configurable AI generation settings
* Pipeline visualization
* Project workspace
* One-click regeneration
* Organized creator-ready output

---

# Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* FastAPI
* Python
* SQLAlchemy

### AI

* Gemini API
* Modular AI agent architecture

---

# Why CreatorOS AI?

Instead of asking one AI to do everything in a single prompt, CreatorOS AI divides the workflow into specialized stages.

This makes the generated content more structured, easier to review, and easier to improve while giving creators a complete publishing package in one place.

---
For hackathon judges, the setup guide should be **short, foolproof, and take less than 5 minutes**. They are unlikely to troubleshoot dependency issues, so keep it simple.

---

# 🚀 Setup Guide

## Prerequisites

Before running CreatorOS AI, ensure the following are installed:

* Python **3.12+**
* Node.js **20+**
* npm
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/creatoros-ai.git
cd creatoros-ai
```

---

## 2. Backend Setup

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
MODEL_PROVIDER=gemini
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend will be available at:

```text
http://localhost:8000
```

---

## 3. Frontend Setup

Open another terminal.

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

Run the frontend:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🧪 Sample Run Guide

### Step 1

Open CreatorOS AI.

---

### Step 2

Click **Create New Project**.

---

### Step 3

Enter the following sample topic:

```text
Apple WWDC 2026: Top AI Features That Will Change Your iPhone
```

---

### Step 4

Configure the generation settings:

| Setting        | Value                    |
| -------------- | ------------------------ |
| AI Provider    | Gemini                   |
| Content Length | Medium                   |
| Creativity     | High                     |
| Platform       | YouTube                  |
| Tone           | Educational              |
| Audience       | General Tech Enthusiasts |

---

### Step 5

Click **Generate Pipeline**.

---

### Step 6

Watch the AI agents execute sequentially:

1. 📈 Trend Analyst
2. 🔍 Research Agent
3. ✍️ Script Writer
4. 🎨 Thumbnail Strategist
5. 🚀 SEO Specialist
6. 📅 Publishing Planner

Each stage builds upon the previous stage to create a complete content package.

---

### Step 7

Review the generated outputs, including:

* Trending content ideas
* Research outline
* Video script
* Thumbnail concepts
* SEO titles, descriptions, tags, and chapters
* Publishing checklist and promotion schedule

---

### Step 8

(Optional)

Click **Regenerate** to create an alternative version and compare the generated content.

# Future Roadmap

* Support for additional AI providers (OpenAI, Claude, etc.)
* Web search integration with citations
* Export to Markdown, PDF, and DOCX
* Direct YouTube publishing
* Team collaboration
* Performance analytics

---

# Conclusion

CreatorOS AI simplifies the YouTube content creation process by combining specialized AI agents into one intelligent workflow. From a single idea to a complete publish-ready package, it helps creators spend less time managing tools and more time creating content.

