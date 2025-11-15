"""
LangChain-based PersonaSay Multi-Agent System
Official LangChain implementation from https://langchain.com
Each persona is an independent agent with persistent memory and tools
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.logging_config import get_logger

logger = get_logger(__name__)

# LangChain Core
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict

# Database & Storage
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


class Settings(BaseSettings):
    """LangChain PersonaSay Settings"""

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore"  # Allow extra fields from .env file
    )

    openai_api_key: str = ""  # Must be provided via env var or parameter
    database_url: str = "sqlite:///./data/personasay.db"
    redis_url: str = "redis://localhost:6379"
    langsmith_api_key: str = ""
    langsmith_project: str = "PersonaSay"


# Database Models
Base = declarative_base()


class PersonaMemory(Base):
    """Persistent memory storage for personas"""

    __tablename__ = "persona_memories"

    id = Column(Integer, primary_key=True)
    persona_id = Column(String(255), index=True)
    session_id = Column(String(255), index=True)
    message_type = Column(String(50))  # 'human', 'ai', 'system'
    content = Column(Text)
    meta_data = Column(Text)  # JSON metadata
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConversationSession(Base):
    """Track conversation sessions"""

    __tablename__ = "conversation_sessions"

    id = Column(String(255), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    meta_data = Column(Text)  # JSON metadata about the session


class LangChainPersonaAgent:
    """
    Individual Persona Agent using official LangChain architecture
    Each agent has persistent memory, tools, and independent thinking capability
    """

    def __init__(self, persona_data: Dict[str, Any], settings: Settings, db_session: Session):
        self.settings = settings
        self.db_session = db_session

        # Load enhanced profile if available (Phase 1)
        from app.enhanced_profile_loader import get_persona_data

        self.persona_data = get_persona_data(persona_data["id"], persona_data)

        # Persona identity
        self.persona_id = self.persona_data["id"]
        self.name = self.persona_data["name"]
        self.role = self.persona_data.get("role", self.persona_data.get("title", "Expert"))
        self.company = self.persona_data["company"]
        self.avatar = self.persona_data.get("avatar", "")
        self.empathy_map = self.persona_data.get("empathy_map", {})

        # Initialize LangChain components
        self._initialize_llm()
        self._initialize_memory()
        self._initialize_tools()
        self._initialize_agent(context_mode="evaluation")  # Default to evaluation mode

    def _initialize_llm(self):
        """Initialize the LangChain LLM with role-specific temperature for diverse responses"""
        # Role-specific temperature for differentiation
        role_lower = self.role.lower()
        if any(
            keyword in role_lower for keyword in ["trading", "trader", "risk", "quant", "analyst"]
        ):
            temperature = 0.6  # More precise, data-driven
        elif any(keyword in role_lower for keyword in ["product", "pm", "design", "ux"]):
            temperature = 0.85  # More creative, strategic
        elif any(keyword in role_lower for keyword in ["operations", "ops", "support", "engineer"]):
            temperature = 0.65  # Practical, process-oriented
        elif any(keyword in role_lower for keyword in ["data", "analytics", "scientist"]):
            temperature = 0.55  # Analytical, methodical
        elif any(
            keyword in role_lower for keyword in ["vp", "director", "executive", "ceo", "cto"]
        ):
            temperature = 0.75  # Strategic, high-level
        else:
            temperature = 0.75  # Default balanced

        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model="gpt-4o",
            temperature=temperature,  # Role-specific temperature for uniqueness
            max_tokens=1500,  # Enough for thorough, detailed responses
            streaming=True,
        )
        logger.debug(f"{self.name} ({self.role}) initialized with temperature={temperature}")

    def _initialize_memory(self):
        """Initialize persistent memory using LangChain memory abstractions"""
        # LangChain conversation memory with custom persistence
        self.memory = ConversationBufferWindowMemory(
            k=50,  # Keep last 50 messages (increased for better context)
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output",
        )

        # Load existing memory from database
        self._load_memory_from_db()

    def _initialize_tools(self):
        """Initialize tools that the persona can use - enhanced for better reasoning"""
        base_tools = [
            Tool(
                name="analyze_product_context",
                description="Deep analysis of product context focusing on aspects most relevant to your role. Use when discussing features, requirements, or strategic decisions.",
                func=self._analyze_product_context,
            ),
            Tool(
                name="recall_past_discussion",
                description="Search your memory for relevant past conversations or points you've made. Use when user asks to elaborate, when building on previous points, or when ensuring consistency.",
                func=self._recall_past_discussion,
            ),
            Tool(
                name="role_specific_analysis",
                description=f"Provide {self.role}-specific analysis considering your daily challenges, pain points, and goals from your empathy map. Use for in-depth, role-focused insights.",
                func=self._role_specific_analysis,
            ),
            Tool(
                name="identify_risks_and_opportunities",
                description="Analyze risks and opportunities from your unique perspective and company context. Use when discussing new features, changes, or strategic decisions.",
                func=self._identify_risks_and_opportunities,
            ),
        ]

        # Add role-specific tools based on persona
        role_tools = self._get_role_specific_tools()
        self.tools = base_tools + role_tools

    def _initialize_agent(self, context_mode: str = "evaluation"):
        """Initialize the LangChain agent with prompt and tools

        Args:
            context_mode: "evaluation" or "debate" to set appropriate persona framing
        """
        # Create system prompt template
        system_prompt = self._create_system_prompt(context_mode=context_mode)

        # Create prompt template with LangChain
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,  # Balanced for thorough responses with reasonable speed
            early_stopping_method="generate",
        )

        self.context_mode = context_mode

    def _create_system_prompt(self, context_mode: str = "evaluation") -> str:
        """Create comprehensive system prompt for the persona with validation requirements

        Args:
            context_mode: "evaluation" for product evaluation (customer evaluating BOOST),
                         "debate" for general debates (customer perspective, not about BOOST)
        """
        from datetime import datetime

        # Calculate current date context dynamically
        now = datetime.now()
        current_year = now.year
        current_quarter_num = (now.month - 1) // 3 + 1
        current_quarter = f"Q{current_quarter_num}"
        current_month = now.strftime("%B")

        # Calculate next quarter
        if current_quarter_num == 4:
            next_quarter = "Q1"
            next_quarter_year = current_year + 1
        else:
            next_quarter = f"Q{current_quarter_num + 1}"
            next_quarter_year = current_year

        empathy_details = ""
        if self.empathy_map:
            empathy_details = f"""
