<p align="center">
  <img src="logo.webp" alt="Barmuda" width="72" />
</p>

<h1 align="center">Barmuda</h1>

<p align="center"><b>People hate filling out forms. So we made surveys that feel like texting.</b></p>

<p align="center">
  <code>● Live</code> &nbsp;·&nbsp; <a href="https://barmuda.in"><b>barmuda.in</b></a> &nbsp;·&nbsp; Flask · Firebase · LLM
</p>

![Barmuda landing page](preview.png)

> Same questions, delivered one at a time as a chat instead of a wall of fields. People actually finish, so you collect more responses and better ones.

Paste in your questions, get a link. Your respondents chat with an AI one question at a time, like texting a friend, and you still get clean structured data back as CSV.

## Why it exists

Static forms quietly leak responses. People see 20 questions, feel the work coming, and bail. A 10% completion rate is a good day. Barmuda flips the format so finishing feels effortless. Think infinite user interviewers, one prompt away.

## How it works

```
Paste questions  →  AI builds the survey  →  Share link  →  People chat  →  CSV + dashboard
```

| Step | What happens |
|------|--------------|
| **1. Paste** | Drop in questions from Google Forms, a doc, or your head. The AI infers a structured survey, question types and all. |
| **2. Share** | You get one link. Works on any device. |
| **3. Chat** | The AI asks one question at a time and adapts to each reply, assembling structured answers in the background. |
| **4. Collect** | Export to CSV, and read responses in a dashboard with charts and word clouds. |

## What you get

| Feature | What it does |
|---------|--------------|
| **Chat, not forms** | Feels like texting, not homework |
| **Paste to survey** | AI writes the questions from your raw text |
| **CSV export** | Standard format, no surprises |
| **Dashboard** | Charts and word clouds over every response |
| **Voice mode** | Respondents can answer out loud |
| **Templates** | User interviews, discovery, churn, pricing, and more |

## Under the hood

Flask · Firebase (Google auth + Firestore) · an LLM layer that both infers the survey from your text and runs the live conversations · deployed on Vercel. Real product with usage-based pricing, since every conversation costs API money.
