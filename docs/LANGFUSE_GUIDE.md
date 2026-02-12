# Langfuse Integration Guide for PersonaSay

This guide explains how to use Langfuse observability in PersonaSay to track, evaluate, and optimize your persona responses.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Features](#features)
5. [Dashboard Usage](#dashboard-usage)
6. [Cost Tracking](#cost-tracking)
7. [Quality Evaluation](#quality-evaluation)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Langfuse provides comprehensive observability for PersonaSay's LangChain-based persona system. It automatically tracks:

- **Every LLM call** with full context
- **Token usage and costs** per persona and feature
- **Latency** for each persona response
- **User feedback** (thumbs up/down)
- **Quality scores** from automated evaluators
- **Session grouping** to track conversations

---

## Quick Start

### Option 1: Langfuse Cloud (Recommended)

1. **Sign up** at [https://cloud.langfuse.com](https://cloud.langfuse.com)
2. **Create a project** in the Langfuse dashboard
3. **Get your API keys**:
   - Go to Settings → API Keys
   - Copy your Public Key and Secret Key
4. **Add keys to PersonaSay**:
   ```bash
   cd backend
   nano .env
   ```
   Add:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
   LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
   LANGFUSE_ENABLED=true
   ```
5. **Restart the backend**:
   ```bash
   python main.py
   ```
6. **Start chatting** - traces will appear in Langfuse automatically!

### Option 2: Self-Hosted Langfuse

1. **Add Langfuse to docker-compose** (see [Self-Hosted Setup](#self-hosted-setup))
2. **Start services**:
   ```bash
   docker compose up -d
   ```
3. **Access Langfuse** at `http://localhost:3000`
4. **Create account** and get API keys
5. **Configure PersonaSay** with your self-hosted URL:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-your-key
   LANGFUSE_SECRET_KEY=sk-lf-your-key
   LANGFUSE_HOST=http://localhost:3000
   LANGFUSE_ENABLED=true
   ```

---

## Configuration

### Environment Variables

All Langfuse configuration is in `backend/.env`:

```bash
# Enable/disable Langfuse tracing
LANGFUSE_ENABLED=true

# Langfuse Cloud (default)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Self-Hosted
# LANGFUSE_HOST=http://localhost:3000
```

### Disabling Langfuse

To temporarily disable tracing without removing keys:

```bash
LANGFUSE_ENABLED=false
```

Or remove the langfuse package:

```bash
pip uninstall langfuse
```

PersonaSay will continue working normally without Langfuse.

---

## Features

### 1. Automatic Tracing

Every persona response is automatically traced with:

- **Full prompt** sent to OpenAI
- **Complete response** from the model
- **Token counts** (prompt + completion)
- **Cost** calculated from token usage
- **Latency** in milliseconds
- **Model used** (gpt-4o, gpt-4o-mini, etc.)

**Example trace metadata:**
```json
{
  "persona_id": "alex",
  "persona_name": "Alex",
  "persona_role": "Head of Trading",
  "persona_company": "BetMax",
  "feature": "chat",
  "generate_mock": false
}
```

### 2. Session Grouping

All messages in a conversation are grouped by `session_id`:

- **Chat conversations**: Grouped by auto-generated session ID
- **Debates**: Grouped by `debate_id`
- **Multi-round debates**: All rounds share the same session

**View in Langfuse:**
- Go to Traces → Filter by Session ID
- See the full conversation flow across multiple personas

### 3. Feature Tagging

Every trace is tagged with the feature used:

- `chat` - Standard persona conversations
- `debate` - Multi-persona debates
- `summary` - AI-generated summaries

**Filter by feature:**
- Langfuse Dashboard → Traces → Filter by Tag → Select "chat", "debate", or "summary"

### 4. User Feedback

Thumbs up/down buttons in the UI send feedback to Langfuse:

- **Thumbs up** = score of 1.0
- **Thumbs down** = score of 0.0
- Feedback is linked to the specific trace
- Visible in Langfuse Dashboard → Scores

**How it works:**
1. User clicks 👍 or 👎 on a persona response
2. Frontend sends POST to `/feedback` with `trace_id` and `score`
3. Backend logs score to Langfuse
4. Score appears in Langfuse dashboard immediately

### 5. Quality Evaluators

Automated quality checks run on every response:

- **Response Length**: 150-250 words is optimal
- **Empathy Compliance**: Checks for empathy framework keywords
- **Role Consistency**: Validates role-specific terminology
- **Specificity**: Measures concrete examples vs generic statements

**View evaluator scores:**
- Langfuse Dashboard → Traces → Select a trace → Scores tab

---

## Dashboard Usage

### Key Views in Langfuse

#### 1. Traces View

**What it shows:** Every LLM call with full details

**How to use:**
- Filter by persona: `metadata.persona_id = "alex"`
- Filter by feature: Tag = "chat" or "debate"
- Filter by session: `session_id = "abc-123"`
- Sort by cost, latency, or timestamp

**Useful queries:**
```
# Find expensive traces
cost > 0.01

# Find slow personas
latency > 5000

# Find errors
status = "error"

# Find specific persona
metadata.persona_name = "Alex"
```

#### 2. Sessions View

**What it shows:** Grouped conversations

**How to use:**
- Click on a session to see all traces in that conversation
- See total cost and latency for the entire conversation
- View user feedback aggregated by session

#### 3. Scores View

**What it shows:** All user feedback and evaluator scores

**How to use:**
- Filter by score name: "user_feedback", "response_length", etc.
- See average scores per persona
- Identify best/worst performing personas

#### 4. Dashboard View

**What it shows:** High-level metrics and charts

**Key metrics:**
- Total traces
- Total cost
- Average latency
- Error rate
- User feedback distribution

---

## Cost Tracking

### Understanding Costs

PersonaSay makes multiple OpenAI calls per request:

**Chat with 3 personas:**
- 3 LLM calls (one per persona)
- Cost: ~$0.01 - $0.03 per conversation

**Debate (5 rounds, 3 personas):**
- 15 LLM calls (3 personas × 5 rounds)
- Cost: ~$0.05 - $0.15 per debate

**Summary:**
- 1 LLM call
- Cost: ~$0.005 - $0.01 per summary

### Cost Optimization Tips

1. **Use fewer personas** for quick questions
2. **Limit debate rounds** to 3-5 rounds
3. **Disable mock generation** unless needed (adds 1 call per persona)
4. **Use gpt-4o-mini** for less critical responses (10x cheaper)

### Setting Up Cost Alerts

In Langfuse Dashboard:

1. Go to Settings → Alerts
2. Create alert: "Daily cost > $10"
3. Add email notification
4. Save

You'll receive an email if daily costs exceed the threshold.

---

## Quality Evaluation

### Automated Evaluators

PersonaSay includes 4 built-in evaluators:

#### 1. Response Length Evaluator

**Checks:** Word count is 150-250 words

**Scoring:**
- 1.0 = 150-250 words (optimal)
- 0.8 = 100-149 or 251-300 words (acceptable)
- 0.5 = <100 or >300 words (too short/long)

#### 2. Empathy Compliance Evaluator

**Checks:** Presence of empathy framework keywords

**Scoring:**
- 1.0 = 3+ dimensions present (thinks, feels, sees, says/does)
- 0.8 = 2 dimensions
- 0.6 = 1 dimension
- 0.4 = No empathy markers

#### 3. Role Consistency Evaluator

**Checks:** Role-specific terminology usage

**Scoring:**
- 1.0 = 30%+ of role keywords present
- 0.8 = 20-29% present
- 0.6 = 10-19% present
- 0.4 = <10% present

#### 4. Specificity Evaluator

**Checks:** Concrete examples vs generic statements

**Scoring:**
- 1.0 = 3+ specificity indicators (numbers, examples, names, etc.)
- 0.8 = 2 indicators
- 0.6 = 1 indicator
- 0.4 = No specific indicators

### Viewing Quality Scores

1. Go to Langfuse Dashboard → Traces
2. Select a trace
3. Click "Scores" tab
4. See all evaluator scores with details

### Creating Custom Evaluators

You can add your own evaluators in `backend/app/evaluators.py`:

```python
def evaluate_custom_metric(response: str) -> Dict[str, Any]:
    """Your custom evaluation logic"""
    score = 1.0  # Your scoring logic
    return {
        "score": score,
        "status": "good",
        "details": {}
    }
```

Then call it in `langchain_personas.py` after generating a response.

---

## Advanced Features

### Persona Performance Comparison

**Query to compare personas:**

1. Go to Langfuse → Traces
2. Group by: `metadata.persona_name`
3. Aggregate: Average of `user_feedback` score
4. Sort by score descending

**Result:** See which personas get the most positive feedback.

### Cost Per Persona

**Query:**

1. Go to Langfuse → Traces
2. Group by: `metadata.persona_id`
3. Aggregate: Sum of `cost`
4. Sort by cost descending

**Result:** Identify most expensive personas.

### Feature Usage Analytics

**Query:**

1. Go to Langfuse → Traces
2. Group by: `metadata.feature`
3. Aggregate: Count
4. Chart type: Pie chart

**Result:** See which features are used most (chat vs debate vs summary).

---

## Self-Hosted Setup

### Adding Langfuse to docker-compose.yml

Add these services to your `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  langfuse-db:
    image: postgres:15
    environment:
      POSTGRES_DB: langfuse
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: langfuse_password_change_me
    volumes:
      - langfuse-db-data:/var/lib/postgresql/data
    networks:
      - personasay-network

  langfuse:
    image: langfuse/langfuse:latest
    depends_on:
      - langfuse-db
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://langfuse:langfuse_password_change_me@langfuse-db:5432/langfuse
      NEXTAUTH_SECRET: change_this_to_a_random_string
      NEXTAUTH_URL: http://localhost:3000
      SALT: change_this_to_another_random_string
    networks:
      - personasay-network

volumes:
  langfuse-db-data:
```

### Starting Self-Hosted Langfuse

```bash
docker compose up -d
```

### Accessing Self-Hosted Langfuse

1. Open `http://localhost:3000`
2. Create an account
3. Create a project
4. Get API keys from Settings → API Keys
5. Add keys to `backend/.env`:
   ```bash
   LANGFUSE_HOST=http://langfuse:3000
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   ```

---

## Troubleshooting

### Traces Not Appearing

**Check 1: Is Langfuse enabled?**
```bash
cat backend/.env | grep LANGFUSE_ENABLED
# Should show: LANGFUSE_ENABLED=true
```

**Check 2: Are API keys configured?**
```bash
cat backend/.env | grep LANGFUSE_PUBLIC_KEY
# Should show your key
```

**Check 3: Check backend logs**
```bash
tail -f backend/logs/personasay.log | grep -i langfuse
```

**Check 4: Test feedback endpoint**
```bash
curl http://localhost:8001/feedback/health
```

Should return:
```json
{
  "langfuse_available": true,
  "langfuse_enabled": true,
  "langfuse_configured": true,
  "status": "ready"
}
```

### Feedback Buttons Not Working

**Check 1: Does message have trace_id?**

In browser console:
```javascript
// Check if messages have trace_id
console.log(chatHistory.filter(m => !m.isUser && !m.trace_id))
// Should be empty array
```

**Check 2: Check network requests**

Open browser DevTools → Network tab → Send feedback → Check for POST to `/feedback`

**Check 3: Backend logs**
```bash
tail -f backend/logs/personasay.log | grep feedback
```

### High Costs

**Check 1: How many personas are active?**

Fewer personas = lower cost. Use 2-3 personas for quick questions.

**Check 2: Is mock generation enabled?**

Mock generation adds 1 extra LLM call per persona. Disable if not needed.

**Check 3: Check token usage**

In Langfuse Dashboard:
- Go to Traces
- Sort by tokens descending
- Identify traces with high token counts
- Optimize prompts or reduce context

### Slow Responses

**Check 1: Check latency in Langfuse**

- Go to Traces → Sort by latency descending
- Identify slow personas

**Check 2: Check if running sequentially**

PersonaSay runs personas concurrently, but if you see sequential timing, check the `get_all_responses` implementation.

**Check 3: Network latency**

Self-hosted Langfuse should be faster than cloud. Check if network is the bottleneck.

---

## Best Practices

### 1. Use Sessions Consistently

Always pass `session_id` to group related conversations:

```python
responses = await manager.get_all_responses(
    ...,
    session_id=session_id,  # ← Important!
    ...
)
```

### 2. Add Meaningful Metadata

Include context in trace metadata:

```python
trace_metadata = {
    "user_id": user_id,
    "conversation_topic": topic,
    "experiment_variant": "A",
}
```

### 3. Monitor Costs Daily

Set up cost alerts in Langfuse to avoid surprises.

### 4. Review Feedback Weekly

Check user feedback scores to identify:
- Best performing personas
- Worst performing personas
- Common issues

### 5. Use Evaluators for Quality Gates

Set minimum quality thresholds:

```python
if overall_score < 0.6:
    logger.warning(f"Low quality response: {overall_score}")
    # Optionally regenerate or flag for review
```

---

## FAQ

**Q: Does Langfuse slow down responses?**

A: No. Langfuse logging is async and non-blocking. It adds <10ms overhead.

**Q: Can I use Langfuse in production?**

A: Yes! Langfuse is production-ready and used by many companies.

**Q: How much does Langfuse Cloud cost?**

A: Free tier: 50K events/month. Pro: $59/month for 500K events. See [langfuse.com/pricing](https://langfuse.com/pricing)

**Q: Can I export data from Langfuse?**

A: Yes. Langfuse supports data export via API or CSV download.

**Q: Does Langfuse store my prompts and responses?**

A: Yes, Langfuse stores full traces including prompts and responses. Use self-hosted if you need full data control.

**Q: Can I delete traces?**

A: Yes. In Langfuse Dashboard → Traces → Select trace → Delete.

**Q: How long does Langfuse keep data?**

A: Cloud: 30 days on free tier, longer on paid plans. Self-hosted: You control retention.

---

## Resources

- **Langfuse Documentation**: [https://langfuse.com/docs](https://langfuse.com/docs)
- **Langfuse GitHub**: [https://github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)
- **PersonaSay Issues**: [GitHub Issues](https://github.com/yourusername/personasay/issues)

---

## Support

For Langfuse-specific issues:
- Langfuse Discord: [https://discord.gg/7NXusRtqYU](https://discord.gg/7NXusRtqYU)
- Langfuse Support: support@langfuse.com

For PersonaSay integration issues:
- Open an issue on GitHub
- Check backend logs: `backend/logs/personasay.log`

---

*Last updated: 2026-02-06*