EMPATHY MAP:
- Think & Feel: {self.empathy_map.get('think_and_feel', 'Not specified')}
- Hear: {self.empathy_map.get('hear', 'Not specified')}
- See: {self.empathy_map.get('see', 'Not specified')}
- Say & Do: {self.empathy_map.get('say_and_do', 'Not specified')}
- Pain Points: {self.empathy_map.get('pain', 'Not specified')}
- Goals & Gains: {self.empathy_map.get('gain', 'Not specified')}
"""

        # Different identity framing based on context
        if context_mode == "debate":
            identity = f"""You are {self.name}, a {self.role} at {self.company}.
You are a CUSTOMER/USER perspective, NOT a BOOST employee. You represent the voice of betting operators who use or might use BOOST's services.

DEBATE MODE - ENGAGEMENT RULES:
- This is a CONVERSATION with other betting industry professionals, not isolated statements
- LISTEN to what others say and RESPOND to their specific points
- DISAGREE explicitly when your priorities differ: "I see [Name]'s point, but from my perspective..."
- ACKNOWLEDGE when someone makes a good argument: "That's a fair point about X, and..."
- ADJUST your position if convinced by good reasoning - changing your mind shows critical thinking
- REFERENCE specific people and their arguments: "While Marco emphasizes X, I think..."
- DON'T repeat yourself across rounds - the debate should evolve
- CONTRAST your company's constraints with others: "Unlike larger operators, we..."
- BUILD ON or CHALLENGE previous points - this is a dynamic conversation"""
        else:
            identity = f"""You are {self.name}, {self.role} at {self.company}.
You are evaluating BOOST as a potential solution for your company."""

        # Time awareness context
        time_context = f"""
CURRENT DATE & TIME CONTEXT:
- Today's date: {current_month} {now.day}, {current_year}
- Current quarter: {current_quarter} {current_year}
- Next quarter: {next_quarter} {next_quarter_year}
- Current year: {current_year}
- Next year: {current_year + 1}

WHEN DISCUSSING TIMING:
- Use "this quarter" to mean {current_quarter} {current_year}
- Use "next quarter" to mean {next_quarter} {next_quarter_year}
- Use "this year" to mean {current_year}
- Use relative terms: "recently", "upcoming", "in the coming months"
- Don't reference specific hardcoded dates unless provided in context
"""

        return f"""{identity}

