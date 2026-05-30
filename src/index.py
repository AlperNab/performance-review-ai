#!/usr/bin/env python3
"""
performance-review-ai — manager notes + peer feedback → structured performance review
Generates: ratings, narrative paragraphs, development plan, SMART goals,
calibration summary, promotion readiness assessment
"""
import anthropic, json, re, sys
from pathlib import Path

SYSTEM = """You are a senior HR business partner and talent development specialist.
Transform raw manager observations and peer feedback into a structured, fair, actionable performance review.

Principles:
- Evidence-based: tie every rating to specific examples
- Balanced: acknowledge strengths genuinely, frame improvements constructively
- Forward-looking: development plan should be specific and achievable
- Bias-aware: flag any language that suggests potential bias
- Use SBI format for feedback (Situation-Behavior-Impact)

Return ONLY valid JSON — no markdown, no explanation.

{
  "employee_name": "string or 'Employee'",
  "role": "string or null",
  "review_period": "string or null",
  "reviewer": "string or null",
  "overall_rating": number_1_to_5,
  "overall_rating_label": "Exceptional|Exceeds Expectations|Meets Expectations|Needs Improvement|Unsatisfactory",
  "ratings": {
    "job_performance": {"score":number_1_to_5,"rationale":"evidence-based explanation"},
    "collaboration": {"score":number_1_to_5,"rationale":"string"},
    "communication": {"score":number_1_to_5,"rationale":"string"},
    "initiative": {"score":number_1_to_5,"rationale":"string"},
    "problem_solving": {"score":number_1_to_5,"rationale":"string"},
    "reliability": {"score":number_1_to_5,"rationale":"string"},
    "growth_mindset": {"score":number_1_to_5,"rationale":"string"}
  },
  "narrative": {
    "overall_summary": "3-4 sentence summary balancing strengths and growth areas",
    "key_achievements": "paragraph highlighting 2-3 specific accomplishments with impact",
    "areas_for_growth": "constructive paragraph — SBI format, no blame language",
    "collaboration_feedback": "paragraph synthesizing peer feedback themes"
  },
  "strengths": ["top 3-4 genuine strengths with brief evidence"],
  "development_areas": ["2-3 specific, actionable areas"],
  "development_plan": [
    {
      "area": "skill or behavior to develop",
      "current_state": "where they are now",
      "target_state": "specific measurable outcome",
      "actions": ["concrete steps to take"],
      "resources": ["training|mentorship|project|reading"],
      "timeline": "Q1 2026|6 months|...",
      "success_metric": "how we'll know it's improved"
    }
  ],
  "smart_goals_next_period": [
    {
      "goal": "full SMART goal statement",
      "specific": "what exactly",
      "measurable": "how measured",
      "achievable": "why realistic",
      "relevant": "why it matters",
      "time_bound": "deadline"
    }
  ],
  "promotion_readiness": {
    "ready": "yes|not_yet|no",
    "timeline": "now|6_months|12_months|24_months|not_applicable",
    "gaps_to_address": ["what needs to happen first"],
    "rationale": "one paragraph explanation"
  },
  "calibration_summary": "2-3 sentences suitable for a calibration meeting",
  "bias_flags": ["any language or patterns in input that may indicate bias"],
  "manager_coaching_notes": ["private notes for the manager's own development"],
  "confidence": 0.0
}"""

def generate_review(
    manager_notes: str,
    peer_feedback: list[str] | None = None,
    role: str = "",
    employee_name: str = "",
    review_period: str = ""
) -> dict:
    client = anthropic.Anthropic()
    context_parts = [
        f"Employee: {employee_name}" if employee_name else "",
        f"Role: {role}" if role else "",
        f"Review period: {review_period}" if review_period else "",
        f"\nManager notes:\n{manager_notes}"
    ]
    if peer_feedback:
        context_parts.append(f"\nPeer feedback:\n" + "\n---\n".join(peer_feedback))
    context = "\n".join(p for p in context_parts if p)

    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=4096, system=SYSTEM,
        messages=[{"role":"user","content":f"Generate a performance review from:\n\n{context}"}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

STARS = {1:"★☆☆☆☆",2:"★★☆☆☆",3:"★★★☆☆",4:"★★★★☆",5:"★★★★★"}
RATING_LABELS = {1:"Unsatisfactory",2:"Needs Improvement",3:"Meets Expectations",4:"Exceeds",5:"Exceptional"}

def print_review(r: dict):
    overall = r.get("overall_rating",3)
    print(f"\n{'═'*60}")
    print(f"  PERFORMANCE REVIEW — {r.get('employee_name','Employee')}")
    print(f"  {r.get('role','')} | {r.get('review_period','')}")
    print(f"  Overall: {STARS.get(overall,'')} {r.get('overall_rating_label','')}")
    print(f"{'═'*60}")

    narrative = r.get("narrative",{})
    if narrative.get("overall_summary"):
        print(f"\n  {narrative['overall_summary']}")

    ratings = r.get("ratings",{})
    if ratings:
        print(f"\n  Ratings:")
        for k,v in ratings.items():
            score = v.get("score",3)
            bar = "█"*score + "░"*(5-score)
            print(f"  {k.replace('_',' '):<22} {bar} {score}/5")

    if narrative.get("key_achievements"):
        print(f"\n  Achievements:\n  {narrative['key_achievements'][:300]}")
    if narrative.get("areas_for_growth"):
        print(f"\n  Growth areas:\n  {narrative['areas_for_growth'][:300]}")

    dev_plan = r.get("development_plan",[])
    if dev_plan:
        print(f"\n{'─'*60}\n  DEVELOPMENT PLAN")
        for d in dev_plan:
            print(f"\n  📌 {d.get('area','')}")
            print(f"     Target: {d.get('target_state','')}")
            print(f"     Timeline: {d.get('timeline','')} | Metric: {d.get('success_metric','')}")
            for action in d.get("actions",[])[:3]: print(f"     → {action}")

    goals = r.get("smart_goals_next_period",[])
    if goals:
        print(f"\n{'─'*60}\n  SMART GOALS NEXT PERIOD")
        for goal in goals:
            print(f"\n  🎯 {goal.get('goal','')}")

    promo = r.get("promotion_readiness",{})
    if promo.get("ready"):
        print(f"\n  Promotion readiness: {promo.get('ready','?').upper()} ({promo.get('timeline','?')})")
        if promo.get("gaps_to_address"):
            print(f"  Gaps: {', '.join(promo['gaps_to_address'][:2])}")

    print(f"\n  Calibration: {r.get('calibration_summary','')}")

    bias_flags = r.get("bias_flags",[])
    if bias_flags:
        print(f"\n  ⚠ Bias flags:")
        for b in bias_flags: print(f"  ! {b}")
    print(f"\n  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate performance review from manager notes")
    p.add_argument("notes", help="Manager notes file or '-' for stdin")
    p.add_argument("--peer", nargs="+", help="Peer feedback files")
    p.add_argument("--role", default="")
    p.add_argument("--name", default="")
    p.add_argument("--period", default="")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    notes = Path(a.notes).read_text(encoding="utf-8",errors="replace") if Path(a.notes).exists() else sys.stdin.read()
    peers = [Path(pf).read_text(encoding="utf-8",errors="replace") for pf in (a.peer or []) if Path(pf).exists()]

    r = generate_review(notes, peers or None, a.role, a.name, a.period)
    if a.json: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_review(r)
