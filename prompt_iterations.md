# Prompt Iterations

## Iteration 1

### Full Prompt

```text
Summarize this interview transcript for a recruiter. Include the topics discussed, the candidate profile, and a short candidate summary.

Transcript:
"I spent the last year working mostly in Python and SQL. We talked through an API I built for internal reporting, then discussed debugging a slow query. The interviewer also asked about communicating with product managers and how I handle unclear requirements."
```

### Sample Input Excerpt

```text
I spent the last year working mostly in Python and SQL. We talked through an API I built for internal reporting, then discussed debugging a slow query. The interviewer also asked about communicating with product managers and how I handle unclear requirements.
```

### Model Output

```text
Topics:
- Python
- SQL
- API

Profile: Backend developer, probably mid-level.

Summary: The candidate has backend experience with Python, SQL, APIs, and cross-functional collaboration.
```

### What Failed

The output was not valid JSON, and the formatting changed between sections. Topic extraction was too literal: it listed keywords instead of grouping themes like backend API development, database performance, and stakeholder communication.

### What Improved

This prompt established the basic fields needed for recruiter review.

### Why Next Iteration Was Made

The next prompt needed a strict JSON schema and clearer instructions for extracting interview themes rather than isolated keywords.

## Iteration 2

### Full Prompt

```text
You are a recruiter. Return JSON with topics_covered, profile, and candidate_summary.

Group topics into major themes. Infer the likely role and seniority. Keep the summary concise.

Transcript:
"I have used React for side projects and completed two backend internships. In the interview I explained a Flask endpoint, a PostgreSQL schema, and how I debugged a failing deployment with help from a senior engineer. I have not led a team, but I have reviewed small pull requests."
```

### Sample Input Excerpt

```text
I have used React for side projects and completed two backend internships. In the interview I explained a Flask endpoint, a PostgreSQL schema, and how I debugged a failing deployment with help from a senior engineer. I have not led a team, but I have reviewed small pull requests.
```

### Model Output

```json
{
  "topics_covered": [
    "Backend development",
    "Databases",
    "DevOps",
    "Leadership"
  ],
  "profile": {
    "role": "Full-stack engineer",
    "level": "Mid-level",
    "justification": "The candidate has React and backend experience, deployment debugging, and code review experience."
  },
  "candidate_summary": "Mid-level full-stack engineer with strong backend, database, DevOps, and leadership experience."
}
```

### What Failed

The model overstated the candidate's seniority and confidence. It treated side-project React experience as enough for a full-stack role and converted limited pull request review into leadership. The output was valid JSON, but the content was not sufficiently evidence-grounded.

### What Improved

The JSON structure was more consistent, and topic grouping was better than the first attempt.

### Why Next Iteration Was Made

The final prompt needed explicit constraints against hallucinating experience, stronger evidence requirements for role and seniority, and instructions to express uncertainty when evidence is weak.

## Iteration 3

### Full Prompt

```text
You are an experienced technical recruiter summarizing an interview transcript.

Task:
Analyze the transcript and return a concise structured summary for recruiter review.

Output rules:
- Return valid JSON only.
- Do not wrap the JSON in Markdown.
- Do not include commentary before or after the JSON.
- Use exactly this top-level schema:
  {
    "topics_covered": ["topic 1", "topic 2"],
    "profile": {
      "role": "",
      "level": "",
      "justification": ""
    },
    "candidate_summary": ""
  }
- "topics_covered" should list the major interview themes, grouped at a useful level.
- "profile.role" should infer the most likely role from evidence in the transcript.
- "profile.level" should infer likely seniority only when supported by evidence.
- "profile.justification" must cite transcript evidence in concise prose.
- "candidate_summary" should be recruiter-style: concise, useful, and evidence-based.

Reasoning constraints:
- Do not invent employment history, skills, project scope, metrics, education, or seniority.
- If evidence is weak or missing, explicitly state uncertainty in the relevant field.
- Prefer "unclear" over unsupported certainty.
- Base every claim on the transcript only.
- Keep the summary balanced and professional.

Transcript:
"""
I have used React for side projects and completed two backend internships. In the interview I explained a Flask endpoint, a PostgreSQL schema, and how I debugged a failing deployment with help from a senior engineer. I have not led a team, but I have reviewed small pull requests.
"""
```

### Sample Input Excerpt

```text
I have used React for side projects and completed two backend internships. In the interview I explained a Flask endpoint, a PostgreSQL schema, and how I debugged a failing deployment with help from a senior engineer. I have not led a team, but I have reviewed small pull requests.
```

### Model Output

```json
{
  "topics_covered": [
    "Backend API development with Flask",
    "Database schema design with PostgreSQL",
    "Deployment debugging with senior support",
    "Limited frontend exposure through React side projects",
    "Early code review and collaboration experience"
  ],
  "profile": {
    "role": "Backend engineer",
    "level": "Junior or early-career; exact seniority unclear",
    "justification": "The transcript mentions two backend internships, discussion of a Flask endpoint and PostgreSQL schema, and deployment debugging with help from a senior engineer. React experience is described only as side projects, and the candidate explicitly says they have not led a team."
  },
  "candidate_summary": "The candidate appears strongest in early-career backend engineering, with interview evidence around Flask APIs, PostgreSQL schema work, and deployment debugging. They have some frontend exposure through React side projects and limited code review experience, but the transcript does not support confident mid-level or leadership claims."
}
```

### What Failed

No major structural issue remained. The prompt is longer than the earlier versions, but the added constraints are useful for reducing unsupported claims.

### What Improved

The model grouped topics thematically, avoided overstating full-stack depth, and handled seniority with appropriate uncertainty. The summary became more useful for recruiter screening because it separated evidence from inference.

### Why Next Iteration Was Made

This became the final prompt used in the implementation because it satisfied the schema, grounded inference, uncertainty handling, and recruiter-style summary requirements.