{time_context}

{empathy_details}

CORE IDENTITY:
- You are a real professional with years of experience in your role
- You have strong opinions shaped by your unique background and challenges
- You think independently and don't just agree with others
- You remember ALL previous conversations and build meaningful continuity
- Your perspective is shaped by your company size, role, and daily challenges

UNIQUENESS & DIFFERENTIATION:
- Your response should be UNIQUE to your role as {self.role}
- Vary your language naturally - don't repeat the same phrases or introductions
- NEVER mention your role/title in your response (e.g., "As a {self.role}..." or "From my perspective as...")
- Your role is already displayed in the UI header - don't repeat it in your text
- Reference YOUR specific pain points from your empathy map when relevant
- Show how YOUR priorities differ from other roles through your actual concerns and focus areas
- Use terminology and metrics specific to {self.role} (not generic business speak)
- If other personas respond, CONTRAST your view with theirs based on different priorities
- Let your constraints show through your concerns, not through explicit statements about your position

THINKING & REASONING:
- Think through questions carefully using your expertise and tools when helpful
- Reference specific past conversations to show continuity
- Draw from your empathy map (pains, gains, what you see/hear daily) naturally
- Challenge assumptions if they don't align with YOUR SPECIFIC experience
- Use concrete examples from your role - be specific, not generic
- If you disagree with another persona, explain why based on actual differences in priorities
- Focus on metrics and KPIs that matter to YOUR role, not all roles

CONVERSATION STYLE:
- Speak naturally as {self.name}, like a real colleague in a conversation
- CRITICAL: Never start responses with "As a [role]..." or "From my perspective as [role]..."
- Jump directly into your point - your role is already shown in the UI
- Vary your openings - don't start every response the same way
- Show personality through your concerns and priorities, not self-introductions
- Use industry terminology naturally when it fits the discussion
- Reference constraints naturally when they're relevant to the point
- Build on previous points - don't repeat phrases or patterns from earlier responses
- If asked to elaborate, dive DEEPER with role-specific insights
- Be conversational: you're in a multi-turn dialogue, not giving isolated speeches

TOOL USAGE:
- Use tools when they add value to your response
- Use analyze_product_context for questions about features, requirements, or strategy
- Use recall_past_discussion when building on previous conversations
- Use role_specific_analysis for deep insights from your perspective

RESPONSE QUALITY:
- Provide thorough, insightful responses (150-250 words typically)
- Include specific examples, concerns, or suggestions from your role's viewpoint
- Show how your response connects to previous discussion points
- End with forward-thinking questions or implications when relevant
- Be comprehensive but avoid unnecessary verbosity

STRICT RESPONSE REQUIREMENTS (CRITICAL):

TARGET LENGTH: 150-200 words (STRICT)
- Minimum: 150 words
- Maximum: 250 words (hard limit)
- Optimal: 180-200 words
- If over 200 words, remove least important details

VALIDATION CHECKLIST (You MUST include ALL of these in EVERY response):
Before sending your response, verify:
✓ Referenced at least ONE specific number (budget, team size, metric, percentage)
   Examples: "$25K approval limit", "25 people", "99.95% uptime", "30 minutes"

✓ Used at least TWO role-specific terms for {self.role}
   Examples: industry jargon, technical terms, metrics specific to your domain

✓ Mentioned at least ONE constraint or decision criterion
   Examples: budget limits, approval processes, team capacity, goals, stakeholder dynamics

✓ Used at least ONE typical phrase or showed your communication style
   Examples: your usual way of starting responses, skepticism patterns, decision-making language

✓ Spoke from EXPERIENCE, not fake incidents
   Use: "In my experience...", "I've dealt with situations where...", "We've seen..."
   AVOID: Claiming specific events you haven't verified

If you cannot check ALL 5 boxes above, STOP and REVISE your response.

Remember: You're not here to just answer - you're here to provide the authentic perspective of {self.name}, {self.role} at {self.company}.
- Be conversational but professional
- Use formatting (bold, lists, etc.) when helpful
- Reference specific metrics, KPIs, or examples when relevant
- Show your unique perspective and expertise
- Keep responses focused and valuable (2-3 paragraphs typically)

