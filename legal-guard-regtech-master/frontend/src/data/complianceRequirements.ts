export const complianceChecklist = {
    employment_laws_my: {
        requirements: [
            "Termination_Clause",
            "Minimum_Wage_Compliance",
            "Overtime_Provisions",
            "Annual_Leave_Entitlement",
            "Notice_Period_Requirements"
        ]
    },
    data_protection: {
        requirements: [
            "Data_Processing_Notice",
            "Consent_Mechanism",
            "Data_Retention_Policy"
        ]
    }
};

export type ComplianceChecklistData = typeof complianceChecklist;