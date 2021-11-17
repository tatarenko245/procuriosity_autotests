create_fs_full_data_model = {
  "tender":
  {
    "procuringEntity": {
      "name": "Payer's Name1",
      "identifier": {
        "id": "111",
        "scheme": "MD-IDNO",
        "legalName": "Legal Name",
        "uri": "http://454.to"
      },
      "address": {
        "streetAddress": "street",
        "postalCode": "785412",
        "addressDetails": {
          "country": {
            "id": "MD"
          },
          "region": {
            "id": "3400000"
          },
          "locality": {
            "scheme": "CUATM",
            "id": "3401000",
            "description": "11"
          }
        }
      },
      "additionalIdentifiers": [
        {
          "id": "additional identifier",
          "scheme": "MD-K",
          "legalName": "legalname",
          "uri": "http://k.to"
        }],
      "contactPoint": {
        "name": "contact person",
        "email": "string@mail.ccc",
        "telephone": "98-79-87",
        "faxNumber": "78-56-55",
        "url": "http://url.com"
      }
    }
  },
  "buyer": {
    "name": "funder's name1",
    "identifier": {
      "id": "12222",
      "scheme": "MD-IDNO",
      "legalName": "legal Name",
      "uri": "http://buyer.com"
    },
    "address": {
      "streetAddress": "street address of buyer",
      "postalCode": "02054",
      "addressDetails": {
        "country": {
          "id": "MD"
        },
        "region": {
          "id": "1700000"
        },
        "locality": {
          "scheme": "CUATM",
          "id": "1701000",
          "description": "description of locality"
        }
      }
    },
    "additionalIdentifiers": [
      {
        "id": "additional identifier",
        "scheme": "scheme",
        "legalName": "legal name",
        "uri": "http://addtIdent.com"
      }],
    "contactPoint": {
      "name": "contact point of buyer",
      "email": "email.com",
      "telephone": "32-22-23",
      "faxNumber": "12-22-21",
      "url": "http://url.com"
    }
  },
  "planning": {
    "rationale": "reason for the budget",
    "budget": {
      "id": "IBAN - 102030",
      "description": "description",
      "period": {
        "startDate": "2020-02-01T11:07:00Z",
        "endDate": "2021-12-31T00:00:00Z"
      },
      "amount": {
        "amount": 100,
        "currency": "EUR"
      },
      "isEuropeanUnionFunded": false,
      "europeanUnionFunding": {
        "projectName": "Name of this project",
        "projectIdentifier": "projectIdentifier",
        "uri": "http://uriuri.th"
      },
      "project": "project",
      "projectID": "projectID",
      "uri": "http://uri.ur"
    }
  }
}
