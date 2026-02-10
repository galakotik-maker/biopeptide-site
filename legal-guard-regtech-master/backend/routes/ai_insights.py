"""
AI-powered insights and summaries for Legal Guard RegTech platform.

This module provides clean AI endpoints using IBM Granite for:
- Legal document summarization in plain language
- Quick risk assessment summaries  
- Contract clause explanations
"""

import json
import logging
import re
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from utils.ai_client import WatsonXClient, WatsonXConfig
from utils.ai_client.exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/ai", tags=["ai-insights"])

# Pydantic models
class DocumentSummaryRequest(BaseModel):
    text: str = Field(..., min_length=100, description="Legal document text to summarize")
    summary_type: str = Field(default="plain_language", description="Type of summary: 'plain_language', 'executive', 'risks'")

class DocumentSummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    risk_level: str
    word_count_reduction: str

class ClauseExplanationRequest(BaseModel):
    clause_text: str = Field(..., min_length=10, description="Legal clause to explain")
    
class ClauseExplanationResponse(BaseModel):
    plain_english: str
    potential_risks: list[str]
    recommendations: list[str]


# Dependency injection
def get_ai_client() -> WatsonXClient:
    """Get configured AI client."""
    return WatsonXClient()


@router.post("/summarize", response_model=DocumentSummaryResponse)
async def summarize_document(
    request: DocumentSummaryRequest,
    ai_client: WatsonXClient = Depends(get_ai_client)
):
    """
    Generate AI-powered plain language summary of legal documents.
    
    Perfect for making complex legal text accessible to non-lawyers.
    """
    try:
        logger.info(f"Generating {request.summary_type} summary for document")
        
        # Create summary prompt based on type
        if request.summary_type == "plain_language":
            prompt = f"""
You are a legal document translator who explains complex contracts in simple, everyday language.

DOCUMENT TO SUMMARIZE:
{request.text}

YOUR TASK:
Write a clear, easy-to-understand summary in plain English. Avoid legal jargon completely.

PROVIDE:
1. Document Type: What kind of document is this? (employment contract, service agreement, etc.)
2. Main Purpose: What is this document trying to accomplish?
3. Key Parties: Who are the main people or companies involved?
4. Important Terms: What are the most important rules, obligations, or benefits?
5. Critical Dates/Numbers: Any important deadlines, amounts, or time periods?

Write your response in simple paragraphs, like you're explaining it to a friend who has no legal background.

EXAMPLE FORMAT:
This is an employment contract between [Company] and [Employee]. The main purpose is to set the rules for the job, including what work needs to be done, how much the employee will be paid, and how the job can end.

The employee will work as a [position] and must focus full-time on company work. They will be paid [amount] per [period] and get [benefits]. 

Important rules include [key obligations]. The job can end if [termination conditions]. Both parties must follow [other important terms].
            """
        elif request.summary_type == "executive":
            prompt = f"""
You are a business analyst preparing an executive brief on this legal document.

DOCUMENT TO ANALYZE:
{request.text}

YOUR TASK:
Create a concise executive summary focused on business impact and decision-making.

COVER THESE AREAS:
1. Business Impact: How does this agreement affect operations, revenue, or strategy?
2. Financial Terms: Key monetary obligations, payments, costs, or benefits
3. Critical Obligations: What must each party do to fulfill this agreement?
4. Risk Factors: What business risks or exposures does this create?
5. Key Deadlines: Important dates, notice periods, or time-sensitive requirements
6. Performance Standards: Metrics, deliverables, or success criteria

Write in a professional tone suitable for executives who need to make informed business decisions.

Format as clear, actionable bullet points under relevant headings.
            """
        else:  # risks
            prompt = f"""
You are a risk management consultant analyzing this legal document for potential problems.

DOCUMENT TO REVIEW:
{request.text}

YOUR TASK:
Identify and explain the main risks and potential problems in this document.

ANALYZE THESE RISK CATEGORIES:
1. Legal Compliance Risks: What laws or regulations might be violated?
2. Financial Risks: Potential monetary losses, penalties, or unexpected costs
3. Operational Risks: How could this agreement disrupt business operations?
4. Relationship Risks: What could damage business relationships or reputation?
5. Enforcement Risks: Are there unclear terms that could lead to disputes?
6. Performance Risks: What happens if someone can't meet their obligations?

For each risk, explain:
- What could go wrong
- How likely it is to happen
- What the consequences might be
- What can be done to reduce the risk

Focus on realistic, practical business concerns rather than theoretical legal issues.
            """
        
        # Get AI response
        summary = ai_client._make_text_request(prompt)
        
        # Clean and process the AI response
        clean_summary = _process_ai_summary_response(summary, request.text, request.summary_type)
        
        # Extract key points (improved parsing for better readability)
        key_points = []
        
        # Try to extract from original JSON structure if it exists
        try:
            if summary.strip().startswith('{'):
                parsed = json.loads(summary)
                
                # Look for structured key points in various fields
                points_sources = []
                
                # Check common fields that might contain key points
                for field in ['key_obligations', 'key_rights', 'key_points', 'main_points', 'important_items']:
                    if field in parsed and isinstance(parsed[field], (dict, list)):
                        if isinstance(parsed[field], dict):
                            points_sources.extend(list(parsed[field].keys())[:5])
                        else:
                            points_sources.extend(parsed[field][:5])
                
                # Clean up the points for frontend display
                for point in points_sources[:5]:
                    if isinstance(point, str):
                        # Clean up the text
                        clean_point = point.replace('\\n', ' ').replace('\\"', '"')
                        # Remove common prefixes and clean formatting
                        clean_point = clean_point.replace('": "', ': ').strip()
                        # Remove trailing quotes and colons
                        clean_point = clean_point.rstrip('",').strip()
                        
                        if len(clean_point) > 10:  # Only meaningful points
                            key_points.append(clean_point)
                            
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
        
        # If no key points extracted from JSON, extract from the clean summary
        if not key_points:
            # Look for structured content in the summary
            key_points = _extract_key_points_from_summary(clean_summary, request.text, request.summary_type)
                        
        # Limit to 5 key points maximum
        key_points = key_points[:5]
        
        # Simple risk assessment based on keywords
        risk_keywords = ['penalty', 'liability', 'breach', 'termination', 'damages', 'default']
        risk_count = sum(1 for keyword in risk_keywords if keyword.lower() in request.text.lower())
        
        if risk_count >= 3:
            risk_level = "High"
        elif risk_count >= 1:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Calculate word reduction - fix negative percentages
        original_words = len(request.text.split())
        summary_words = len(clean_summary.split())
        
        if original_words > 0:
            if summary_words >= original_words:
                # If summary is longer than original, show as 0% reduction
                reduction = "0%"
            else:
                reduction_pct = ((original_words - summary_words) / original_words * 100)
                reduction = f"{reduction_pct:.0f}%"
        else:
            reduction = "0%"
        
        return DocumentSummaryResponse(
            summary=clean_summary.strip(),
            key_points=key_points[:5],  # Top 5 points
            risk_level=risk_level,
            word_count_reduction=reduction
        )
        
    except (APIError, AuthenticationError) as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in document summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/explain-clause", response_model=ClauseExplanationResponse)
