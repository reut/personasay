# PersonaSay Personas Configuration

This directory contains AI persona definitions used by PersonaSay.

## Files in This Directory

- **`persona_template.json`** (tracked in git) - Template for creating new personas
- **`*_enhanced.json`** (gitignored) - Your actual persona files (private customizations)

## Current Status

**Important**: The default persona files (`alex_enhanced.json`, `nina_enhanced.json`, etc.) are currently **tracked in git** but should be **gitignored** for security and privacy.

### Why Remove Them from Git?

1. **Privacy**: Personas may contain company-specific information
2. **Customization**: Each installation should create their own personas
3. **Best Practice**: Configuration files with specific details should be private

### Migration Steps (One Time)

If you want to remove the existing personas from git history and make them private:

```bash
# Remove from git tracking (keeps local files)
git rm --cached backend/app/personas/*_enhanced.json

# Commit the removal
git commit -m "Remove persona files from git tracking (now gitignored)"

# The files remain on your local system but won't be pushed to git
```

After this, the `.gitignore` rules will prevent future persona files from being tracked.

### Alternative: Keep Example Personas

If you want to keep example personas in the repo for reference:

1. Rename them to `*_example.json` (e.g., `alex_example.json`)
2. Update `.gitignore` to allow `*_example.json` files
3. Users copy examples and customize them

## Creating New Personas

### Quick Start

```bash
# 1. Copy the template
cp backend/app/personas/persona_template.json backend/app/personas/sarah_analyst.json

# 2. Edit with your persona details
nano backend/app/personas/sarah_analyst.json

# 3. Remove the _README and _SETUP sections from the top

# 4. Fill in all [bracketed placeholders] with your specific content
```

### Template Structure

The template includes these main sections:

1. **Basic Info**: id, name, role, company, description
2. **Empathy Map**: think_and_feel, hear, see, say_and_do, pain, gain
3. **Career History**: Previous roles, achievements, defining experiences
4. **Industry Awareness**: Market trends, competitors, vendors, regulations
5. **Organizational Context**: Reports to, stakeholders, team structure, budget
6. **Communication Patterns**: Tone, terminology, question patterns, storytelling
7. **Incentives & Motivations**: KPIs, career risks/gains, decision drivers
8. **Response Rules**: How the persona generates responses

### Best Practices

#### 1. Be Specific with Numbers

Bad: "Manages a team"  
Good: "Manages 25 traders across 3 regions with $3.2M annual budget"

#### 2. Include Real Constraints

Bad: "Needs approval for big purchases"  
Good: "Can approve up to $25K solo; above that requires CFO sign-off"

#### 3. Use Domain Terminology

Bad: "Works with data providers"  
Good: "Evaluates odds feed providers like Betradar, LSports, BetGenius for coverage and latency"

#### 4. Show Career Experience

Bad: "Has experience in the industry"  
Good: "9 years in sports betting operations. Previously led provider consolidation that saved $400K annually"

#### 5. Define Clear Pain Points

Bad: "System outages are frustrating"  
Good: "Provider outages cost $50K-$100K per incident and hurt my 20% performance bonus"

#### 6. Include Stakeholder Dynamics

Bad: "Reports to management"  
Good: "Reports to COO Sarah. CFO David constantly pressures to cut 20% from provider spend. Weekly 1:1s to justify costs."

## Example Personas Included

The repo includes 7 example personas from **sports betting industry**:

| Persona | Role | Focus Areas |
|---------|------|-------------|
| Alex | Trading Manager | Operations, costs, reliability, team management |
| Ben | Performance Analyst | Data analysis, ROI, reporting, optimization |
| Clara | Risk & Trading Ops | Risk management, margin analysis, real-time monitoring |
| John | Customer Support Lead | Incident response, reliability, customer satisfaction |
| Marco | VP Commercial Strategy | Business strategy, ROI, competitive positioning |
| Nina | Product Owner | User experience, feature prioritization, roadmap |
| Rachel | In-Play Trader | Real-time trading, latency, live event management |

**These are examples only** - showing the level of detail needed. You should create personas relevant to your product and industry.

## How Personas Are Used

### 1. LangChain Agents

Each persona becomes an independent LangChain agent that:
- Loads persona details into system prompts
- Uses empathy map to understand user perspective
- References career history for credibility
- Applies communication patterns for authentic voice
- Follows response generation rules for consistency

### 2. Empathy-Driven Responses

Personas don't just "know facts" - they have:
- **Pain points** that make them passionate about certain issues
- **Gains** that motivate their priorities
- **KPIs** that drive their decision criteria
- **Stakeholders** they need to satisfy
- **Budget constraints** that limit their options
- **Career risks** that make them cautious

### 3. Authentic Communication

Each persona has unique:
- Sentence starters and qualifiers
- Domain terminology and jargon level
- Question patterns (clarifying, probing, validating)
- Storytelling style with anecdotes
- Tone variations (excited, skeptical, analytical)

## File Naming Convention

- **Template**: `persona_template.json`
- **Your personas**: `[firstname]_[role].json` or `[firstname]_enhanced.json`
- **Examples** (if keeping): `[firstname]_example.json`

## Troubleshooting

### "Persona responses feel generic"

**Solution**: Add more specific details:
- Include exact numbers, budgets, team sizes
- Reference specific tools, vendors, competitors
- Define clear KPIs with targets and current performance
- Add defining experiences with impact and lessons learned

### "All personas sound the same"

**Solution**: Differentiate their focus areas:
- Each persona should have unique `decision_drivers_ranked`
- Different `pain` and `gain` priorities
- Distinct `communication_patterns` and terminology
- Varied stakeholder relationships

### "Personas don't reference their constraints"

**Solution**: Ensure you've defined:
- `budget_authority` with specific approval limits
- `decision_making_authority` with what they can/can't decide
- `key_stakeholders` with relationship dynamics
- `kpis_and_targets` with bonus implications

## Related Documentation

- [CUSTOMIZATION_GUIDE](../../../docs/CUSTOMIZATION_GUIDE.md) - Full customization instructions
- [Backend Config README](../../config/README.md) - Overall configuration guide
- [Main README](../../../README.md) - Project overview

## Support

For questions about creating effective personas:
- Review the `persona_template.json` file - it has extensive inline guidance
- Examine the example personas to see the level of detail
- Open a GitHub issue with the `personas` label

---

**Remember**: Great personas are specific, authentic, and constrained by real-world organizational dynamics!
