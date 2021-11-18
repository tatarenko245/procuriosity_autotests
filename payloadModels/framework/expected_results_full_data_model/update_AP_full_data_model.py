  update_ap_full_data_model_fa = {
  "ocid": "ocds-t1s2t3-MD-1637230371725",
  "compiledRelease": {
    "ocid": "ocds-t1s2t3-MD-1637230371725",
    "id": "ocds-t1s2t3-MD-1637230371725-1637231328318",
    "date": "2021-11-18T10:28:48Z",
    "tag": [
      "compiled" ],
    "language": "ro",
    "initiationType": "tender",
    "tender": {
      "id": "bc021cb4-6097-4b7f-8783-f5f9dc68bae9",
      "title": "updateAP:tender/title",
      "description": "updateAP:tender/description",
      "status": "planning",
      "statusDetails": "aggregatePlanning",
      "value": {
        "amount": 90.00,
        "currency": "EUR"
      },
      "procurementMethod": "selective",
      "procurementMethodDetails": "testClosedFA",
      "procurementMethodRationale": "tender/procurementMethodRationale AP",
      "mainProcurementCategory": "services",
      "hasEnquiries": false,
      "eligibilityCriteria": "Regulile generale privind naționalitatea și originea, precum și alte criterii de eligibilitate sunt enumerate în Ghidul practic privind procedurile de contractare a acțiunilor externe ale UE (PRAG)",
      "contractPeriod": {
        "startDate": "2021-12-10T09:30:00Z",
        "endDate": "2021-12-11T10:30:00Z"
      },
      "acceleratedProcedure": {
        "isAcceleratedProcedure": false
      },
      "classification": {
        "scheme": "CPV",
        "id": "50100000-6",
        "description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
      },
      "designContest": {
        "serviceContractAward": false
      },
      "electronicWorkflows": {
        "useOrdering": false,
        "usePayment": false,
        "acceptInvoicing": false
      },
      "jointProcurement": {
        "isJointProcurement": false
      },
      "legalBasis": "DIRECTIVE_2009_81_EC",
      "procedureOutsourcing": {
        "procedureOutsourced": false
      },
      "dynamicPurchasingSystem": {
        "hasDynamicPurchasingSystem": false
      },
      "framework": {
        "isAFramework": true
      }
    },
    "relatedProcesses": [
      {
        "id": "16bcda00-4858-11ec-b310-c7ecf598564f",
        "relationship": [
          "aggregatePlanning" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637230371725-AP-1637230371725",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637230371725/ocds-t1s2t3-MD-1637230371725-AP-1637230371725"
      },
      {
        "id": "cbc8a326-708d-4e33-8683-2d7d40e4c909",
        "relationship": [
          "x_demand" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637230365154",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637230365154/ocds-t1s2t3-MD-1637230365154"
      } ]
  }
}


  update_ap_full_data_model_ap = {
  "ocid": "ocds-t1s2t3-MD-1637230371725-AP-1637230371725",
  "compiledRelease": {
    "ocid": "ocds-t1s2t3-MD-1637230371725-AP-1637230371725",
    "id": "ocds-t1s2t3-MD-1637230371725-AP-1637230371725-1637231328318",
    "date": "2021-11-18T10:28:48Z",
    "tag": [
      "planningUpdate" ],
    "language": "ro",
    "initiationType": "tender",
    "parties": [
      {
        "id": "MD-IDNO-3",
        "name": "name of PE from AP (future cpb)",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "3",
          "legalName": "identifier/legal name",
          "uri": "ident uri"
        },
        "address": {
          "streetAddress": "street address",
          "postalCode": "11",
          "addressDetails": {
            "country": {
              "scheme": "iso-alpha2",
              "id": "MD",
              "description": "Moldova, Republica",
              "uri": "https://www.iso.org"
            },
            "region": {
              "scheme": "CUATM",
              "id": "0101000",
              "description": "mun.Chişinău",
              "uri": "http://statistica.md"
            },
            "locality": {
              "scheme": "other",
              "id": "localityid",
              "description": "locality/description"
            }
          }
        },
        "additionalIdentifiers": [
          {
            "scheme": "md-idno",
            "id": "445521",
            "legalName": "legalName",
            "uri": "uri"
          } ],
        "contactPoint": {
          "name": "contactPoint/name",
          "email": "contactPoint/email",
          "telephone": "contactPoint/456-95-96",
          "faxNumber": "fax-number",
          "url": "CP url"
        },
        "roles": [
          "centralPurchasingBody" ]
      },
      {
        "id": "MD-IDNO-1",
        "name": "Buyer name",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "1",
          "legalName": "legal_name",
          "uri": "uri"
        },
        "address": {
          "streetAddress": "street address",
          "postalCode": "postalCode",
          "addressDetails": {
            "country": {
              "scheme": "iso-alpha2",
              "id": "MD",
              "description": "Moldova, Republica",
              "uri": "https://www.iso.org"
            },
            "region": {
              "scheme": "CUATM",
              "id": "0101000",
              "description": "mun.Chişinău",
              "uri": "http://statistica.md"
            },
            "locality": {
              "scheme": "CUATM",
              "id": "0101000",
              "description": "mun.Chişinău",
              "uri": "http://statistica.md"
            }
          }
        },
        "additionalIdentifiers": [
          {
            "scheme": "md-idno",
            "id": "445521",
            "legalName": "legalName",
            "uri": "uri"
          } ],
        "contactPoint": {
          "name": "contactPoint/name",
          "email": "contactPoint/email",
          "telephone": "contactPoint/456-95-96",
          "faxNumber": "fax-number",
          "url": "url"
        },
        "details": {
          "typeOfBuyer": "MINISTRY",
          "mainGeneralActivity": "HEALTH",
          "mainSectoralActivity": "WATER"
        },
        "roles": [
          "client" ]
      } ],
    "tender": {
      "id": "bc021cb4-6097-4b7f-8783-f5f9dc68bae9",
      "title": "tender.title AP",
      "description": "tender description AP",
      "status": "planning",
      "statusDetails": "aggregation",
      "items": [
        {
          "id": "12fff9ce-4d0a-43ea-9459-bb7ea1b68a1c",
          "description": "itemdescription.",
          "classification": {
            "scheme": "CPV",
            "id": "50100000-6",
            "description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
          },
          "quantity": 1.000,
          "unit": {
            "name": "Parsec",
            "id": "10"
          },
          "relatedLot": "f5de0dcb-85c5-4b9b-a774-fd2bfa4ea57c"
        } ],
      "lots": [
        {
          "id": "f5de0dcb-85c5-4b9b-a774-fd2bfa4ea57c",
          "title": "lots.titleNew",
          "description": "lots.description",
          "status": "planning",
          "statusDetails": "empty",
          "placeOfPerformance": {
            "address": {
              "addressDetails": {
                "country": {
                  "scheme": "iso-alpha2",
                  "id": "MD",
                  "description": "Moldova, Republica",
                  "uri": "https://www.iso.org"
                },
                "region": {
                  "scheme": "CUATM",
                  "id": "1000000",
                  "description": "Anenii Noi",
                  "uri": "http://statistica.md"
                },
                "locality": {
                  "scheme": "CUATM",
                  "id": "1001001",
                  "description": "s.Albiniţa",
                  "uri": "http://statistica.md"
                }
              }
            }
          }
        },
        {
          "id": "70a4d772-1b57-4c87-8245-b4c4168f8417",
          "title": "lots.titleNew",
          "description": "lots.description",
          "status": "planning",
          "statusDetails": "empty",
          "placeOfPerformance": {
            "address": {
              "addressDetails": {
                "country": {
                  "scheme": "iso-alpha2",
                  "id": "MD",
                  "description": "Moldova, Republica",
                  "uri": "https://www.iso.org"
                },
                "region": {
                  "scheme": "CUATM",
                  "id": "1000000",
                  "description": "Anenii Noi",
                  "uri": "http://statistica.md"
                },
                "locality": {
                  "scheme": "CUATM",
                  "id": "1001001",
                  "description": "s.Albiniţa",
                  "uri": "http://statistica.md"
                }
              }
            }
          }
        } ],
      "tenderPeriod": {
        "startDate": "2020-08-01T11:07:00Z"
      },
      "hasEnquiries": false,
      "documents": [
        {
          "id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
          "documentType": "evaluationCriteria",
          "title": "updateAP:documents/title",
          "description": "updateAP:documents/description",
          "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
          "datePublished": "2021-09-30T11:54:20Z",
          "relatedLots": [
            "lots/id" ]
        } ],
      "submissionMethod": [
        "electronicSubmission" ],
      "submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
      "submissionMethodRationale": [
        "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice" ],
      "requiresElectronicCatalogue": false,
      "procurementMethodRationale": "tender/procurementMethodRationale AP",
      "classification": {
        "scheme": "CPV",
        "id": "50100000-6",
        "description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
      },
      "value": {
        "amount": 90.00,
        "currency": "EUR"
      }
    },
    "hasPreviousNotice": false,
    "purposeOfNotice": {
      "isACallForCompetition": false
    },
    "relatedProcesses": [
      {
        "id": "16bcda01-4858-11ec-b310-c7ecf598564f",
        "relationship": [
          "parent" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637230371725",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637230371725/ocds-t1s2t3-MD-1637230371725"
      },
      {
        "id": "02cb9155-0ad1-4d19-bd04-a3fda60b0637",
        "relationship": [
          "x_scope" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637230365154-PN-1637230365154",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637230365154/ocds-t1s2t3-MD-1637230365154-PN-1637230365154"
      } ]
  }
}
