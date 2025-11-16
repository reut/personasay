# Customization Guide: Make PersonaSay Your Own

PersonaSay is an **open-source, customizable AI persona chat framework**. While the default configuration showcases sports betting analytics (LSports BOOST), you can easily adapt it to **any industry or product**.

---

## Quick Start: 3 Steps to Customize

### **1. Define Your Product Context**

**Primary Location (Recommended):** `backend/config/product_config.py`

This is the **single source of truth** for product information. The backend owns product configuration and serves it to the frontend via API.

```python
# Basic Identity
PRODUCT_NAME = "Your Product Name"
PRODUCT_SHORT_NAME = "YourProduct"
PRODUCT_TAGLINE = "Your compelling tagline"
PRODUCT_INDUSTRY = "Your Industry"

# Full Product Context
PRODUCT_DESCRIPTION = """
What does your product do? 
Who is it for?
What problems does it solve?
"""

TARGET_USERS = [
    "User Type 1 (e.g., Data Analysts)",
    "User Type 2 (e.g., Product Managers)",
    # Add 3-6 user types
]

KEY_FEATURES = [
    "Feature 1: Description",
    "Feature 2: Description",
    # List 5-10 key features
]

PAIN_POINTS = [
    "Problem your product solves",
    "Another pain point",
    # List 5-10 pain points
]

VALUE_PROPOSITION = "Your clear value proposition in 1-2 sentences"

TECHNICAL_CONTEXT = "Brief technical overview for AI context"
```

**Alternative:** You can also edit `frontend/src/config/product.config.ts` for frontend-only customization, but backend is the recommended source of truth.

**Tips:**
- Be **specific** about your industry and users
- Use **concrete examples** rather than generic terms
- Include **technical details** that help AI understand your domain
- Backend config is accessible via `GET /product/config` API endpoint

---

### **2. Create Your Personas**

Edit: `frontend/src/config/personas.config.ts`

Each persona represents a **target user** of your product. Use the **empathy map structure** to give AI rich understanding:

```typescript
{
  id: "john-analyst",
  name: "John Smith",
  title: "Senior Data Analyst",
  company: "Your Company Type",
  avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
  role: "Data Analyst (Your Product)",
  person_perspective: "As a data analyst, I need [X] so that I can [Y]",
  
  empathy_map: {
    think_and_feel: [
      "I'm worried about [concern]",
      "I need to [priority]",
      "I feel [emotion] when [situation]"
    ],
    see: [
      "I observe [behavior] in my workflow",
      "I notice [problem] daily"
    ],
    hear: [
      "From my manager: '[quote]'",
      "From customers: '[feedback]'"
    ],
    say_and_do: [
      "I check [tool] multiple times daily",
      "I create [deliverable] weekly"
    ],
    pain: [
      "It's difficult to [challenge]",
      "I waste time on [manual task]"
    ],
    gain: [
      "I want to achieve [goal]",
      "Success for me means [outcome]"
    ]
  }
}
```

**Best Practices:**
- **3-7 personas** is ideal (more = diluted focus)
- **3-6 items** per empathy map field
- Use **real quotes** and **specific scenarios**
- Mix **user levels** (junior, senior, executive)
- Include **different roles** that use your product

**Empathy Map Guide:**

| Field | What to Include | Example (Sports Betting) |
|-------|-----------------|-------------------------|
| **think_and_feel** | Internal thoughts, emotions, concerns | "I worry about coverage gaps during high-stakes events" |
| **see** | What they observe in their environment | "Multiple dashboards with inconsistent metrics" |
| **hear** | What colleagues/managers/customers tell them | "From management: 'Why are we paying so much for Provider X?'" |
| **say_and_do** | Their actions, behaviors, daily tasks | "Check provider dashboards multiple times daily" |
| **pain** | Problems, frustrations, obstacles | "Too much time spent manually collecting data" |
| **gain** | Goals, desires, success metrics | "Single dashboard showing all providers in real-time" |

---

### **3. Configure Mock Generation Context**

**Primary Location (Recommended):** `backend/config/product_config.py`

This helps AI generate **relevant visual mocks** (SVG diagrams) for your domain:

```python
MOCK_GENERATION_CONTEXT = {
    "domain": "Your industry domain keywords",
    "requirements": [
        "Content MUST be relevant to: [your keywords]",
        "Include: [specific metrics, data types, entities]",
        "Make it [visual style description]",
        "NO placeholder text—show realistic [your data]"
    ],
    "example_sports": ["Entity Type 1", "Entity Type 2"],      # e.g., "SaaS Companies", "Healthcare Providers"
    "example_leagues": ["Example 1", "Example 2"],             # e.g., "Fortune 500", "SMBs"
    "example_providers": ["Tool A", "Tool B"],                 # e.g., "Salesforce", "HubSpot"
    "example_metrics": ["Metric 1", "Metric 2"]                # e.g., "Conversion Rate", "Churn %"
}
```

**Alternative:** You can also configure this in `frontend/src/config/product.config.ts`, but backend is the recommended source of truth.

---

## Customization Examples

### Example 1: SaaS Analytics Platform