async def explain_clause(
    request: ClauseExplanationRequest,
    ai_client: WatsonXClient = Depends(get_ai_client)
):
    """
    Explain a specific legal clause in plain English with risk assessment.
    
    Great for understanding complex contract terms quickly.
    """
    try:
        logger.info("Explaining legal clause")
        
        # Enhanced prompt with clear instructions to provide explanation, not echo
        prompt = f"""
Act as a legal translator who converts complex legal language into simple, everyday English.

LEGAL CLAUSE TO TRANSLATE:
"{request.clause_text}"

YOUR TASK:
Write a clear explanation in plain English that anyone can understand. Do NOT repeat or quote the original clause.

STRUCTURE YOUR RESPONSE AS:
1. Simple Explanation: [Write 1-2 sentences explaining what this clause means in everyday language]
2. Practical Impact: [Explain what this means for the people involved]
3. Potential Risks: [List 2-3 specific risks or problems that could arise]
4. Recommendations: [Give 2-3 practical suggestions for handling this clause]

EXAMPLE OF GOOD RESPONSE FORMAT:
Simple Explanation: This means the person receiving the information must keep it secret and can't share it with anyone else or use it for their own purposes.
Practical Impact: Anyone who gets confidential information must treat it like a secret and only use it for the specific purpose allowed in the agreement.
Potential Risks: 
- Risk of lawsuits if information is accidentally shared
- Possible financial penalties for breaching confidentiality
Recommendations:
- Set up clear procedures for handling sensitive information
- Train staff on what information must be kept confidential

Remember: Use simple words, short sentences, and avoid legal jargon completely.
        """
        
        explanation = ai_client._make_text_request(prompt)
        
        # Clean the response and extract meaningful content
        logger.debug(f"Raw AI response: {explanation}")
        
        # Remove any echoing of the original clause
        clean_explanation = explanation
        if request.clause_text.lower() in explanation.lower():
            # If the AI echoed back the original clause, remove it
            explanation_parts = explanation.split('\n')
            clean_parts = []
            for part in explanation_parts:
                # Skip parts that contain substantial portions of the original text
                if len(part.strip()) > 20 and not _contains_substantial_overlap(part.lower(), request.clause_text.lower()):
                    clean_parts.append(part.strip())
            clean_explanation = '\n'.join(clean_parts)
        
        # If the cleaned explanation is too short or still contains the original, provide a fallback
        if len(clean_explanation.strip()) < 50 or _contains_substantial_overlap(clean_explanation.lower(), request.clause_text.lower()):
            clean_explanation = _generate_fallback_explanation(request.clause_text)
        
        # Parse the explanation into structured parts
        lines = [line.strip() for line in clean_explanation.split('\n') if line.strip()]
        
        # Extract different sections based on the structured response
        main_explanation = []
        risks = []
        recommendations = []
        
        current_section = "explanation"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            line_lower = line.lower()
            if any(header in line_lower for header in ['simple explanation:', 'explanation:', 'what it means:']):
                current_section = "explanation"
                # Extract the content after the colon if present
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        main_explanation.append(content)
                continue
            elif any(header in line_lower for header in ['practical impact:', 'impact:', 'what this means:']):
                current_section = "explanation"
                if ':' in line:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        main_explanation.append(content)
                continue
            elif any(header in line_lower for header in ['potential risks:', 'risks:', 'problems:']):
                current_section = "risks"
                continue
            elif any(header in line_lower for header in ['recommendations:', 'advice:', 'suggestions:']):
                current_section = "recommendations"
                continue
            
            # Process content based on current section
            if current_section == "explanation" and not any(word in line_lower for word in ['risk', 'recommend', 'suggest']):
                # Skip numbered lists and bullet points for the main explanation
                clean_line = line.lstrip('1234567890.-•* ').strip()
                if len(clean_line) > 20:
                    main_explanation.append(clean_line)
            elif current_section == "risks" or any(word in line_lower for word in ['risk', 'problem', 'concern', 'warning', 'danger']):
                clean_line = line.lstrip('1234567890.-•* ').strip()
                if len(clean_line) > 10 and clean_line not in risks:
                    risks.append(clean_line)
            elif current_section == "recommendations" or any(word in line_lower for word in ['recommend', 'suggest', 'should', 'consider', 'advice', 'best']):
                clean_line = line.lstrip('1234567890.-•* ').strip()
                if len(clean_line) > 10 and clean_line not in recommendations:
                    recommendations.append(clean_line)
        
        # Construct the plain English explanation
        if main_explanation:
            plain_english = ' '.join(main_explanation)
        else:
            # Fallback: use the first substantial line
            substantial_lines = [line for line in lines if len(line) > 30]
            plain_english = substantial_lines[0] if substantial_lines else _generate_fallback_explanation(request.clause_text)
        
        # Clean up the plain English explanation
        plain_english = plain_english.strip()
        if not plain_english.endswith('.'):
            plain_english += '.'
        
        # Ensure we have some risks and recommendations
        if not risks:
            risks = _extract_implicit_risks(request.clause_text)
        
        if not recommendations:
            recommendations = _extract_implicit_recommendations(request.clause_text)
        
        return ClauseExplanationResponse(
            plain_english=plain_english,
            potential_risks=risks[:3],  # Top 3 risks
            recommendations=recommendations[:3]  # Top 3 recommendations
        )
        
    except (APIError, AuthenticationError) as e:
        logger.error(f"AI service error: {e}")
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in clause explanation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _contains_substantial_overlap(text1: str, text2: str, threshold: float = 0.7) -> bool:
    """Check if two texts have substantial overlap."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return False
    
    overlap = len(words1.intersection(words2))
    smaller_set_size = min(len(words1), len(words2))
    
    return (overlap / smaller_set_size) > threshold


def _generate_fallback_explanation(clause_text: str) -> str:
    """Generate a fallback explanation when AI fails."""
    clause_lower = clause_text.lower()
    
    if 'confidential' in clause_lower and 'disclose' in clause_lower:
        return "This clause creates a duty to keep certain information secret and not share it with others without permission."
    elif 'terminate' in clause_lower or 'termination' in clause_lower:
        return "This clause explains the conditions and procedures for ending the agreement."
    elif 'payment' in clause_lower or 'compensation' in clause_lower:
        return "This clause outlines how and when payments will be made under the agreement."
    elif 'liability' in clause_lower or 'damages' in clause_lower:
        return "This clause addresses who is responsible for losses or damages that may occur."
    elif 'intellectual property' in clause_lower or 'copyright' in clause_lower:
        return "This clause deals with ownership and rights to creative works or innovations."
    else:
        return "This clause establishes specific rights, obligations, or procedures that the parties must follow."


def _extract_implicit_risks(clause_text: str) -> list[str]:
    """Extract implied risks from the clause text."""
    clause_lower = clause_text.lower()
    risks = []
    
    if 'confidential' in clause_lower:
        risks.append("Risk of legal action if confidential information is accidentally disclosed")
        risks.append("Potential liability for damages if confidentiality is breached")
    
    if 'terminate' in clause_lower:
        risks.append("Risk of unexpected contract termination")
        risks.append("Potential loss of business relationship or revenue")
    
    if 'liability' in clause_lower or 'damages' in clause_lower:
        risks.append("Financial exposure to claims and damages")
        risks.append("Potential for expensive legal disputes")
    
    return risks


def _extract_implicit_recommendations(clause_text: str) -> list[str]:
    """Extract implied recommendations from the clause text."""
    clause_lower = clause_text.lower()
    recommendations = []
    
    if 'confidential' in clause_lower:
        recommendations.append("Implement clear procedures for handling confidential information")
        recommendations.append("Train employees on confidentiality requirements")
    
    if 'terminate' in clause_lower:
        recommendations.append("Understand the termination conditions and notice requirements")
        recommendations.append("Keep detailed records of contract performance")
    
    if 'liability' in clause_lower:
        recommendations.append("Consider appropriate insurance coverage")
        recommendations.append("Review and understand the scope of potential liability")
    
    return recommendations


def _extract_key_points_from_summary(summary: str, original_text: str, summary_type: str) -> list[str]:
    """Extract key points from the summary text based on the summary type."""
    key_points = []
    
    # First, try to find structured content (bullets, numbered lists, etc.)
    lines = summary.split('\n')
    for line in lines:
        line = line.strip()
        # Look for numbered items, bullet points, or lines with colons
        if (line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')) or 
            any(char.isdigit() and '.' in line for char in line[:3])):
            
            clean_line = line.lstrip('-•* 0123456789.').strip()
            if len(clean_line) > 20:  # Meaningful content
                key_points.append(clean_line)
                if len(key_points) >= 5:
                    break
    
    # If no structured content found, extract from sentences
    if not key_points:
        sentences = summary.split('. ')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 200:  # Good length for key points
                # Look for sentences that mention key contract elements based on summary type
                if summary_type == "plain_language":
                    key_indicators = [
                        'contract', 'agreement', 'parties', 'employer', 'employee', 
                        'duties', 'responsibilities', 'wages', 'termination', 'duration',
                        'rights', 'obligations', 'payment', 'benefits', 'terms'
                    ]
                elif summary_type == "executive":
                    key_indicators = [
                        'business', 'financial', 'revenue', 'cost', 'deadline', 'milestone',
                        'performance', 'deliverable', 'obligation', 'commitment', 'risk'
                    ]
                else:  # risks
                    key_indicators = [
                        'risk', 'problem', 'concern', 'liability', 'exposure', 'compliance',
                        'violation', 'penalty', 'dispute', 'failure', 'breach'
                    ]
                
                if any(indicator in sentence.lower() for indicator in key_indicators):
                    # Clean up the sentence for display
                    clean_sentence = sentence.replace('The ', '').replace('This ', '')
                    if not clean_sentence.endswith('.'):
                        clean_sentence += '.'
                    key_points.append(clean_sentence)
                    
                    if len(key_points) >= 5:
                        break
    
    # Final fallback: create key points from main topics in original text
    if not key_points:
        key_points = _generate_fallback_key_points(original_text, summary_type)
    
    return key_points[:5]


def _generate_fallback_key_points(original_text: str, summary_type: str) -> list[str]:
    """Generate fallback key points when extraction fails."""
    text_lower = original_text.lower()
    points = []
    
    if summary_type == "plain_language":
        if 'employment' in text_lower and 'agreement' in text_lower:
            points.append('This is an employment agreement between a company and employee')
        if 'duties' in text_lower or 'responsibilities' in text_lower:
            points.append('Employee duties and responsibilities are clearly defined')
        if 'salary' in text_lower or 'wage' in text_lower or 'compensation' in text_lower:
            points.append('Compensation and payment terms are specified')
        if 'termination' in text_lower:
            points.append('Termination conditions and procedures are established')
        if 'confidential' in text_lower:
            points.append('Confidentiality obligations are included')
    
    elif summary_type == "executive":
        if 'rm' in text_lower or 'dollar' in text_lower or 'payment' in text_lower:
            points.append('Financial terms and payment obligations defined')
        if 'termination' in text_lower or 'notice' in text_lower:
            points.append('Termination procedures and notice requirements specified')
        if 'full-time' in text_lower or 'duties' in text_lower:
            points.append('Employee commitment and performance expectations outlined')
        if 'confidential' in text_lower or 'proprietary' in text_lower:
            points.append('Intellectual property and confidentiality protections included')
    
    else:  # risks
        if 'termination' in text_lower:
            points.append('Risk of employment termination with notice requirements')
        if 'confidential' in text_lower:
            points.append('Risk of confidentiality breaches and potential legal action')
        if 'misconduct' in text_lower or 'breach' in text_lower:
            points.append('Risk of immediate termination for cause')
        if 'malaysia' in text_lower:
            points.append('Governed by Malaysian law - compliance with local regulations required')
    
    # Generic fallback if no specific points found
    if not points:
        points = [
            'Document contains legal terms and obligations',
            'Parties have specific rights and responsibilities',
            'Agreement includes termination and compliance provisions'
        ]
    
    return points[:5]


def _process_ai_summary_response(summary: str, original_text: str, summary_type: str) -> str:
    """Process and clean AI summary response, handling JSON and poor responses."""
    
    # First, check if the response is too short or obviously bad
    if len(summary.strip()) < 50:
        logger.warning("AI response too short, generating fallback summary")
        return _generate_fallback_summary(original_text, summary_type)
    
    # Handle case where AI returns JSON despite asking for plain text
    if summary.strip().startswith('{'):
        try:
            parsed = json.loads(summary)
            
            # Extract meaningful summary text from various possible fields
            extracted_text = _extract_text_from_json_response(parsed)
            
            if extracted_text and len(extracted_text) > 50:
                clean_summary = extracted_text
            else:
                logger.warning("Could not extract meaningful text from JSON response, generating fallback")
                clean_summary = _generate_fallback_summary(original_text, summary_type)
                
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.warning(f"Failed to parse JSON response: {e}, generating fallback")
            clean_summary = _generate_fallback_summary(original_text, summary_type)
    else:
        # Plain text response - clean it up
        clean_summary = summary.strip()
    
    # Clean up the summary text
    if clean_summary:
        # Remove JSON-like formatting artifacts
        clean_summary = clean_summary.replace('\\n', ' ').replace('\\"', '"')
        clean_summary = re.sub(r'\s+', ' ', clean_summary)  # Multiple spaces to single
        
        # Ensure it's a proper sentence
        if not clean_summary.endswith('.'):
            clean_summary += '.'
    
    # Final quality check - if summary is still poor, generate fallback
    if len(clean_summary.strip()) < 100 or _is_poor_quality_summary(clean_summary):
        logger.warning("Summary quality check failed, generating fallback")
        clean_summary = _generate_fallback_summary(original_text, summary_type)
    
    return clean_summary


def _extract_text_from_json_response(parsed: dict) -> str:
    """Extract meaningful text from a JSON response."""
    
    # Try to extract meaningful summary text from various possible fields
    if 'summary' in parsed:
        if isinstance(parsed['summary'], str):
            return parsed['summary']
        elif isinstance(parsed['summary'], dict):
            # If summary is a dict, extract first meaningful text
            return str(list(parsed['summary'].values())[0]) if parsed['summary'] else ""
    
    # Try other common fields
    for field in ['text', 'content', 'description', 'explanation', 'analysis']:
        if field in parsed and isinstance(parsed[field], str) and len(parsed[field]) > 50:
            return parsed[field]
    
    # Extract from nested structures
    descriptive_fields = ['summary', 'text', 'content', 'description', 'explanation']
    extracted_parts = []
    
    for key, value in parsed.items():
        if isinstance(value, str) and len(value) > 50:  # Meaningful text content
            # Skip obviously malformed or repetitive content
            if not _is_repetitive_content(value):
                extracted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        elif isinstance(value, dict):
            # If it's a nested dict, extract some meaningful content
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str) and len(sub_value) > 30:
                    if not _is_repetitive_content(sub_value):
                        extracted_parts.append(f"{sub_key.replace('_', ' ').title()}: {sub_value}")
                        break  # Just take the first meaningful one
    
    if extracted_parts:
        return ". ".join(extracted_parts[:3])  # Limit to first 3 meaningful items
    
    return ""


def _is_repetitive_content(text: str) -> bool:
    """Check if text content is repetitive or malformed."""
    # Check for excessive repetition
    words = text.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If any word appears more than 30% of the time, it's likely repetitive
        for count in word_counts.values():
            if count / len(words) > 0.3:
                return True
    
    # Check for obvious JSON artifacts
    json_artifacts = ['{', '}', '":', '",', '\\"', '\\n']
    artifact_count = sum(1 for artifact in json_artifacts if artifact in text)
    if artifact_count > 5:  # Too many JSON artifacts
        return True
    
    return False


def _is_poor_quality_summary(summary: str) -> bool:
    """Check if a summary is of poor quality."""
    
    # Check for generic fallback phrases that indicate poor AI response
    poor_indicators = [
        "this is a legal document",
        "various terms and conditions",
        "should be reviewed carefully",
        "sets out the terms",
        "document contains"
    ]
    
    summary_lower = summary.lower()
    if any(indicator in summary_lower for indicator in poor_indicators):
        return True
    
    # Check for excessive repetition within the summary
    sentences = summary.split('.')
    if len(sentences) > 3:
        # Check if sentences are too similar
        for i, sentence1 in enumerate(sentences):
            for sentence2 in sentences[i+1:]:
                if len(sentence1.strip()) > 10 and len(sentence2.strip()) > 10:
                    # Simple similarity check
                    words1 = set(sentence1.lower().split())
                    words2 = set(sentence2.lower().split())
                    if len(words1.intersection(words2)) / max(len(words1), len(words2)) > 0.7:
                        return True
    
    return False


def _generate_fallback_summary(original_text: str, summary_type: str) -> str:
    """Generate a quality fallback summary when AI fails."""
    
    text_lower = original_text.lower()
    
    # Determine document type
    doc_type = "legal document"
    if 'employment' in text_lower and 'agreement' in text_lower:
        doc_type = "employment agreement"
    elif 'service' in text_lower and 'agreement' in text_lower:
        doc_type = "service agreement"
    elif 'privacy' in text_lower and ('policy' in text_lower or 'notice' in text_lower):
        doc_type = "privacy policy"
    elif 'confidentiality' in text_lower or 'non-disclosure' in text_lower:
        doc_type = "confidentiality agreement"
    
    # Extract key information
    parties = []
    if 'between' in text_lower:
        # Try to extract party names
        between_match = re.search(r'between\s+([^,\n]+?)(?:\s+and\s+([^,\n]+?))?(?:\s*\(|\.|\n)', text_lower)
        if between_match:
            parties = [party.strip() for party in between_match.groups() if party]
    
    # Extract key amounts
    amounts = re.findall(r'rm\s*(\d+(?:,\d+)*)', text_lower)
    amounts.extend(re.findall(r'\$(\d+(?:,\d+)*)', text_lower))
    amounts.extend(re.findall(r'(\d+)\s*days?', text_lower))
    
    # Build summary based on type
    if summary_type == "plain_language":
        summary = f"This is an {doc_type}"
        
        if parties and len(parties) >= 2:
            summary += f" between {parties[0]} and {parties[1]}"
        elif parties:
            summary += f" involving {parties[0]}"
        
        summary += ". "
        
        # Add key terms based on document content
        if 'employment' in text_lower:
            if amounts:
                summary += f"The employee will receive compensation and benefits as specified. "
            summary += "The agreement covers job duties, termination procedures, and confidentiality requirements."
        elif 'service' in text_lower:
            summary += "The agreement outlines services to be provided, payment terms, and delivery requirements."
        elif 'confidential' in text_lower:
            summary += "The agreement establishes obligations to keep certain information confidential and not disclose it to third parties."
        else:
            summary += "The document establishes rights, obligations, and procedures that the parties must follow."
            
    elif summary_type == "executive":
        summary = f"Executive Summary: This {doc_type} creates business obligations and commitments. "
        
        if amounts:
            summary += f"Key financial terms include amounts of {', '.join(amounts[:3])}. "
        
        if 'termination' in text_lower:
            summary += "The agreement includes termination procedures and notice requirements. "
        
        if 'confidential' in text_lower:
            summary += "Confidentiality and intellectual property protections are established. "
        
        summary += "Regular review and compliance monitoring are recommended."
        
    else:  # risks
        summary = f"Risk Analysis: This {doc_type} creates several potential business risks. "
        
        risks = []
        if 'termination' in text_lower:
            risks.append("contract termination risks")
        if 'confidential' in text_lower:
            risks.append("confidentiality breach risks")
        if 'liability' in text_lower or 'damages' in text_lower:
            risks.append("financial liability exposure")
        if 'compliance' in text_lower or 'law' in text_lower:
            risks.append("regulatory compliance risks")
        
        if risks:
            summary += f"Primary concerns include {', '.join(risks)}. "
        
        summary += "Legal review and appropriate risk mitigation measures are recommended."
    
    return summary


@router.get("/health")
async def health_check():
    """Simple health check for AI services."""
    try:
        ai_client = get_ai_client()
        # Simple test prompt
        test_response = ai_client._make_text_request("Hello, this is a test. Respond with 'OK'.")
        return {"status": "healthy", "ai_service": "connected"}
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
