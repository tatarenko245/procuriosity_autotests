create_pn = {
    "planning": {
        "rationale": "reason for budget",
        "budget": {
            "description": "budgetBreakdown description",
            "budgetBreakdown": [

           {
                    "id": "{{fs-id}}",
                    "amount": {
                        "amount": 90,
                        "currency": "EUR"
                    }
                }
            ]
        }
    },
    "tender": {
        "title": "tender title",
        "description": "tender description",
        "legalBasis": "NATIONAL_PROCUREMENT_LAW",
        "procurementMethodRationale": "tender/procurementMethodRationale",
        "procurementMethodAdditionalInfo": "tender/procurementMethodAdditionalInfo",
        "tenderPeriod": {
            "startDate": "2020-12-01T00:07:00Z"
        },

        "documents": [
            {
                "id": "{{doc}}",
                "documentType": "evaluationCriteria",
                "title": "document title",
                "description": "document description"

            }
        ]
    }
}