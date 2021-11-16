create_ei = {
    "tender": {
        "title": "tender.title",
        "description": "tender.description",
        "classification": {
            "id": "50100000-6"
        }
    },
    "planning": {
        "budget": {
            "period": {
                "startDate": "2020-02-01T11:07:00Z",
                "endDate": "2021-12-31T00:00:00Z"
            }
        },
        "rationale": "planning.budget.rationale"
    },
    "buyer": {
        "name": "Buyer name",
        "identifier": {
            "scheme": "MD-IDNO",
            "id": "1",
            "legalName": "legal_name",
            "uri": "uri"
        },
        "contactPoint": {
            "name": "contactPoint/name",
            "email": "contactPoint/email",
            "telephone": "contactPoint/456-95-96",
            "faxNumber": "fax-number",
            "url": "url"
        },
        "additionalIdentifiers": [{
            "scheme": "md-idno",
            "id": "445521",
            "legalName": "legalName",
            "uri": "uri"
        }],
        "address": {
            "streetAddress": "street address",
            "postalCode": "postalCode",
            "addressDetails": {
                "country": {
                    "id": "MD"
                },
                "region": {
                    "id": "0101000"
                },
                "locality": {
                    "scheme": "CUATM",
                    "id": "0101000",
                    "description": "locality/description",
                    "uri": ""
                }
            }
        },
        "details": {
            "typeOfBuyer": "MINISTRY",
            "mainGeneralActivity": "HEALTH",
            "mainSectoralActivity": "WATER"
        }
    }}
