   create_fe_full_data_model_with_auction_ms = {
  "ocid": "ocds-t1s2t3-MD-1637236357516",
  "compiledRelease": {
    "ocid": "ocds-t1s2t3-MD-1637236357516",
    "id": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516-1637237472501",
    "date": "2021-11-18T12:11:12Z",
    "tag": [
      "compiled" ],
    "language": "ro",
    "initiationType": "tender",
    "tender": {
      "id": "66c252fc-6e2f-4bc9-b87c-bc9ac57b3956",
      "title": "createFE:tender.title",
      "description": "createFE:tender.description",
      "status": "active",
      "statusDetails": "establishment",
      "value": {
        "amount": 12.00,
        "currency": "EUR"
      },
      "procurementMethod": "selective",
      "procurementMethodDetails": "testClosedFA",
      "procurementMethodRationale": "createFE:procurementMethodRationale",
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
        "id": "068bebe0-4866-11ec-b310-c7ecf598564f",
        "relationship": [
          "aggregatePlanning" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236357516/ocds-t1s2t3-MD-1637236357516-AP-1637236357516"
      },
      {
        "id": "f9655f80-b462-4347-b605-b51efa4fafc5",
        "relationship": [
          "x_demand" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637236350931",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236350931/ocds-t1s2t3-MD-1637236350931"
      },
      {
        "id": "9f1e6250-4868-11ec-b310-c7ecf598564f",
        "relationship": [
          "x_establishment" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637236357516-FE-1637237472364",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236357516/ocds-t1s2t3-MD-1637236357516-FE-1637237472364"
      } ]
  }
}


  create_fe_full_data_model_with_auction_ap = {
  "ocid": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516",
  "compiledRelease": {
    "ocid": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516",
    "id": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516-1637237472501",
    "date": "2021-11-18T12:11:12Z",
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
      "id": "480097a7-fcd9-4d7f-8f83-49508834f60d",
      "title": "tender.title AP",
      "description": "tender description AP",
      "status": "planned",
      "statusDetails": "aggregated",
      "items": [
        {
          "id": "0e7fdfc4-16a1-400b-a02b-c65f8a9338ea",
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
          "relatedLot": "034afb4c-8c96-4859-871c-d6505ca5059a"
        } ],
      "lots": [
        {
          "id": "034afb4c-8c96-4859-871c-d6505ca5059a",
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
          "id": "6c66d192-0ea9-46bc-8696-ba4823ed539d",
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
          "title": "doctitle`",
          "description": "docdesc`",
          "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
          "datePublished": "2021-09-30T11:54:20Z",
          "relatedLots": [
            "6c66d192-0ea9-46bc-8696-ba4823ed539d" ]
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
        "amount": 12.00,
        "currency": "EUR"
      }
    },
    "hasPreviousNotice": false,
    "purposeOfNotice": {
      "isACallForCompetition": false
    },
    "relatedProcesses": [
      {
        "id": "068bebe1-4866-11ec-b310-c7ecf598564f",
        "relationship": [
          "parent" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637236357516",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236357516/ocds-t1s2t3-MD-1637236357516"
      },
      {
        "id": "c2f6a696-8ef0-496f-bc2f-aca81a56d7f4",
        "relationship": [
          "x_scope" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1637236350931-PN-1637236350931",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236350931/ocds-t1s2t3-MD-1637236350931-PN-1637236350931"
      } ]
  }
}

    create_fe_full_data_model_with_auction_fe = {
 	"ocid": "ocds-t1s2t3-MD-1637236357516-FE-1637237472364",
 	"compiledRelease": {
 		"ocid": "ocds-t1s2t3-MD-1637236357516-FE-1637237472364",
 		"id": "ocds-t1s2t3-MD-1637236357516-FE-1637237472364-1637237472500",
 		"date": "2021-11-18T12:11:12Z",
 		"tag": ["tender"],
 		"initiationType": "tender",
 		"parties": [{
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
 			"additionalIdentifiers": [{
 				"scheme": "md-idno",
 				"id": "445521",
 				"legalName": "legalName",
 				"uri": "uri"
 			}],
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
 			"roles": ["buyer"]
 		}, {
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
 			"additionalIdentifiers": [{
 				"scheme": "md-idno",
 				"id": "445521",
 				"legalName": "legalName",
 				"uri": "uri"
 			}],
 			"contactPoint": {
 				"name": "contactPoint/name",
 				"email": "contactPoint/email",
 				"telephone": "contactPoint/456-95-96",
 				"faxNumber": "fax-number",
 				"url": "CP url"
 			},
 			"persones": [{
 				"id": "MD-IDNO-84",
 				"title": "Mr.",
 				"name": "Person from FE",
 				"identifier": {
 					"scheme": "MD-IDNO",
 					"id": "84",
 					"uri": "uri"
 				},
 				"businessFunctions": [{
 					"id": "businessFunctions1",
 					"type": "chairman",
 					"jobTitle": "string",
 					"period": {
 						"startDate": "2020-09-22T14:38:20Z"
 					},
 					"documents": [{
 						"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
 						"documentType": "regulatoryDocument",
 						"title": "string",
 						"description": "string"
 					}]
 				}]
 			}],
 			"roles": ["procuringEntity"]
 		}],
 		"tender": {
 			"id": "66c252fc-6e2f-4bc9-b87c-bc9ac57b3956",
 			"title": "createFE:tender.title",
 			"description": "createFE:tender.description",
 			"status": "active",
 			"statusDetails": "submission",
 			"criteria": [{
 				"id": "8f03ae06-fd29-42a8-9521-ab10ad27fbdd",
 				"title": "criteria for tenderer1",
 				"source": "tenderer",
 				"description": "criteria description",
 				"requirementGroups": [{
 					"id": "b1de3468-509d-4b20-82ca-ce9b010506d2",
 					"description": "RG1 for lot",
 					"requirements": [{
 						"id": "5972bdcc-7529-4f27-98c8-3f5bb07b2da9",
 						"title": "Your age???",
 						"dataType": "number",
 						"status": "active",
 						"datePublished": "2021-11-18T12:11:12Z",
 						"description": "sdrg",
 						"period": {
 							"startDate": "2021-12-26T14:45:00Z",
 							"endDate": "2021-12-30T14:45:00Z"
 						},
 						"eligibleEvidences": [{
 							"id": "35",
 							"title": "2",
 							"type": "document",
 							"description": "3"
 						}],
 						"expectedValue": 4.000
 					}]
 				}],
 				"relatesTo": "tenderer",
 				"classification": {
 					"scheme": "ESPD-2.2.1",
 					"id": "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"
 				}
 			}, {
 				"id": "eefc6e3b-4548-42a0-b849-e83f6076b641",
 				"title": "criteria for tenderer2",
 				"source": "tenderer",
 				"description": "criteria description",
 				"requirementGroups": [{
 					"id": "39b92454-2ff9-4cb9-85d3-4e62a0e65637",
 					"description": "RG1 for lot",
 					"requirements": [{
 						"id": "70f9da04-f178-4584-99b3-92d17188c818",
 						"title": "Your age???",
 						"dataType": "number",
 						"status": "active",
 						"datePublished": "2021-11-18T12:11:12Z",
 						"description": "sdrg",
 						"period": {
 							"startDate": "2021-12-26T14:45:00Z",
 							"endDate": "2021-12-30T14:45:00Z"
 						},
 						"eligibleEvidences": [{
 							"id": "85557",
 							"title": "2",
 							"type": "document",
 							"description": "3"
 						}, {
 							"id": "88",
 							"title": "string",
 							"type": "document",
 							"description": "string",
 							"relatedDocument": {
 								"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899"
 							}
 						}],
 						"minValue": 2.500,
 						"maxValue": 3.300
 					}]
 				}],
 				"relatesTo": "tenderer",
 				"classification": {
 					"scheme": "ESPD-2.2.1",
 					"id": "CRITERION.EXCLUSION.SOCIAL.SOCIAL_LAW"
 				}
 			}, {
 				"id": "2b373e0d-03e8-475b-a22d-3426ad0cda15",
 				"title": "criteria for tenderer2",
 				"source": "tenderer",
 				"description": "criteria description",
 				"requirementGroups": [{
 					"id": "372c4261-ff0a-4299-8b4e-f0e2086347d0",
 					"description": "RG1 for lot",
 					"requirements": [{
 						"id": "c5851595-4d99-47cd-8329-89ff1c0a8c8d",
 						"title": "Your age???",
 						"dataType": "number",
 						"status": "active",
 						"datePublished": "2021-11-18T12:11:12Z",
 						"description": "sdrg",
 						"period": {
 							"startDate": "2021-12-26T14:45:00Z",
 							"endDate": "2021-12-30T14:45:00Z"
 						},
 						"eligibleEvidences": [{
 							"id": "07",
 							"title": "2",
 							"type": "document",
 							"description": "3"
 						}, {
 							"id": "08",
 							"title": "string",
 							"type": "document"
 						}],
 						"minValue": 2.500,
 						"maxValue": 3.300
 					}]
 				}],
 				"relatesTo": "tenderer",
 				"classification": {
 					"scheme": "ESPD-2.2.1",
 					"id": "CRITERION.EXCLUSION.SOCIAL.LABOUR_LAW"
 				}
 			}, {
 				"id": "e24182b2-d159-41cb-963e-7e851774eb80",
 				"title": "criteria for tenderer2",
 				"source": "tenderer",
 				"description": "criteria description",
 				"requirementGroups": [{
 					"id": "5ffe88d8-07ee-4e44-9733-54646a7ac7c9",
 					"description": "RG1 for lot",
 					"requirements": [{
 						"id": "accfd797-1a7a-4c2d-b08c-d02033f55aea",
 						"title": "Your age???",
 						"dataType": "number",
 						"status": "active",
 						"datePublished": "2021-11-18T12:11:12Z",
 						"description": "sdrg",
 						"period": {
 							"startDate": "2021-12-26T14:45:00Z",
 							"endDate": "2021-12-30T14:45:00Z"
 						},
 						"eligibleEvidences": [{
 							"id": "7555",
 							"title": "2",
 							"type": "document",
 							"description": "3"
 						}, {
 							"id": "55558",
 							"title": "string",
 							"type": "document"
 						}],
 						"minValue": 2.500,
 						"maxValue": 3.300
 					}]
 				}],
 				"relatesTo": "tenderer",
 				"classification": {
 					"scheme": "ESPD-2.2.1",
 					"id": "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.CERTIFICATES.ENVIRONMENTAL_MANAGEMENT.ENV_INDEPENDENT_CERTIFICATE"
 				}
 			}],
 			"otherCriteria": {
 				"reductionCriteria": "none",
 				"qualificationSystemMethods": ["manual"]
 			},
 			"enquiryPeriod": {
 				"startDate": "2021-11-18T12:11:12Z",
 				"endDate": "2021-12-03T12:42:00Z"
 			},
 			"hasEnquiries": false,
 			"documents": [{
 				"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
 				"documentType": "evaluationCriteria",
 				"title": "doctitle`",
 				"description": "docdesc`",
 				"url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
 				"datePublished": "2021-09-30T11:54:20Z"
 			}],
 			"submissionMethod": ["electronicSubmission"],
 			"submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
 			"submissionMethodRationale": ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"],
 			"requiresElectronicCatalogue": false,
 			"procurementMethodModalities": ["electronicAuction"],
 			"secondStage": {
 				"minimumCandidates": 1,
 				"maximumCandidates": 3
 			},
 			"procurementMethodRationale": "string",
 			"classification": {
 				"scheme": "CPV",
 				"id": "50100000-6",
 				"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
 			},
 			"value": {
 				"amount": 12.00,
 				"currency": "EUR"
 			},
 			"procuringEntity": {
 				"id": "MD-IDNO-3",
 				"name": "name of PE from AP (future cpb)"
 			}
 		},
 		"preQualification": {
 			"period": {
 				"startDate": "2021-11-18T12:11:12Z",
 				"endDate": "2021-12-03T12:43:00Z"
 			}
 		},
 		"hasPreviousNotice": true,
 		"purposeOfNotice": {
 			"isACallForCompetition": true
 		},
 		"relatedProcesses": [{
 			"id": "c65e37d4-e78c-4898-9789-cb64b219c697",
 			"relationship": ["aggregatePlanning"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637236357516-AP-1637236357516",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236357516/ocds-t1s2t3-MD-1637236357516-AP-1637236357516"
 		}, {
 			"id": "d1499fc0-3829-468c-9c96-bdeb8ab0dc1f",
 			"relationship": ["parent"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637236357516",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637236357516/ocds-t1s2t3-MD-1637236357516"
 		}]
 	}
 }