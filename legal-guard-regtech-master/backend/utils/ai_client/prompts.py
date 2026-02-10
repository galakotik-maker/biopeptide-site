import json
from typing import Dict, Any, Optional


class PromptFormatter:
    """Handles prompt formatting and templating for different use cases"""
    SYSTEM_MESSAGES = {
        "default": "You are LegalGuard AI, an expert legal technology assistant. You analyze contracts and provide structured JSON responses.",
        
        "contract_analysis": """You are LegalGuard AI powered by IBM Granite, an expert legal compliance analyzer specialized in Malaysian employment law, PDPA, GDPR, and contract compliance for the TechXchange Hackathon.

CRITICAL ANALYSIS INSTRUCTIONS FOR IBM GRANITE:
You are analyzing contracts with precision and legal expertise. Apply rigorous legal analysis and only flag genuine statutory violations.

ANALYSIS METHODOLOGY:

STEP 1: CONTRACT TYPE IDENTIFICATION
Carefully read the entire contract and determine:
- Contract type: employment, service agreement, data processing, NDA, etc.
- Primary business relationship and obligations
- Whether personal data processing is involved
- Jurisdiction and governing law

STEP 2: APPLICABLE LAW DETERMINATION
Apply ONLY relevant legal frameworks based on contract analysis:

FOR EMPLOYMENT CONTRACTS (Malaysia):
- Employment Act 1955 - Sections 12 (termination notice), 60A (working hours/overtime), 60E (annual leave), 11 (probation)
- Minimum wage requirements (RM1,500)
- EPF Act 1991 (11% employee, 12-13% employer contribution)
- SOCSO Act 1969 (employment injury and invalidity coverage)
- Statutory benefits and protections

FOR DATA PROCESSING (Any jurisdiction):
- PDPA (Malaysia/Singapore) - Consent, data subject rights, security
- GDPR (EU) - Lawful basis, data subject rights, cross-border transfers
- CCPA (US) - Consumer rights, disclosure requirements

FOR ALL CONTRACTS:
- Contract law principles - consideration, unconscionable terms, enforceability

STEP 3: RIGOROUS LEGAL ANALYSIS
Identify ONLY clear statutory violations with specific legal references:

EMPLOYMENT LAW VIOLATIONS (Employment Act 1955):
✓ Section 12: Termination without minimum notice (2 weeks for <2 years, 4 weeks for >2 years service)
✓ Section 60A: Missing overtime compensation (1.5x normal rate)
✓ Section 60A: Excessive working hours (>8 hours/day or >48 hours/week)
✓ Section 60E: Missing annual leave (8-16 days based on service length)
✓ Section 11: Probation period exceeding 6 months
✓ Below minimum wage (RM1,500 monthly)
✓ Missing EPF/SOCSO contributions
✓ Missing rest day and public holiday provisions

SPECIFIC EMPLOYMENT CONTRACT ANALYSIS EXAMPLES:
- "Employee may be terminated without notice" → HIGH SEVERITY (violates Section 12)
- "Working hours: 10 hours per day" → HIGH SEVERITY (violates Section 60A maximum 8 hours)
- "Salary: RM1,200 per month" → HIGH SEVERITY (below RM1,500 minimum wage)
- "No overtime payment mentioned" → HIGH SEVERITY (violates Section 60A)
- "Annual leave: 5 days" → MEDIUM SEVERITY (below Section 60E minimum 8 days)
- "Probation: 12 months" → MEDIUM SEVERITY (exceeds Section 11 maximum 6 months)

DATA PROTECTION VIOLATIONS:
✓ Missing explicit consent for personal data collection
✓ Inadequate lawful basis for processing
✓ Missing data subject rights (access, rectification, erasure)
✓ Insufficient cross-border transfer safeguards
✓ Missing breach notification procedures

GENERAL CONTRACT VIOLATIONS:
✓ Unconscionable liability limitations (<RM1,000)
✓ Unilateral modification rights without consideration
✓ Missing essential terms (consideration, performance obligations)

STEP 4: SEVERITY ASSESSMENT
- HIGH: Clear violation of mandatory statutory requirements with significant penalties
- MEDIUM: Non-compliance with regulatory guidance or best practices
- LOW: Minor technical issues (avoid flagging these)

CRITICAL RULES FOR IBM GRANITE:
1. ONLY flag clear violations of specific statutory provisions
2. Provide exact legal section references (e.g., "Employment Act 1955 Section 12")
3. Extract precise clause text that violates the law
4. Do NOT flag theoretical or minor issues
5. Do NOT apply employment law to non-employment contracts
6. Do NOT apply PDPA/GDPR unless contract processes personal data
7. Maximum 8 flagged clauses to maintain focus on critical issues
8. Be extremely specific in identifying violations

ENHANCED EMPLOYMENT CONTRACT REQUIREMENTS:
For Malaysian employment contracts, specifically check for:
- Termination notice periods (minimum 2-4 weeks based on service)
- Working hours compliance (max 8 hours/day, 48 hours/week)
- Overtime payment provisions (minimum 1.5x normal rate)
- Annual leave entitlement (8-16 days based on service)
- Probation period limits (maximum 6 months)
- Minimum wage compliance (RM1,500 monthly)
- EPF contribution (11% employee, 12-13% employer)
- SOCSO contribution requirements
- Rest days and public holiday provisions

RESPONSE FORMAT:
Return ONLY valid JSON with specific legal references. Each compliance issue must have exactly ONE law field:

{
  "summary": "Precise assessment of statutory violations found with specific legal references",
  "flagged_clauses": [
    {
      "clause_text": "Exact contract clause text that violates the law",
      "issue": "Specific violation with exact statutory reference (e.g., 'Violates Employment Act 1955 Section 12 - minimum 4 weeks notice required')",
      "severity": "high|medium"
    }
  ],
  "compliance_issues": [
    {
      "law": "EMPLOYMENT_ACT_MY",
      "missing_requirements": ["Specific employment law requirements missing from contract with exact statutory references"],
      "recommendations": ["Add specific employment law compliance measures with exact implementation details"]
    },
    {
      "law": "PDPA_MY", 
      "missing_requirements": ["Specific data protection requirements missing"],
      "recommendations": ["Implement specific PDPA compliance measures"]
    }
  ]
}

CRITICAL: 
- Use exactly ONE law per compliance issue object
- Valid law values: EMPLOYMENT_ACT_MY, PDPA_MY, PDPA_SG, GDPR_EU, CCPA_US
- Do NOT combine multiple laws in one field
- Be extremely specific in requirements and recommendations with exact statutory section references
- Include specific amounts, timeframes, and percentages in requirements

If contract is fully compliant:
{
  "summary": "Contract meets applicable statutory requirements for the identified jurisdiction.",
  "flagged_clauses": [],
  "compliance_issues": []
}""",
        
        "metadata_extraction": "You are a legal document analyzer. Extract metadata from contracts and return structured JSON.",
        
        "compliance_summary": "You are a legal compliance consultant creating executive summaries."
    }
    
    @staticmethod
    def format_for_granite(prompt: str, system_message: Optional[str] = None) -> str:
        """
        Format prompt specifically for IBM Granite models.
        
        Args:
            prompt: The main prompt text
            system_message: Optional system message, uses default if not provided
            
        Returns:
            Formatted prompt string for Granite models
        """
        if system_message is None:
            system_message = PromptFormatter.SYSTEM_MESSAGES["default"]
        
        # Granite models work better with a simpler format and explicit completion instruction
        return f"""{system_message}

{prompt}

Analyze carefully and return complete JSON response:"""
    
    @staticmethod
    def build_contract_analysis_prompt(contract_text: str, compliance_checklist: Dict[str, Any]) -> str:
        """
        Build comprehensive contract analysis prompt optimized for IBM Granite models.
        
        Args:
            contract_text: The contract text to analyze
            compliance_checklist: Compliance requirements to check against
            
        Returns:
            Formatted analysis prompt
        """
        # Clean the contract text for better analysis
        cleaned_contract = PromptFormatter._clean_contract_text(contract_text)
        checklist_str = json.dumps(compliance_checklist, indent=2)
        
        return f"""LEGAL COMPLIANCE ANALYSIS TASK

CONTRACT TO ANALYZE:
```
{cleaned_contract}
```

APPLICABLE LEGAL REQUIREMENTS:
{checklist_str}

ANALYSIS INSTRUCTIONS:

1. READ THE ENTIRE CONTRACT CAREFULLY
   - Identify the contract type and business relationship
   - Determine if personal data is actually processed
   - Identify the governing jurisdiction
   - Note the parties and their roles

2. DETERMINE APPLICABLE LAWS
   Based on what you read, apply ONLY relevant legal frameworks:
   
   IF this is a data processing agreement OR privacy policy OR contains personal data collection:
   → Apply GDPR/PDPA requirements
   
   IF this is an employment contract OR contractor agreement with employment-like terms:
   → Apply employment law requirements
   
   FOR ALL contracts:
   → Apply general contract law principles

3. IDENTIFY GENUINE VIOLATIONS ONLY
   Look for specific clauses that violate mandatory legal requirements:
   
   For Data Processing (if applicable):
   ✓ Check for proper consent mechanisms
   ✓ Verify lawful basis for processing
   ✓ Ensure data subject rights are addressed
   ✓ Check cross-border transfer safeguards
   ✓ Verify breach notification procedures
   ✓ Check security measures
   
   For Employment (if applicable):
   ✓ Verify termination notice periods meet minimums
   ✓ Check overtime and working time compliance
   ✓ Ensure minimum wage compliance
   ✓ Verify leave entitlements
   
   For All Contracts:
   ✓ Check liability limitations are reasonable
   ✓ Ensure termination clauses are fair
   ✓ Verify indemnification is balanced
   ✓ Check for unconscionable terms

4. EXTRACT CLEAN CLAUSE TEXT
   When flagging problematic clauses:
   - Remove all markdown formatting (\n, **, ##, etc.)
   - Provide the exact problematic text in readable format
   - Keep clause text concise but complete

5. ASSESS SEVERITY ACCURATELY
   - HIGH: Violates mandatory law with serious penalties
   - MEDIUM: Non-compliance with guidance or best practices  
   - LOW: Minor technical issues

IMPORTANT: If the contract is a simple service agreement with no personal data processing, do NOT flag PDPA violations. If it's not an employment contract, do NOT flag employment law issues.

Provide your analysis as valid JSON only."""
    
    @staticmethod
    def _clean_contract_text(contract_text: str) -> str:
        """
        Clean contract text to remove excessive whitespace and formatting issues.
        
        Args:
            contract_text: Raw contract text
            
        Returns:
            Cleaned contract text
        """
        # Remove excessive newlines and whitespace
        lines = contract_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join with single newlines and limit total length for context window
        cleaned = '\n'.join(cleaned_lines)
        
        # If contract is very long, truncate but ensure we keep important parts
        if len(cleaned) > 8000:  # Reasonable limit for analysis
            # Try to keep the beginning and end, which often contain key terms
            first_half = cleaned[:4000]
            last_half = cleaned[-4000:]
            cleaned = first_half + "\n\n[... middle section truncated ...]\n\n" + last_half
        
        return cleaned
    
    @staticmethod
    def build_metadata_extraction_prompt(contract_text: str) -> str:
        """
        Build metadata extraction prompt.
        
        Args:
            contract_text: The contract text to analyze
            
        Returns:
            Formatted metadata extraction prompt
        """
        cleaned_contract = PromptFormatter._clean_contract_text(contract_text)
        
        return f"""Analyze this contract and extract key metadata.

CONTRACT TEXT:
```
{cleaned_contract}
```

Extract the following information and return as JSON:

{{
  "contract_type": "employment|service|nda|partnership|data_processing|other",
  "parties": ["list of contracting parties"],
  "jurisdiction": "detected jurisdiction code (MY/SG/EU/US)",
  "key_dates": ["important dates mentioned"],
  "contract_value": "monetary value if mentioned",
  "duration": "contract duration if specified",
  "data_processing": "yes|no - does this contract involve personal data processing"
}}

JSON response only:"""
    
    @staticmethod
    def build_compliance_summary_prompt(analysis_results: Dict[str, Any]) -> str:
        """
        Build compliance summary generation prompt.
        
        Args:
            analysis_results: Results from previous analysis
            
        Returns:
            Formatted summary prompt
        """
        return f"""Create an executive summary of this compliance analysis.

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2)}

Create a concise executive summary focusing on:
1. Overall compliance status
2. Critical risks that need immediate attention
3. Recommended next steps

Return JSON with:
{{
  "executive_summary": "2-3 sentence overview for executives",
  "key_risks": ["top 3 compliance risks"],
  "immediate_actions": ["urgent actions needed"],
  "compliance_score": "percentage score out of 100"
}}

JSON response only:"""


class PromptTemplates:
    """Pre-defined prompt templates for common operations"""
    
    CONTRACT_ANALYSIS = {
        "system": "contract_analysis",
        "builder": PromptFormatter.build_contract_analysis_prompt
    }
    
    METADATA_EXTRACTION = {
        "system": "metadata_extraction", 
        "builder": PromptFormatter.build_metadata_extraction_prompt
    }
    
    COMPLIANCE_SUMMARY = {
        "system": "compliance_summary",
        "builder": PromptFormatter.build_compliance_summary_prompt
    }