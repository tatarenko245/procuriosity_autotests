create_fa = {
    "tender": {
        "title": "tender.title AP",
        "value": {
            "currency": "EUR"
        },
        "classification": {
            "id": "50100000-6"
        },
        "description": "tender description AP",
        "legalBasis": "DIRECTIVE_2009_81_EC",
        "procurementMethodRationale": "tender/procurementMethodRationale AP",
        "tenderPeriod": {
            "startDate": "2020-12-01T11:07:00Z"
        },
        "contractPeriod": {
            "startDate": "2021-12-10T09:30:00Z",
            "endDate": "2021-12-11T10:30:00Z"
        },
        "procuringEntity": {
            "name": "name of PE from AP (future cpb)",
            "identifier": {
                "scheme": "MD-IDNO",
                "id": "3",
                "legalName": "identifier/legal name",
                "uri": "ident uri"
            },
            "contactPoint": {
                "name": "contactPoint/name",
                "email": "contactPoint/email",
                "telephone": "contactPoint/456-95-96",
                "faxNumber": "fax-number",
                "url": "CP url"
            },
            "additionalIdentifiers": [
                {
                    "scheme": "md-idno",
                    "id": "445521",
                    "legalName": "legalName",
                    "uri": "uri"
                }

            ],
            "address": {
                "streetAddress": "street address",
                "postalCode": "11",
                "addressDetails": {
                    "country": {
                        "id": "MD"
                    },
                    "region": {
                        "id": "0101000"
                    },
                    "locality": {
                        "scheme": "other",
                        "id": "localityid",
                        "description": "locality/description"
                    }
                }
            }
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
