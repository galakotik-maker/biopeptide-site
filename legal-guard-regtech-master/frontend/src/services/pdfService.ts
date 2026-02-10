import jsPDF from 'jspdf';

interface FlaggedClause {
    clause_text: string;
    issue: string;
    severity: 'low' | 'medium' | 'high';
}

interface ComplianceIssue {
    law: string;
    missing_requirements: string[];
    recommendations: string[];
}

interface AnalysisResult {
    summary: string;
    flagged_clauses: FlaggedClause[];
    compliance_issues: ComplianceIssue[];
    jurisdiction: string;
}

interface ComplianceRiskScore {
    overall_score: number;
    financial_risk_estimate: number;
    violation_categories: string[];
    jurisdiction_risks: Record<string, number>;
}

export class PDFReportGenerator {
    private doc: jsPDF;
    private pageHeight: number;
    private pageWidth: number;
    private margin: number;
    private currentY: number;
    private lineHeight: number;

    constructor() {
        this.doc = new jsPDF();
        this.pageHeight = this.doc.internal.pageSize.height;
        this.pageWidth = this.doc.internal.pageSize.width;
        this.margin = 20;
        this.currentY = this.margin;
        this.lineHeight = 6;
    }

    private addNewPageIfNeeded(requiredHeight: number): void {
        if (this.currentY + requiredHeight > this.pageHeight - 40) {
            this.doc.addPage();
            this.currentY = this.margin;
        }
    }

    private getJurisdictionName(code: string): string {
        const jurisdictionNames: Record<string, string> = {
            MY: 'Malaysia',
            SG: 'Singapore',
            EU: 'European Union',
            US: 'United States',
            UK: 'United Kingdom',
            AU: 'Australia',
            CA: 'Canada'
        };
        return jurisdictionNames[code] || code;
    }

    private getSeverityColor(severity: string): [number, number, number] {
        switch (severity) {
            case 'high':
                return [220, 38, 127];
            case 'medium':
                return [245, 158, 11];
            case 'low':
                return [34, 197, 94];
            default:
                return [107, 114, 128];
        }
    }

    private getRiskScoreColor(score: number): [number, number, number] {
        if (score >= 80) return [220, 38, 127];
        if (score >= 60) return [245, 158, 11];
        if (score >= 40) return [234, 179, 8];
        return [34, 197, 94];
    }

    private getRiskLevel(score: number): string {
        if (score >= 80) return 'HIGH RISK';
        if (score >= 60) return 'MEDIUM RISK';
        if (score >= 40) return 'LOW-MEDIUM RISK';
        return 'LOW RISK';
    }

    private cleanText(text: string): string {
        // Remove any problematic characters and normalize text
        return text
            .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII characters
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
    }

    private wrapText(text: string, maxWidth: number, fontSize: number = 12): string[] {
        // Clean the text first
        const cleanedText = this.cleanText(text);
        
        this.doc.setFontSize(fontSize);
        const words = cleanedText.split(' ');
        const lines: string[] = [];
        let currentLine = '';

        for (const word of words) {
            const testLine = currentLine + (currentLine ? ' ' : '') + word;
            const textWidth = this.doc.getStringUnitWidth(testLine) * fontSize / this.doc.internal.scaleFactor;
            
            if (textWidth > maxWidth && currentLine) {
                lines.push(currentLine);
                currentLine = word;
            } else {
                currentLine = testLine;
            }
        }
        
        if (currentLine) {
            lines.push(currentLine);
        }
        
        return lines;
    }

    private addHeader(): void {
        // Clean gradient background
        this.doc.setFillColor(59, 130, 246);
        this.doc.rect(0, 0, this.pageWidth, 35, 'F');
        
        this.doc.setFillColor(79, 150, 255);
        this.doc.rect(0, 0, this.pageWidth, 25, 'F');

        // Company name - use only ASCII characters
        this.doc.setFontSize(26);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(255, 255, 255);
        this.doc.text('LegalGuard RegTech', this.margin, 20);
        
        // Report title
        this.doc.setFontSize(14);
        this.doc.setFont('helvetica', 'normal');
        this.doc.text('Contract Analysis Report', this.margin, 30);
        
        this.currentY = 50;
        
        // Date and status
        this.doc.setFontSize(11);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(107, 114, 128);
        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        this.doc.text(`Generated on: ${currentDate}`, this.margin, this.currentY);
        
        // Status badge
        this.doc.setFillColor(34, 197, 94);
        this.doc.roundedRect(this.pageWidth - 80, this.currentY - 6, 55, 12, 3, 3, 'F');
        this.doc.setFontSize(9);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(255, 255, 255);
        this.doc.text('ANALYSIS COMPLETE', this.pageWidth - 77, this.currentY);
        
        this.currentY += 20;
        
        // Separator line
        this.doc.setDrawColor(229, 231, 235);
        this.doc.setLineWidth(0.5);
        this.doc.line(this.margin, this.currentY, this.pageWidth - this.margin, this.currentY);
        this.currentY += 15;
    }