Remember: You are an independent thinking agent with your own memory, tools, and perspective. Think before you respond and use your capabilities effectively."""

    def _load_memory_from_db(self):
        """Load conversation history from database into LangChain memory"""
        try:
            # Get recent memories for this persona
            recent_memories = (
                self.db_session.query(PersonaMemory)
                .filter(PersonaMemory.persona_id == self.persona_id)
                .order_by(PersonaMemory.timestamp.desc())
                .limit(20)
                .all()
            )

            # Convert to LangChain messages and load into memory
            for memory in reversed(recent_memories):  # Reverse to get chronological order
                if memory.message_type == "human":
                    self.memory.chat_memory.add_user_message(memory.content)
                elif memory.message_type == "ai":
                    self.memory.chat_memory.add_ai_message(memory.content)

            logger.debug(f"Loaded {len(recent_memories)} memory items for {self.name}")

        except Exception as e:
            logger.error(f"Error loading memory for {self.name}: {e}")

    def _save_memory_to_db(self, human_message: str, ai_message: str, session_id: str):
        """Save conversation to database for persistence"""
        try:
            # Save human message
            human_memory = PersonaMemory(
                persona_id=self.persona_id,
                session_id=session_id,
                message_type="human",
                content=human_message,
                meta_data=json.dumps({"persona_name": self.name}),
            )

            # Save AI response
            ai_memory = PersonaMemory(
                persona_id=self.persona_id,
                session_id=session_id,
                message_type="ai",
                content=ai_message,
                meta_data=json.dumps({"persona_name": self.name}),
            )

            self.db_session.add(human_memory)
            self.db_session.add(ai_memory)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Error saving memory for {self.name}: {e}")
            self.db_session.rollback()

    async def think_and_respond(
        self, user_message: str, product_context: Dict[str, Any], session_id: str = None
    ) -> str:
        """
        Main method for persona to think and respond - FAST PATH without agent overhead
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            logger.debug(f"{self.name} thinking about: {user_message[:50]}...")

            # Build conversation context from memory
            chat_history = self.memory.load_memory_variables({})
            history_text = ""
            if chat_history.get("chat_history"):
                recent_messages = chat_history["chat_history"][-6:]  # Last 3 exchanges
                for msg in recent_messages:
                    role = "User" if hasattr(msg, "type") and msg.type == "human" else "You"
                    history_text += f"{role}: {msg.content}\n"

            # Create system prompt
            system_prompt = self._create_system_prompt()

            # Direct LLM call (bypasses agent/tools for speed)
            # Build history section without backslash in f-string
            history_section = f"Recent conversation:\n{history_text}" if history_text else ""

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""Product Context: {json.dumps(product_context, indent=2)}

{history_section}

User Message: {user_message}

Respond as {self.name} based on your role and expertise.""",
                },
            ]

            response_obj = await self.llm.ainvoke(messages)
            response = response_obj.content

            logger.debug(f"{self.name} generated response: {response[:100]}...")

            # Validate response quality
            try:
                from app.enhanced_profile_loader import prepare_for_validator
                from app.response_validator import ResponseValidator

                validator = ResponseValidator()

                # Prepare persona data for validator (handles enhanced profiles)
                validator_data = prepare_for_validator(self.persona_data)

                validation = validator.validate_response_quality(response, validator_data)

                # Log validation results
                if not validation["passed"]:
                    logger.warning(
                        f"{self.name} response quality: {validation['score']}/100. "
                        f"Issues: {validation['issues']}"
                    )
                else:
                    logger.info(f"{self.name} response quality: {validation['score']}/100 ✓")
            except Exception as validation_error:
                logger.error(f"Validation error for {self.name}: {validation_error}")

            # Save to memory
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(response)

            # Save to persistent database
            self._save_memory_to_db(user_message, response, session_id)

            return response

        except Exception as e:
            error_msg = f"Error in {self.name}'s thinking process: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"

    # Enhanced Tool Implementations
    def _analyze_product_context(self, query: str) -> str:
        """Deep analysis tool - focuses on role-relevant aspects"""
        pain_points = self.empathy_map.get("pain", "")
        gains = self.empathy_map.get("gain", "")

        return f"""ANALYSIS AS {self.role}:

Key Considerations for {self.company}:
- Pain Points to Address: {pain_points}
- Value I'm Looking For: {gains}
- My Role's Priority: How this impacts my daily responsibilities and KPIs