```typescript
// product.config.ts
export const productContext = {
  name: "MetricFlow",
  tagline: "Unify Your SaaS Metrics Across All Tools",
  industry: "SaaS Analytics & Business Intelligence",
  target_users: ["Product Managers", "Growth Teams", "Data Analysts"],
  key_features: ["Cross-platform data aggregation", "Custom dashboards", "Predictive analytics"],
  // ... etc
};

// personas.config.ts
{
  id: "sarah-pm",
  name: "Sarah Johnson",
  title: "Senior Product Manager",
  role: "Product Manager (MetricFlow)",
  person_perspective: "As a PM, I need unified metrics to make data-driven product decisions",
  empathy_map: {
    think_and_feel: [
      "I'm responsible for hitting OKRs but data is scattered",
      "I worry about making decisions based on incomplete data"
    ],
    see: ["10+ dashboards across Mixpanel, Amplitude, GA4"],
    hear: ["From CEO: 'What's our actual conversion rate?'"],
    // ... etc
  }
}
```

### Example 2: Healthcare Patient Management

```typescript
// product.config.ts
export const productContext = {
  name: "CareSync",
  tagline: "Coordinate Patient Care Across Providers",
  industry: "Healthcare IT & Patient Management",
  target_users: ["Physicians", "Nurses", "Care Coordinators"],
  // ... etc
};

// personas.config.ts
{
  id: "dr-patel",
  name: "Dr. Anita Patel",
  title: "Primary Care Physician",
  role: "Physician (CareSync)",
  empathy_map: {
    think_and_feel: ["I need complete patient history instantly during appointments"],
    see: ["Fragmented patient records across 3 different EMR systems"],
    pain: ["Critical patient info is in a different system I can't access"],
    // ... etc
  }
}
```

---

## Advanced Customization

### Update App.tsx to Use Config

Edit: `frontend/src/App.tsx`

```typescript
// Replace hardcoded data with imports
import { productContext } from './config/product.config';
import { personasData } from './config/personas.config';

// The rest of your App.tsx stays the same!
```

### Customize Backend Mock Prompts

Edit: `backend/app/server.py`

Search for `svg_prompt` variables and update the context:

```python
svg_prompt = f"""You are a UX designer creating a professional SVG mock/wireframe.

CONTEXT: This is for {product_name}, a {product_industry} platform. {product_description}

Persona: {persona['name']} - {persona['title']}
Question: "{question}"
Domain: "{your_domain_keywords}"

Requirements:
- Content MUST be relevant to: {your_key_topics}
- Include: {your_specific_metrics}
- Make it visually rich, professional, mature
- NO placeholder text—show realistic {your_data_type}
"""
```

---

## Avatar Customization

Personas use **DiceBear avatars** by default:

```typescript
avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=YourName"
```

**Options:**
- Change `seed=YourName` for different avatars
- Use other DiceBear styles: `avataaars`, `bottts`, `personas`, `lorelei`
- Replace with your own image URLs

**Example:**
```typescript
avatar: "https://api.dicebear.com/7.x/personas/svg?seed=Alex"  // Different style
avatar: "https://yourcdn.com/avatars/alex.png"                 // Custom image
```

---

## Tips for Great Personas

### DO:
- **Be specific**: "I check Salesforce 20+ times daily" vs. "I use CRM tools"
- **Use real quotes**: "From manager: 'Can you pull Q3 churn data?'"
- **Include metrics**: "I'm responsible for keeping NPS above 8.5"
- **Show emotion**: "I feel frustrated when data is siloed"
- **Describe workflows**: "I export CSVs from 3 tools and merge them in Excel"

### DON'T:
- Be vague: "I use various tools" vs. "I use Mixpanel, GA4, and Heap"
- Skip the empathy map: It's the secret sauce for rich AI personalities!
- Create too many personas: 3-7 is ideal
- Make personas too similar: Diversify roles, seniority, and pain points
- Forget technical details: AI needs context about your domain

---

## Testing Your Customization

1. **Update configurations**:
   ```bash
   # Edit these files:
   frontend/src/config/product.config.ts
   frontend/src/config/personas.config.ts
   frontend/src/App.tsx (import the configs)
   ```

2. **Restart frontend**:
   ```bash
   cd frontend && npm run dev
   ```

3. **Test persona quality**:
   - Ask domain-specific questions
   - Toggle "Mock" on to test visual generation
   - Attach images to test multimodal understanding
   - Check if personas stay in character and use empathy map details

4. **Iterate**:
   - If personas are too generic → Add more specific details to empathy maps
   - If mocks are off-topic → Update `mockGenerationContext` in product.config.ts
   - If responses lack depth → Ensure personas have rich `think_and_feel`, `pain`, and `gain` arrays

---

## Community Examples

Share your customization! Create a PR to add your industry example:

**Template:**
```markdown
### Industry: [Your Industry]
- **Product**: [Your Product Name]
- **Personas**: [List persona roles]
- **Repo/Demo**: [Link if public]
- **Description**: [1-2 sentence description]
```

---

## 🆘 Need Help?

- **Issues**: Open a GitHub issue with the `customization` label
- **Discussions**: Use GitHub Discussions for questions
- **Examples**: Check `/examples` directory for more templates (coming soon!)

---

## Related Documentation

- [README.md](./README.md) - Project overview
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment options
- [QUICKSTART.md](./QUICKSTART.md) - Get running fast

---

**Made with love by the PersonaSay Community**

*Transform PersonaSay into YOUR product's AI persona engine!*