    private addSummarySection(result: AnalysisResult): void {
        this.addNewPageIfNeeded(50);
        
        // Section header - use simple text instead of emoji
        this.doc.setFontSize(18);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(59, 130, 246);
        this.doc.text('Executive Summary', this.margin, this.currentY);
        this.currentY += 15;
        
        // Jurisdiction info
        this.doc.setFillColor(245, 245, 245);
        this.doc.setDrawColor(200, 200, 200);
        this.doc.roundedRect(this.margin, this.currentY - 5, 100, 16, 3, 3, 'FD');
        
        this.doc.setFontSize(10);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(107, 114, 128);
        this.doc.text('JURISDICTION', this.margin + 5, this.currentY);
        
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(0, 0, 0);
        this.doc.text(this.getJurisdictionName(result.jurisdiction), this.margin + 5, this.currentY + 8);
        this.currentY += 25;
        
        // Summary text
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(55, 65, 81);
        const summaryLines = this.wrapText(result.summary, this.pageWidth - 2 * this.margin, 12);
        
        for (const line of summaryLines) {
            this.addNewPageIfNeeded(this.lineHeight + 2);
            this.doc.text(line, this.margin, this.currentY);
            this.currentY += this.lineHeight + 2;
        }
        
        this.currentY += 15;
    }

    private addRiskScoreSection(riskScore: ComplianceRiskScore): void {
        this.addNewPageIfNeeded(80);
        
        // Section header
        this.doc.setFontSize(18);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(147, 51, 234);
        this.doc.text('Compliance Risk Assessment', this.margin, this.currentY);
        this.currentY += 20;
        
        // Risk score card
        const cardWidth = this.pageWidth - 2 * this.margin;
        const cardHeight = 45;
        const cardX = this.margin;
        const cardY = this.currentY - 5;
        
        // Card background
        this.doc.setFillColor(248, 250, 252);
        this.doc.setDrawColor(226, 232, 240);
        this.doc.roundedRect(cardX, cardY, cardWidth, cardHeight, 5, 5, 'FD');
        
        // Risk score circle
        const circleRadius = 20;
        const circleX = cardX + 30;
        const circleY = cardY + cardHeight/2;
        
        const [r, g, b] = this.getRiskScoreColor(riskScore.overall_score);
        this.doc.setFillColor(r, g, b);
        this.doc.circle(circleX, circleY, circleRadius, 'F');
        
        // Risk score text
        this.doc.setFontSize(16);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(255, 255, 255);
        this.doc.text(`${riskScore.overall_score}%`, circleX, circleY + 2, { align: 'center' });
        
        // Risk level
        this.doc.setFontSize(12);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(0, 0, 0);
        this.doc.text(this.getRiskLevel(riskScore.overall_score), circleX + 35, circleY - 8);
        
        // Financial impact
        this.doc.setFontSize(10);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(107, 114, 128);
        this.doc.text('Estimated Financial Impact:', circleX + 35, circleY + 2);
        
        this.doc.setFontSize(14);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(220, 38, 127);
        const financialRisk = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(riskScore.financial_risk_estimate);
        this.doc.text(financialRisk, circleX + 35, circleY + 12);
        
        this.currentY += cardHeight + 20;
        
        // Violation categories
        if (riskScore.violation_categories.length > 0) {
            this.doc.setFontSize(14);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(220, 38, 127);
            this.doc.text('Violation Categories:', this.margin, this.currentY);
            this.currentY += 12;
            
            for (const category of riskScore.violation_categories) {
                this.addNewPageIfNeeded(15);
                
                // Category badge
                this.doc.setFillColor(254, 242, 242);
                this.doc.setDrawColor(254, 202, 202);
                const categoryWidth = Math.max(60, this.doc.getStringUnitWidth(category) * 11 / this.doc.internal.scaleFactor + 10);
                this.doc.roundedRect(this.margin, this.currentY - 4, categoryWidth, 12, 2, 2, 'FD');
                
                this.doc.setFontSize(11);
                this.doc.setFont('helvetica', 'bold');
                this.doc.setTextColor(185, 28, 28);
                this.doc.text(this.cleanText(category), this.margin + 5, this.currentY + 3);
                
                this.currentY += 18;
            }
        }
        
        this.currentY += 10;
    }

