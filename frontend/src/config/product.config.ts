/**
 * PRODUCT CONFIGURATION
 * 
 * This file defines the product context for your AI personas.
 * Customize this to match your own product/domain.
 * 
 * EXAMPLE: Sports Betting Analytics (LSports BOOST)
 * Replace with your own product details below.
 */

export interface ProductContext {
  name: string;
  tagline: string;
  description: string;
  industry: string;
  target_users: string[];
  key_features: string[];
  pain_points: string[];
  value_proposition: string;
  technical_context?: string;
}

/**
 * DEFAULT PRODUCT CONTEXT
 * 
 * This example is for BOOST - a sports betting analytics platform.
 * 
 * TO CUSTOMIZE:
 * 1. Replace all fields below with your product details
 * 2. Keep the same structure for best AI persona performance
 * 3. Be specific about your industry, users, and features
 */
export const productContext: ProductContext = {
  name: "BOOST by LSports",
  tagline: "Empower Your Sportsbook with Data-Driven Insights",
  description: "BOOST is a comprehensive sports betting analytics platform designed to help sportsbook operators evaluate and compare odds feed provider performance across pre-match and in-play sports markets.",
  industry: "Sports Betting & iGaming",
  
  target_users: [
    "Sportsbook Traders & Trading Managers",
    "Product Owners & Product Managers",
    "Performance Analysts & Data Scientists",
    "Operations & Support Teams",
    "Technical Integration Teams",
    "Business Stakeholders & Decision Makers"
  ],
  
  key_features: [
    "Real-time odds feed monitoring across multiple providers",
    "Coverage analysis by sport, league, and market type",
    "Uptime and latency tracking with SLA compliance",
    "Settlement accuracy and payout reconciliation",
    "Provider performance comparison dashboards",
    "Custom alerts for coverage gaps and outages",
    "Historical data analysis and trend reporting",
    "Multi-currency and multi-sport support"
  ],
  
  pain_points: [
    "Difficulty comparing multiple odds feed providers objectively",
    "Coverage gaps leading to customer dissatisfaction",
    "Settlement delays affecting customer trust and GGR",
    "Lack of visibility into provider SLA compliance",
    "Manual data collection and reporting is time-consuming",
    "Hard to justify provider costs without performance data",
    "Missed opportunities due to incomplete market coverage",
    "Technical issues not detected until customer complaints"
  ],
  
  value_proposition: "BOOST provides sportsbook operators with the data transparency and actionable insights needed to optimize odds feed provider selection, improve market coverage, reduce settlement errors, and ultimately increase customer satisfaction and GGR.",
  
  technical_context: "BOOST integrates with major odds feed providers (LSports, Betradar, BetGenius, etc.) via standardized APIs, ingests real-time data streams, and provides a unified analytics dashboard. The platform supports both pre-match and in-play betting markets across 50+ sports."
};

/**
 * MOCK GENERATION CONTEXT
 * 
 * This context is used when generating visual mocks (SVG diagrams).
 * Customize this to match your domain for better mock quality.
 */
export const mockGenerationContext = {
  domain: "Sports betting operations, sportsbook trading, odds feed providers, sports data analytics",
  
  requirements: [
    "Content MUST be relevant to: sports betting, odds providers, fixture coverage, market uptime, settlement data, sports leagues, trading operations",
    "Include: sports-specific metrics (e.g., Premier League coverage 98%, Provider A latency 1.2s, Settlement Success 95%), fixture lists, provider comparisons, market performance data",
    "Make it visually rich, professional, mature, and unique to sports betting analytics",
    "NO placeholder text—show realistic sports betting data (leagues, teams, providers, odds, coverage %)"
  ],
  
  // Example data that AI can use in mocks
  example_sports: ["Football/Soccer", "Basketball", "Tennis", "American Football", "Ice Hockey", "Baseball", "Esports"],
  example_leagues: ["Premier League", "La Liga", "NBA", "NFL", "Champions League", "ATP Tour"],
  example_providers: ["LSports", "Betradar", "BetGenius", "Kambi", "SBTech"],
  example_metrics: ["Coverage %", "Uptime", "Latency (ms)", "Settlement Success", "Market Count", "Odds Margin"]
};