This analysis should inform a response that's grounded in my real-world challenges."""

    def _recall_past_discussion(self, topic: str) -> str:
        """Search memory for relevant past conversations"""
        # Get recent conversation context from memory
        messages = (
            self.memory.chat_memory.messages[-20:] if self.memory.chat_memory.messages else []
        )

        relevant_context = []
        for msg in messages:
            if topic.lower() in msg.content.lower():
                relevant_context.append(msg.content[:200])

        if relevant_context:
            return f"PAST CONTEXT RECALLED: {' | '.join(relevant_context[:3])}"
        return f"No specific past discussion found on '{topic}', responding with fresh perspective."

    def _role_specific_analysis(self, topic: str) -> str:
        """Provide deep role-specific insights"""
        think_feel = self.empathy_map.get("think_and_feel", "")
        see = self.empathy_map.get("see", "")
        hear = self.empathy_map.get("hear", "")

        return f"""ROLE-SPECIFIC PERSPECTIVE ({self.role}):

What I Think/Feel: {think_feel}
What I See Daily: {see}
What I Hear: {hear}

This shapes how I view '{topic}' through my unique lens at {self.company}."""

    def _identify_risks_and_opportunities(self, topic: str) -> str:
        """Analyze from risk/opportunity perspective"""
        pain = self.empathy_map.get("pain", "operational challenges")
        gain = self.empathy_map.get("gain", "efficiency improvements")

        return f"""RISK & OPPORTUNITY ANALYSIS:

RISKS (based on my pain points): {pain}
- How could this exacerbate existing challenges?
- What are the implementation hurdles for {self.company}?

OPPORTUNITIES (aligned with my goals): {gain}
- How could this address my key pain points?
- What value does this unlock for my role?

Recommendation: [Agent will synthesize based on above]"""

    def _get_role_specific_tools(self) -> List[Tool]:
        """Get additional tools based on specific role type"""
        role_lower = self.role.lower()
        additional_tools = []

        # Trading/Performance roles get data analysis tools
        if any(keyword in role_lower for keyword in ["trading", "analyst", "performance"]):
            additional_tools.append(
                Tool(
                    name="analyze_metrics_impact",
                    description="Analyze how this impacts key metrics, KPIs, and performance indicators relevant to your role",
                    func=lambda x: f"METRICS IMPACT: Analyzing effect on operational KPIs, performance benchmarks, and measurable outcomes from {self.role} perspective. Consider: uptime, latency, accuracy, cost, efficiency.",
                )
            )

        # Product/Management roles get stakeholder analysis
        if any(keyword in role_lower for keyword in ["product", "owner", "manager", "vp", "lead"]):
            additional_tools.append(
                Tool(
                    name="stakeholder_analysis",
                    description="Analyze stakeholder impact and adoption considerations",
                    func=lambda x: f"STAKEHOLDER ANALYSIS: As {self.role}, considering team adoption, user experience impact, training needs, and cross-functional dependencies at {self.company}.",
                )
            )

        # Support/Operations roles get operational impact tool
        if any(keyword in role_lower for keyword in ["support", "operations", "ops"]):
            additional_tools.append(
                Tool(
                    name="operational_impact",
                    description="Assess operational and support implications",
                    func=lambda x: f"OPERATIONAL IMPACT: Evaluating support burden, operational complexity, incident management considerations, and team bandwidth from {self.role} perspective.",
                )
            )

        return additional_tools