    private addFlaggedClausesSection(flaggedClauses: FlaggedClause[]): void {
        this.addNewPageIfNeeded(40);
        
        // Section header
        this.doc.setFontSize(18);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(245, 158, 11);
        this.doc.text(`Flagged Clauses (${flaggedClauses.length})`, this.margin, this.currentY);
        this.currentY += 20;
        
        if (flaggedClauses.length === 0) {
            // No issues found
            this.doc.setFillColor(240, 253, 244);
            this.doc.setDrawColor(167, 243, 208);
            this.doc.roundedRect(this.margin, this.currentY - 5, this.pageWidth - 2 * this.margin, 25, 5, 5, 'FD');
            
            this.doc.setFontSize(14);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(34, 197, 94);
            this.doc.text('No flagged clauses found', this.margin + 10, this.currentY + 5);
            
            this.doc.setFontSize(11);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(21, 128, 61);
            this.doc.text('All clauses appear to be compliant with regulatory requirements', this.margin + 10, this.currentY + 15);
            
            this.currentY += 35;
            return;
        }
        
        for (let i = 0; i < flaggedClauses.length; i++) {
            const clause = flaggedClauses[i];
            this.addNewPageIfNeeded(60);
            
            // Clause header
            this.doc.setFillColor(254, 249, 195);
            this.doc.setDrawColor(251, 191, 36);
            this.doc.roundedRect(this.margin, this.currentY - 5, this.pageWidth - 2 * this.margin, 15, 3, 3, 'FD');
            
            this.doc.setFontSize(14);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(0, 0, 0);
            this.doc.text(`Clause ${i + 1}`, this.margin + 10, this.currentY + 5);
            
            // Severity badge
            const [r, g, b] = this.getSeverityColor(clause.severity);
            this.doc.setFillColor(r, g, b);
            const severityText = clause.severity.toUpperCase();
            const severityWidth = this.doc.getStringUnitWidth(severityText) * 10 / this.doc.internal.scaleFactor + 8;
            this.doc.roundedRect(this.pageWidth - this.margin - severityWidth - 10, this.currentY - 2, severityWidth, 10, 2, 2, 'F');
            this.doc.setTextColor(255, 255, 255);
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'bold');
            this.doc.text(severityText, this.pageWidth - this.margin - severityWidth - 6, this.currentY + 3);
            
            this.currentY += 20;
            
            // Issue description
            this.doc.setFontSize(12);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(220, 38, 127);
            this.doc.text('Issue:', this.margin + 5, this.currentY);
            this.currentY += 8;
            
            this.doc.setFontSize(11);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(55, 65, 81);
            const issueLines = this.wrapText(clause.issue, this.pageWidth - 2 * this.margin - 10, 11);
            for (const line of issueLines) {
                this.addNewPageIfNeeded(this.lineHeight + 1);
                this.doc.text(line, this.margin + 10, this.currentY);
                this.currentY += this.lineHeight + 1;
            }
            
            this.currentY += 5;
            
            // Clause text
            this.doc.setFontSize(12);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(75, 85, 99);
            this.doc.text('Clause Text:', this.margin + 5, this.currentY);
            this.currentY += 8;
            
            this.doc.setFont('helvetica', 'italic');
            this.doc.setTextColor(107, 114, 128);
            const clauseText = clause.clause_text.length > 400 
                ? clause.clause_text.substring(0, 400) + '...' 
                : clause.clause_text;
            const clauseLines = this.wrapText(`"${clauseText}"`, this.pageWidth - 2 * this.margin - 10, 11);
            
            for (const line of clauseLines) {
                this.addNewPageIfNeeded(this.lineHeight + 1);
                this.doc.text(line, this.margin + 10, this.currentY);
                this.currentY += this.lineHeight + 1;
            }
            
            this.currentY += 15;
        }
    }

    private addComplianceIssuesSection(complianceIssues: ComplianceIssue[]): void {
        this.addNewPageIfNeeded(40);
        
        // Section header
        this.doc.setFontSize(18);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(147, 51, 234);
        this.doc.text(`Compliance Issues (${complianceIssues.length})`, this.margin, this.currentY);
        this.currentY += 20;
        
        if (complianceIssues.length === 0) {
            // No issues
            this.doc.setFillColor(240, 253, 244);
            this.doc.setDrawColor(167, 243, 208);
            this.doc.roundedRect(this.margin, this.currentY - 5, this.pageWidth - 2 * this.margin, 25, 5, 5, 'FD');
            
            this.doc.setFontSize(14);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(34, 197, 94);
            this.doc.text('No compliance issues found', this.margin + 10, this.currentY + 5);
            
            this.doc.setFontSize(11);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(21, 128, 61);
            this.doc.text('Contract meets all regulatory requirements', this.margin + 10, this.currentY + 15);
            
            this.currentY += 35;
            return;
        }
        
        for (const issue of complianceIssues) {
            this.addNewPageIfNeeded(70);
            
            // Law header
            this.doc.setFillColor(239, 246, 255);
            this.doc.setDrawColor(147, 197, 253);
            this.doc.roundedRect(this.margin, this.currentY - 5, this.pageWidth - 2 * this.margin, 20, 3, 3, 'FD');
            
            this.doc.setFontSize(16);
            this.doc.setFont('helvetica', 'bold');
            this.doc.setTextColor(59, 130, 246);
            this.doc.text(this.cleanText(issue.law), this.margin + 10, this.currentY + 8);
            this.currentY += 25;
            
            // Missing requirements
            if (issue.missing_requirements.length > 0) {
                this.doc.setFontSize(14);
                this.doc.setFont('helvetica', 'bold');
                this.doc.setTextColor(220, 38, 127);
                this.doc.text('Missing Requirements:', this.margin + 5, this.currentY);
                this.currentY += 12;
                
                for (const requirement of issue.missing_requirements) {
                    this.addNewPageIfNeeded(20);
                    
                    this.doc.setFontSize(11);
                    this.doc.setFont('helvetica', 'normal');
                    this.doc.setTextColor(55, 65, 81);
                    
                    const reqLines = this.wrapText(`• ${requirement}`, this.pageWidth - 2 * this.margin - 15, 11);
                    for (const line of reqLines) {
                        this.addNewPageIfNeeded(this.lineHeight + 1);
                        this.doc.text(line, this.margin + 15, this.currentY);
                        this.currentY += this.lineHeight + 1;
                    }
                    this.currentY += 2;
                }
                this.currentY += 8;
            }
            
            // Recommendations
            if (issue.recommendations.length > 0) {
                this.doc.setFontSize(14);
                this.doc.setFont('helvetica', 'bold');
                this.doc.setTextColor(34, 197, 94);
                this.doc.text('Recommendations:', this.margin + 5, this.currentY);
                this.currentY += 12;
                
                for (const recommendation of issue.recommendations) {
                    this.addNewPageIfNeeded(20);
                    
                    this.doc.setFontSize(11);
                    this.doc.setFont('helvetica', 'normal');
                    this.doc.setTextColor(55, 65, 81);
                    
                    const recLines = this.wrapText(`• ${recommendation}`, this.pageWidth - 2 * this.margin - 15, 11);
                    for (const line of recLines) {
                        this.addNewPageIfNeeded(this.lineHeight + 1);
                        this.doc.text(line, this.margin + 15, this.currentY);
                        this.currentY += this.lineHeight + 1;
                    }
                    this.currentY += 2;
                }
                this.currentY += 8;
            }
            
            this.currentY += 15;
        }
    }

    private addFooter(): void {
        const pageCount = (this.doc as any).getNumberOfPages();
        
        for (let i = 1; i <= pageCount; i++) {
            this.doc.setPage(i);
            
            // Footer background
            this.doc.setFillColor(248, 250, 252);
            this.doc.rect(0, this.pageHeight - 25, this.pageWidth, 25, 'F');
            
            // Footer line
            this.doc.setDrawColor(226, 232, 240);
            this.doc.setLineWidth(0.5);
            this.doc.line(this.margin, this.pageHeight - 25, this.pageWidth - this.margin, this.pageHeight - 25);
            
            // Footer text
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(107, 114, 128);
            this.doc.text('LegalGuard RegTech - Contract Analysis Report', this.margin, this.pageHeight - 15);
            
            // Confidentiality notice
            this.doc.setFontSize(8);
            this.doc.setTextColor(156, 163, 175);
            this.doc.text('CONFIDENTIAL - This report contains proprietary analysis', this.margin, this.pageHeight - 8);
            
            // Page number
            this.doc.setFontSize(9);
            this.doc.setTextColor(107, 114, 128);
            this.doc.text(`Page ${i} of ${pageCount}`, this.pageWidth - this.margin, this.pageHeight - 15, { align: 'right' });
        }
    }

    public generateReport(
        result: AnalysisResult, 
        riskScore?: ComplianceRiskScore | null,
        filename?: string
    ): void {
        // Reset position
        this.currentY = this.margin;
        
        // Add sections
        this.addHeader();
        this.addSummarySection(result);
        
        if (riskScore) {
            this.addRiskScoreSection(riskScore);
        }
        
        this.addFlaggedClausesSection(result.flagged_clauses);
        this.addComplianceIssuesSection(result.compliance_issues);
        
        // Add footer to all pages
        this.addFooter();
        
        // Generate filename with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const jurisdictionCode = result.jurisdiction.replace(/[^A-Z]/g, '');
        const defaultFilename = `LegalGuard-Analysis-${jurisdictionCode}-${timestamp}.pdf`;
        
        // Download the PDF
        this.doc.save(filename || defaultFilename);
    }
}

export const downloadAnalysisReport = (
    result: AnalysisResult, 
    riskScore?: ComplianceRiskScore | null,
    filename?: string
): void => {
    const generator = new PDFReportGenerator();
    generator.generateReport(result, riskScore, filename);
};