class LangChainPersonaManager:
    """
    Manager for multiple LangChain-based persona agents
    Handles orchestration, database setup, and agent coordination
    """

    def __init__(self, api_key: str = None):
        self.settings = Settings(openai_api_key=api_key) if api_key else Settings()
        self.personas: Dict[str, LangChainPersonaAgent] = {}

        # Setup database
        self._setup_database()

    def _setup_database(self):
        """Setup database connection and tables"""
        self.engine = create_engine(self.settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session = SessionLocal()
        logger.info(f"Database setup complete: {self.settings.database_url}")

    def initialize_personas(self, personas_data: List[Dict[str, Any]]):
        """Initialize all persona agents with LangChain"""
        logger.info(f"Initializing {len(personas_data)} LangChain persona agents...")

        for persona_data in personas_data:
            persona_id = persona_data["id"]
            try:
                self.personas[persona_id] = LangChainPersonaAgent(
                    persona_data=persona_data, settings=self.settings, db_session=self.db_session
                )
                logger.info(f"Initialized LangChain agent: {persona_data['name']}")
            except Exception as e:
                logger.error(f"Failed to initialize {persona_data['name']}: {e}")

        logger.info(f"LangChain PersonaSay ready with {len(self.personas)} agents!")

    async def get_all_responses(
        self,
        active_persona_ids: List[str],
        user_message: str,
        product_context: Dict[str, Any],
        session_id: str = None,
    ) -> List[Dict[str, Any]]:
        """Get responses from all active personas using LangChain agents"""
        if not session_id:
            session_id = str(uuid.uuid4())

        logger.debug(f"Processing through {len(active_persona_ids)} LangChain agents...")

        # Create tasks for concurrent processing
        tasks = []
        for persona_id in active_persona_ids:
            if persona_id in self.personas:
                task = self.personas[persona_id].think_and_respond(
                    user_message, product_context, session_id
                )
                tasks.append((persona_id, task))

        # Execute all agents concurrently
        responses = []
        for persona_id, task in tasks:
            try:
                response = await task
                persona = self.personas[persona_id]
                responses.append(
                    {
                        "persona_id": persona_id,
                        "name": persona.name,
                        "response": response,
                        "role": persona.role,
                        "company": persona.company,
                        "avatar": persona.avatar,
                        "system": "langchain",
                    }
                )
            except Exception as e:
                logger.error(f"Error from {persona_id}: {e}")
                persona = self.personas[persona_id]
                responses.append(
                    {
                        "persona_id": persona_id,
                        "name": persona.name,
                        "response": f"I apologize, but I'm experiencing technical difficulties: {str(e)}",
                        "role": persona.role,
                        "company": persona.company,
                        "avatar": persona.avatar,
                        "error": True,
                    }
                )

        logger.info(f"Generated {len(responses)} LangChain responses")
        return responses

    def get_persona_memory(self, persona_id: str) -> Dict[str, Any]:
        """Get memory summary for a specific persona"""
        if persona_id not in self.personas:
            return {"error": f"Persona {persona_id} not found"}

        try:
            # Get recent memories from database
            memories = (
                self.db_session.query(PersonaMemory)
                .filter(PersonaMemory.persona_id == persona_id)
                .order_by(PersonaMemory.timestamp.desc())
                .limit(10)
                .all()
            )

            memory_summary = {
                "persona_id": persona_id,
                "name": self.personas[persona_id].name,
                "total_memories": len(memories),
                "recent_conversations": [
                    {
                        "type": mem.message_type,
                        "content": (
                            mem.content[:100] + "..." if len(mem.content) > 100 else mem.content
                        ),
                        "timestamp": mem.timestamp.isoformat(),
                    }
                    for mem in memories
                ],
            }

            return memory_summary

        except Exception as e:
            return {"error": f"Failed to retrieve memory: {str(e)}"}

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get full conversation history for a session"""
        try:
            memories = (
                self.db_session.query(PersonaMemory)
                .filter(PersonaMemory.session_id == session_id)
                .order_by(PersonaMemory.timestamp)
                .all()
            )

            return [
                {
                    "persona_id": mem.persona_id,
                    "message_type": mem.message_type,
                    "content": mem.content,
                    "timestamp": mem.timestamp.isoformat(),
                    "metadata": json.loads(mem.meta_data) if mem.meta_data else {},
                }
                for mem in memories
            ]

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []

    def cleanup(self):
        """Cleanup database connections"""
        if hasattr(self, "db_session"):
            self.db_session.close()


# Example usage and testing
if __name__ == "__main__":

    async def test_langchain_personas():
        """Test the LangChain persona system"""

        # Sample persona data
        test_personas = [
            {
                "id": "alex_trading",
                "name": "Alex",
                "role": "Head of Trading",
                "company": "Tier 1 Sportsbook",
                "empathy_map": {
                    "think_and_feel": "Focused on risk management and profitability",
                    "pain": "Market inefficiencies and poor data quality",
                    "gain": "Better odds accuracy and risk control",
                },
            }
        ]

        # Initialize manager
        manager = LangChainPersonaManager(api_key="your-openai-key")
        manager.initialize_personas(test_personas)

        # Test conversation
        responses = await manager.get_all_responses(
            active_persona_ids=["alex_trading"],
            user_message="What are your thoughts on implementing real-time odds monitoring?",
            product_context={"product": "BOOST Analytics", "feature": "Real-time monitoring"},
        )

        for response in responses:
            logger.info(f"{response['name']}: {response['response']}")

        manager.cleanup()

    # Uncomment to test
    # asyncio.run(test_langchain_personas())
