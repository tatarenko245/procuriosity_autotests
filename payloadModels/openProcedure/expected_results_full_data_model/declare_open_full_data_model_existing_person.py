declare_open_full_data_model_existing_person_MS = {

  "ocid": "ocds-t1s2t3-MD-1638188915734",
  "compiledRelease": {
    "ocid": "ocds-t1s2t3-MD-1638188915734",
    "id": "ocds-t1s2t3-MD-1638188915734-1638189604495",
    "date": "2021-11-29T12:40:03Z",
    "tag": [
      "compiled" ],
    "initiationType": "tender",
    "language": "ro",
    "planning": {
      "budget": {
        "description": "budget/description from PN",
        "amount": {
          "amount": 5.00,
          "currency": "EUR"
        },
        "isEuropeanUnionFunded": true,
        "budgetBreakdown": [
          {
            "id": "ocds-t1s2t3-MD-1638183418367-FS-1638183432488",
            "amount": {
              "amount": 5.00,
              "currency": "EUR"
            },
            "period": {
              "startDate": "2021-09-01T11:07:00Z",
              "endDate": "2021-12-01T00:00:00Z"
            },
            "sourceParty": {
              "id": "MD-IDNO-123654789000",
              "name": "funder's name"
            },
            "europeanUnionFunding": {
              "projectIdentifier": "projectIdentifier",
              "projectName": "Name of this project"
            }
          } ]
      },
      "rationale": "planning rationale from PN"
    },
    "parties": [
      {
        "id": "MD-IDNO-19901",
        "name": "name of buyer for PN-111",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "19901",
          "legalName": "legal_name of buyerei",
          "uri": "uri"
        },
        "address": {
          "streetAddress": "street address",
          "postalCode": "1",
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
          "buyer" ]
      },
      {
        "id": "MD-IDNO-123456789000",
        "name": "Payer's Name",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "123456789000",
          "legalName": "Legal Name"
        },
        "address": {
          "streetAddress": "street",
          "addressDetails": {
            "country": {
              "scheme": "iso-alpha2",
              "id": "MD",
              "description": "Moldova, Republica",
              "uri": "https://www.iso.org"
            },
            "region": {
              "scheme": "CUATM",
              "id": "3400000",
              "description": "Donduşeni",
              "uri": "http://statistica.md"
            },
            "locality": {
              "scheme": "CUATM",
              "id": "3401000",
              "description": "or.Donduşeni (r-l Donduşeni)",
              "uri": "http://statistica.md"
            }
          }
        },
        "contactPoint": {
          "name": "contact person",
          "email": "string@mail.ccc",
          "telephone": "98-79-87"
        },
        "roles": [
          "payer" ]
      },
      {
        "id": "MD-IDNO-123654789000",
        "name": "funder's name",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "123654789000",
          "legalName": "legal Name"
        },
        "address": {
          "streetAddress": "street address of buyer",
          "addressDetails": {
            "country": {
              "scheme": "iso-alpha2",
              "id": "MD",
              "description": "Moldova, Republica",
              "uri": "https://www.iso.org"
            },
            "region": {
              "scheme": "CUATM",
              "id": "1700000",
              "description": "Cahul",
              "uri": "http://statistica.md"
            },
            "locality": {
              "scheme": "CUATM",
              "id": "1701000",
              "description": "mun.Cahul",
              "uri": "http://statistica.md"
            }
          }
        },
        "contactPoint": {
          "name": "contact point of buyer",
          "email": "email.com",
          "telephone": "32-22-23"
        },
        "roles": [
          "funder" ]
      },
      {
        "id": "MD-IDNO-2",
        "name": "createPN: PE name",
        "identifier": {
          "scheme": "MD-IDNO",
          "id": "2",
          "legalName": "identifier/legal name",
          "uri": "uri"
        },
        "address": {
          "streetAddress": "street address pn",
          "postalCode": "11 pn",
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
            "scheme": "md-idno pn",
            "id": "445521 pn",
            "legalName": "legalName pn",
            "uri": "uri pn"
          },
          {
            "scheme": "md-idno pn1",
            "id": "445521 pn1",
            "legalName": "legalName pn1",
            "uri": "uri pn1"
          } ],
        "contactPoint": {
          "name": "contactPoint/name pn",
          "email": "contactPoint/email pn",
          "telephone": "contactPoint/456-95-96 pn",
          "faxNumber": "fax-number pn",
          "url": "url pn"
        },
        "persones": [
          {
            "id": "MD-IDNO-555555",
            "title": "Ms.",
            "name": "createCN: persones name",
            "identifier": {
              "scheme": "MD-IDNO",
              "id": "555555",
              "uri": "uri"
            },
            "businessFunctions": [
              {
                "id": "businessFunction",
                "type": "priceOpener",
                "jobTitle": "Chief Executive Officer",
                "period": {
                  "startDate": "2019-10-29T15:20:10Z"
                }
              },
              {
                "id": "businessFunction1",
                "type": "chairman",
                "jobTitle": "Chief Executive Officer",
                "period": {
                  "startDate": "2019-10-29T15:20:10Z"
                }
              } ]
          } ],
        "roles": [
          "procuringEntity" ]
      } ],
    "tender": {
      "id": "7e80e29d-0f01-4a00-8843-25d1296ffb8a",
      "title": "tender title from PN",
      "description": "tender description PN",
      "status": "active",
      "statusDetails": "evaluation",
      "hasEnquiries": false,
      "value": {
        "amount": 5.00,
        "currency": "EUR"
      },
      "procurementMethod": "open",
      "procurementMethodDetails": "testMicroValue",
      "procurementMethodRationale": "OPTIONAL",
      "mainProcurementCategory": "services",
      "additionalProcurementCategories": [
        "works" ],
      "eligibilityCriteria": "Regulile generale privind naționalitatea și originea, precum și alte criterii de eligibilitate sunt enumerate în Ghidul practic privind procedurile de contractare a acțiunilor externe ale UE (PRAG)",
      "contractPeriod": {
        "startDate": "2021-11-30T11:12:00Z",
        "endDate": "2021-12-29T14:45:00Z"
      },
      "procuringEntity": {
        "id": "MD-IDNO-2",
        "name": "createPN: PE name"
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
      "legalBasis": "NATIONAL_PROCUREMENT_LAW",
      "procedureOutsourcing": {
        "procedureOutsourced": false
      },
      "procurementMethodAdditionalInfo": "OPTIONAL",
      "dynamicPurchasingSystem": {
        "hasDynamicPurchasingSystem": false
      },
      "framework": {
        "isAFramework": false
      }
    },
    "relatedProcesses": [
      {
        "id": "df7cf370-510f-11ec-b310-c7ecf598564f",
        "relationship": [
          "planning" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1638188915734-PN-1638188915734",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1638188915734/ocds-t1s2t3-MD-1638188915734-PN-1638188915734"
      },
      {
        "id": "df7cf371-510f-11ec-b310-c7ecf598564f",
        "relationship": [
          "x_expenditureItem" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1638183418367",
        "uri": "http://dev.public.eprocurement.systems/budgets/ocds-t1s2t3-MD-1638183418367/ocds-t1s2t3-MD-1638183418367"
      },
      {
        "id": "df7cf372-510f-11ec-b310-c7ecf598564f",
        "relationship": [
          "x_fundingSource" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1638183418367-FS-1638183432488",
        "uri": "http://dev.public.eprocurement.systems/budgets/ocds-t1s2t3-MD-1638183418367/ocds-t1s2t3-MD-1638183418367-FS-1638183432488"
      },
      {
        "id": "fdb74b10-510f-11ec-b310-c7ecf598564f",
        "relationship": [
          "x_evaluation" ],
        "scheme": "ocid",
        "identifier": "ocds-t1s2t3-MD-1638188915734-EV-1638188966394",
        "uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1638188915734/ocds-t1s2t3-MD-1638188915734-EV-1638188966394"
      } ]
  }
}

}

   declare_open_full_data_model_existing_person_EV = {
    "ocid": "ocds-t1s2t3-MD-1638188915734-EV-1638188966394",
	"compiledRelease": {
		"ocid": "ocds-t1s2t3-MD-1638188915734-EV-1638188966394",
		"id": "ocds-t1s2t3-MD-1638188915734-EV-1638188966394-1638189604549",
		"date": "2021-11-29T12:40:03Z",
		"tag": ["award"],
		"initiationType": "tender",
		"language": "ro",
		"parties": [{
			"id": "MD-IDNO-888ee7e7-888e-4a44-ae0d-0cc4ee876fe2",
			"name": "FOP Tatarenko R.V.",
			"identifier": {
				"scheme": "MD-IDNO",
				"id": "888ee7e7-888e-4a44-ae0d-0cc4ee876fe2",
				"legalName": "FOP Tatarenko R.V."
			},
			"address": {
				"streetAddress": "Heroev Nebesnoj sotni",
				"addressDetails": {
					"country": {
						"scheme": "ISO-ALPHA2",
						"id": "MD",
						"description": "Moldova, Republica",
						"uri": "http://reference.iatistandard.org"
					},
					"region": {
						"scheme": "CUATM",
						"id": "1000000",
						"description": "Anenii Noi",
						"uri": "http://statistica.md"
					},
					"locality": {
						"scheme": "CUATM",
						"id": "1001000",
						"description": "or.Anenii Noi",
						"uri": "http://statistica.md"
					}
				}
			},
			"additionalIdentifiers": [{
				"scheme": "MD-ENOT",
				"id": "66-333",
				"legalName": "eNotice Company"
			}],
			"contactPoint": {
				"name": "Illia Petrusenko",
				"email": "illya.petrusenko@gmail.com",
				"telephone": "+380632074071"
			},
			"details": {
				"mainEconomicActivities": [{
					"scheme": "MD-CAEM",
					"id": "6666",
					"description": "opisanie mainecon acttivities"
				}],
				"permits": [{
					"id": "4569512354785220000",
					"scheme": "MD-MD",
					"url": "4",
					"permitDetails": {
						"issuedBy": {
							"id": "changed",
							"name": "vasia changed pupkin"
						},
						"issuedThought": {
							"id": "fgfgfgfg",
							"name": "changed"
						},
						"validityPeriod": {
							"startDate": "2020-03-01T00:00:00Z",
							"endDate": "2021-12-15T00:00:00Z"
						}
					}
				}],
				"bankAccounts": [{
					"description": "description",
					"bankName": "bankName",
					"address": {
						"streetAddress": "Steet",
						"addressDetails": {
							"country": {
								"scheme": "ISO-ALPHA2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "http://reference.iatistandard.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							}
						}
					},
					"identifier": {
						"id": "300711",
						"scheme": "UA-MFO"
					},
					"accountIdentification": {
						"id": "2600000625637",
						"scheme": "IBAN"
					}
				}],
				"legalForm": {
					"id": "4592",
					"scheme": "MD-IDNO",
					"description": "description"
				},
				"scale": "micro"
			},
			"persones": [{
				"id": "MD-IDNO-888888",
				"title": "Mr.",
				"name": "persones.name",
				"identifier": {
					"scheme": "MD-IDNO",
					"id": "888888"
				},
				"businessFunctions": [{
					"id": "87153c12-55ee-4423-9d6b-c6928c5c8d64",
					"type": "authority",
					"jobTitle": "Owner of the company tyjtytyjtyjtyjtjtyj",
					"period": {
						"startDate": "2020-03-01T15:20:10Z"
					}
				}]
			}],
			"roles": ["tenderer", "supplier"]
		}, {
			"id": "MD-IDNO-888ee7e7-888e-45b4-9cb4-77b14669c00d",
			"name": "FOP Tatarenko R.V.",
			"identifier": {
				"scheme": "MD-IDNO",
				"id": "888ee7e7-888e-45b4-9cb4-77b14669c00d",
				"legalName": "FOP Tatarenko R.V."
			},
			"address": {
				"streetAddress": "Heroev Nebesnoj sotni",
				"addressDetails": {
					"country": {
						"scheme": "ISO-ALPHA2",
						"id": "MD",
						"description": "Moldova, Republica",
						"uri": "http://reference.iatistandard.org"
					},
					"region": {
						"scheme": "CUATM",
						"id": "1000000",
						"description": "Anenii Noi",
						"uri": "http://statistica.md"
					},
					"locality": {
						"scheme": "CUATM",
						"id": "1001000",
						"description": "or.Anenii Noi",
						"uri": "http://statistica.md"
					}
				}
			},
			"additionalIdentifiers": [{
				"scheme": "MD-ENOT",
				"id": "66-333",
				"legalName": "eNotice Company"
			}],
			"contactPoint": {
				"name": "Illia Petrusenko",
				"email": "illya.petrusenko@gmail.com",
				"telephone": "+380632074071"
			},
			"details": {
				"mainEconomicActivities": [{
					"scheme": "MD-CAEM",
					"id": "6666",
					"description": "opisanie mainecon acttivities"
				}],
				"permits": [{
					"id": "4569512354785220000",
					"scheme": "MD-MD",
					"url": "4",
					"permitDetails": {
						"issuedBy": {
							"id": "changed",
							"name": "vasia changed pupkin"
						},
						"issuedThought": {
							"id": "fgfgfgfg",
							"name": "changed"
						},
						"validityPeriod": {
							"startDate": "2020-03-01T00:00:00Z",
							"endDate": "2021-12-15T00:00:00Z"
						}
					}
				}],
				"bankAccounts": [{
					"description": "description",
					"bankName": "bankName",
					"address": {
						"streetAddress": "Steet",
						"addressDetails": {
							"country": {
								"scheme": "ISO-ALPHA2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "http://reference.iatistandard.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							}
						}
					},
					"identifier": {
						"id": "300711",
						"scheme": "UA-MFO"
					},
					"accountIdentification": {
						"id": "2600000625637",
						"scheme": "IBAN"
					}
				}],
				"legalForm": {
					"id": "4592",
					"scheme": "MD-IDNO",
					"description": "description"
				},
				"scale": "micro"
			},
			"persones": [{
				"id": "MD-IDNO-888888",
				"title": "Mr.",
				"name": "persones.name",
				"identifier": {
					"scheme": "MD-IDNO",
					"id": "888888"
				},
				"businessFunctions": [{
					"id": "887e2f78-12d4-48b3-89ad-08fdb4b7c7d2",
					"type": "authority",
					"jobTitle": "Owner of the company tyjtytyjtyjtyjtjtyj",
					"period": {
						"startDate": "2020-03-01T15:20:10Z"
					}
				}]
			}],
			"roles": ["tenderer", "supplier"]
		}, {
			"id": "MD-IDNO-888ee7e7-888e-40b4-9495-68ef0711dbde",
			"name": "FOP Tatarenko R.V.",
			"identifier": {
				"scheme": "MD-IDNO",
				"id": "888ee7e7-888e-40b4-9495-68ef0711dbde",
				"legalName": "FOP Tatarenko R.V."
			},
			"address": {
				"streetAddress": "Heroev Nebesnoj sotni",
				"addressDetails": {
					"country": {
						"scheme": "ISO-ALPHA2",
						"id": "MD",
						"description": "Moldova, Republica",
						"uri": "http://reference.iatistandard.org"
					},
					"region": {
						"scheme": "CUATM",
						"id": "1000000",
						"description": "Anenii Noi",
						"uri": "http://statistica.md"
					},
					"locality": {
						"scheme": "CUATM",
						"id": "1001000",
						"description": "or.Anenii Noi",
						"uri": "http://statistica.md"
					}
				}
			},
			"additionalIdentifiers": [{
				"scheme": "MD-ENOT",
				"id": "66-333",
				"legalName": "eNotice Company"
			}],
			"contactPoint": {
				"name": "Illia Petrusenko",
				"email": "illya.petrusenko@gmail.com",
				"telephone": "+380632074071"
			},
			"details": {
				"mainEconomicActivities": [{
					"scheme": "MD-CAEM",
					"id": "6666",
					"description": "opisanie mainecon acttivities"
				}],
				"permits": [{
					"id": "4569512354785220000",
					"scheme": "MD-MD",
					"url": "4",
					"permitDetails": {
						"issuedBy": {
							"id": "changed",
							"name": "vasia changed pupkin"
						},
						"issuedThought": {
							"id": "fgfgfgfg",
							"name": "changed"
						},
						"validityPeriod": {
							"startDate": "2020-03-01T00:00:00Z",
							"endDate": "2021-12-15T00:00:00Z"
						}
					}
				}],
				"bankAccounts": [{
					"description": "description",
					"bankName": "bankName",
					"address": {
						"streetAddress": "Steet",
						"addressDetails": {
							"country": {
								"scheme": "ISO-ALPHA2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "http://reference.iatistandard.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							}
						}
					},
					"identifier": {
						"id": "300711",
						"scheme": "UA-MFO"
					},
					"accountIdentification": {
						"id": "2600000625637",
						"scheme": "IBAN"
					}
				}],
				"legalForm": {
					"id": "4592",
					"scheme": "MD-IDNO",
					"description": "description"
				},
				"scale": "micro"
			},
			"persones": [{
				"id": "MD-IDNO-888888",
				"title": "Mr.",
				"name": "persones.name",
				"identifier": {
					"scheme": "MD-IDNO",
					"id": "888888"
				},
				"businessFunctions": [{
					"id": "61a387a3-962b-496c-9991-fa8d1c308930",
					"type": "authority",
					"jobTitle": "Owner of the company tyjtytyjtyjtyjtjtyj",
					"period": {
						"startDate": "2020-03-01T15:20:10Z"
					}
				}]
			}],
			"roles": ["tenderer", "supplier"]
		}, {
			"id": "MD-IDNO-888ee7e7-888e-4ea4-924a-51a4fbb7d68f",
			"name": "FOP Tatarenko R.V.",
			"identifier": {
				"scheme": "MD-IDNO",
				"id": "888ee7e7-888e-4ea4-924a-51a4fbb7d68f",
				"legalName": "FOP Tatarenko R.V."
			},
			"address": {
				"streetAddress": "Heroev Nebesnoj sotni",
				"addressDetails": {
					"country": {
						"scheme": "ISO-ALPHA2",
						"id": "MD",
						"description": "Moldova, Republica",
						"uri": "http://reference.iatistandard.org"
					},
					"region": {
						"scheme": "CUATM",
						"id": "1000000",
						"description": "Anenii Noi",
						"uri": "http://statistica.md"
					},
					"locality": {
						"scheme": "CUATM",
						"id": "1001000",
						"description": "or.Anenii Noi",
						"uri": "http://statistica.md"
					}
				}
			},
			"additionalIdentifiers": [{
				"scheme": "MD-ENOT",
				"id": "66-333",
				"legalName": "eNotice Company"
			}],
			"contactPoint": {
				"name": "Illia Petrusenko",
				"email": "illya.petrusenko@gmail.com",
				"telephone": "+380632074071"
			},
			"details": {
				"mainEconomicActivities": [{
					"scheme": "MD-CAEM",
					"id": "6666",
					"description": "opisanie mainecon acttivities"
				}],
				"permits": [{
					"id": "4569512354785220000",
					"scheme": "MD-MD",
					"url": "4",
					"permitDetails": {
						"issuedBy": {
							"id": "changed",
							"name": "vasia changed pupkin"
						},
						"issuedThought": {
							"id": "fgfgfgfg",
							"name": "changed"
						},
						"validityPeriod": {
							"startDate": "2020-03-01T00:00:00Z",
							"endDate": "2021-12-15T00:00:00Z"
						}
					}
				}],
				"bankAccounts": [{
					"description": "description",
					"bankName": "bankName",
					"address": {
						"streetAddress": "Steet",
						"addressDetails": {
							"country": {
								"scheme": "ISO-ALPHA2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "http://reference.iatistandard.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "CUATM",
								"id": "0301000",
								"description": "mun.Bălţi",
								"uri": "http://statistica.md"
							}
						}
					},
					"identifier": {
						"id": "300711",
						"scheme": "UA-MFO"
					},
					"accountIdentification": {
						"id": "2600000625637",
						"scheme": "IBAN"
					}
				}],
				"legalForm": {
					"id": "4592",
					"scheme": "MD-IDNO",
					"description": "description"
				},
				"scale": "micro"
			},
			"persones": [{
				"id": "MD-IDNO-888888",
				"title": "Mr.",
				"name": "persones.name",
				"identifier": {
					"scheme": "MD-IDNO",
					"id": "888888"
				},
				"businessFunctions": [{
					"id": "d7f2bf5b-66e4-4412-8b23-c15489971e18",
					"type": "authority",
					"jobTitle": "Owner of the company tyjtytyjtyjtyjtjtyj",
					"period": {
						"startDate": "2020-03-01T15:20:10Z"
					}
				}]
			}],
			"roles": ["tenderer", "supplier"]
		}],
		"tender": {
			"id": "f16c278b-fecb-4bcc-9879-25dc41bcc6c4",
			"title": "Evaluation",
			"description": "Evaluation stage of contracting process",
			"status": "active",
			"statusDetails": "awarding",
			"criteria": [{
				"id": "5171e681-348e-4a23-b83c-1251bb73daa4",
				"title": "Declaration of absence of conflict of interest and confidentiality",
				"source": "procuringEntity",
				"description": "Conflict of interest",
				"requirementGroups": [{
					"id": "c560311f-d16f-48a3-ad53-f3ea529ae886",
					"requirements": [{
						"id": "1b99ef92-7d79-400b-8eef-f3ffd54a3fe7",
						"title": "I am aware of Article 24 of Directive 2014/24/EU on public procurement, which states that: \"The concept of conflicts of interest shall at least cover any situation where staff members of the contracting authority or of a procurement service provider acting on behalf of the contracting authority who are involved in the conduct of the procurement procedure or may influence the outcome of that procedure have, directly or indirectly, a financial, economic or other personal interest which might be perceived to compromise their impartiality and independence in the context of the procurement procedure.\"\nto the best of my knowledge and belief I have no conflict of interest with the operators whohave submitted a tender for this procurement, including persons or members of a consortium, or with the subcontractors proposed;\nthere are no facts or circumstances, past or present, or that could arise in the foreseeable future, which might call into question my independence in the eyes of any party;\nif I discover during the course of the [project/evaluation] that such a conflict exists or could arise, I will inform the contracting authority without delay;\nI am encouraged to report a situation or risk of conflict of interest as well as any type of wrongdoing or fraud (i.e. whistleblowing), and if I do so, I should not be treated unfairly or be sanctioned;\nI understand that the contracting authority reserves the right to verify this information.",
						"dataType": "boolean",
						"status": "active",
						"datePublished": "2021-11-29T12:32:25Z",
						"expectedValue": true
					}, {
						"id": "3892e7d6-3bad-4765-88e5-094e5b52716f",
						"title": "I confirm that I will keep all matters entrusted to me confidential. I will not communicate outside the [project team/evaluation committee] any confidential information that is revealed to me or that I have discovered. I will not make any adverse use of information given to me.",
						"dataType": "boolean",
						"status": "active",
						"datePublished": "2021-11-29T12:32:25Z",
						"expectedValue": true
					}]
				}],
				"relatesTo": "award",
				"classification": {
					"scheme": "ESPD-2.2.1",
					"id": "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.PROCEDURE_PARTICIPATION"
				}
			}],
			"items": [{
				"id": "ab2d8a4d-4d87-4791-95ab-946404b5ec4a",
				"description": "items description",
				"classification": {
					"scheme": "CPV",
					"id": "50100000-6",
					"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
				},
				"additionalClassifications": [{
					"scheme": "CPVS",
					"id": "TA30-9",
					"description": "De bonuri de masă"
				}],
				"quantity": 1.000,
				"unit": {
					"id": "120",
					"name": "Milion decalitri"
				},
				"relatedLot": "e56002a1-7b1f-4a95-ba88-2cf418da49ec"
			}, {
				"id": "468980a8-73c1-4caa-a723-bc8b91b443cc",
				"description": "items description",
				"classification": {
					"scheme": "CPV",
					"id": "50100000-6",
					"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
				},
				"additionalClassifications": [{
					"scheme": "CPVS",
					"id": "TA30-9",
					"description": "De bonuri de masă"
				}],
				"quantity": 1.000,
				"unit": {
					"id": "120",
					"name": "Milion decalitri"
				},
				"relatedLot": "0be1830c-ca95-4c4c-9dd9-cc0d16e48a25"
			}, {
				"id": "4677d5b9-019d-4732-a79e-ae19adb5d364",
				"description": "items description",
				"classification": {
					"scheme": "CPV",
					"id": "45100000-8",
					"description": "Lucrări de pregătire a şantierului"
				},
				"additionalClassifications": [{
					"scheme": "CPVS",
					"id": "TA30-9",
					"description": "De bonuri de masă"
				}],
				"quantity": 1.000,
				"unit": {
					"id": "120",
					"name": "Milion decalitri"
				},
				"relatedLot": "e56002a1-7b1f-4a95-ba88-2cf418da49ec"
			}],
			"lots": [{
				"id": "e56002a1-7b1f-4a95-ba88-2cf418da49ec",
				"internalId": "internalId",
				"title": "lots title",
				"description": "lots description",
				"status": "active",
				"statusDetails": "empty",
				"value": {
					"amount": 3.00,
					"currency": "EUR"
				},
				"contractPeriod": {
					"startDate": "2021-11-30T11:12:00Z",
					"endDate": "2021-12-29T14:45:00Z"
				},
				"placeOfPerformance": {
					"address": {
						"streetAddress": "placeOfPerformance streetAddress",
						"postalCode": "placeOfPerformance postalCode",
						"addressDetails": {
							"country": {
								"scheme": "iso-alpha2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "https://www.iso.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "3400000",
								"description": "Donduşeni",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "locality scheme",
								"id": "locality id",
								"description": "locality description"
							}
						}
					},
					"description": "description"
				},
				"hasOptions": true,
				"options": [{
					"description": "The buyer has the option to buy an additional hundred uniforms.",
					"period": {
						"startDate": "2021-11-10T00:00:00Z",
						"endDate": "2024-12-10T00:00:00Z",
						"maxExtentDate": "2024-02-10T00:00:00Z",
						"durationInDays": 180
					}
				}],
				"hasRecurrence": true,
				"hasRenewal": true
			}, {
				"id": "0be1830c-ca95-4c4c-9dd9-cc0d16e48a25",
				"internalId": "internalId",
				"title": "lots title",
				"description": "lots description",
				"status": "active",
				"statusDetails": "empty",
				"value": {
					"amount": 2.00,
					"currency": "EUR"
				},
				"contractPeriod": {
					"startDate": "2021-12-01T11:12:00Z",
					"endDate": "2021-12-29T14:45:00Z"
				},
				"placeOfPerformance": {
					"address": {
						"streetAddress": "placeOfPerformance streetAddress",
						"postalCode": "placeOfPerformance postalCode",
						"addressDetails": {
							"country": {
								"scheme": "iso-alpha2",
								"id": "MD",
								"description": "Moldova, Republica",
								"uri": "https://www.iso.org"
							},
							"region": {
								"scheme": "CUATM",
								"id": "3400000",
								"description": "Donduşeni",
								"uri": "http://statistica.md"
							},
							"locality": {
								"scheme": "locality scheme",
								"id": "locality id",
								"description": "locality description"
							}
						}
					},
					"description": "description"
				},
				"hasOptions": true,
				"options": [{
					"description": "The buyer has the option to buy an additional hundred uniforms.",
					"period": {
						"startDate": "2021-12-10T00:00:00Z",
						"endDate": "2024-12-10T00:00:00Z",
						"maxExtentDate": "2024-02-10T00:00:00Z",
						"durationInDays": 180
					}
				}],
				"hasRecurrence": true,
				"hasRenewal": true
			}],
			"lotGroups": [{
				"optionToCombine": false
			}],
			"tenderPeriod": {
				"startDate": "2021-11-29T12:31:25Z",
				"endDate": "2021-11-29T12:32:25Z"
			},
			"enquiryPeriod": {
				"startDate": "2021-11-29T12:29:26Z",
				"endDate": "2021-11-29T12:31:25Z"
			},
			"awardPeriod": {
				"startDate": "2021-11-29T12:32:25Z"
			},
			"hasEnquiries": false,
			"documents": [{
				"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
				"documentType": "technicalSpecifications",
				"title": "title",
				"description": "description",
				"url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
				"datePublished": "2021-09-30T11:54:20Z"
			}],
			"awardCriteria": "priceOnly",
			"awardCriteriaDetails": "automated",
			"submissionMethod": ["electronicSubmission"],
			"submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
			"submissionMethodRationale": ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"],
			"requiresElectronicCatalogue": false
		},
		"awards": [{
			"id": "c46bbb61-e270-4b28-bafe-cfa27288017b",
			"status": "pending",
			"statusDetails": "awaiting",
			"date": "2021-11-29T12:32:25Z",
			"value": {
				"amount": 3.00,
				"currency": "EUR"
			},
			"suppliers": [{
				"id": "MD-IDNO-888ee7e7-888e-4ea4-924a-51a4fbb7d68f",
				"name": "FOP Tatarenko R.V."
			}],
			"requirementResponses": [{
				"id": "cfb1c87d-37ac-4298-88e4-4688241d833e",
				"value": true,
				"requirement": {
					"id": "1b99ef92-7d79-400b-8eef-f3ffd54a3fe7"
				},
				"responder": {
					"id": "MD-IDNO-555555",
					"name": "createCN: persones name"
				},
				"relatedTenderer": {
					"id": "MD-IDNO-888ee7e7-888e-4ea4-924a-51a4fbb7d68f"
				}
			}],
			"relatedLots": ["0be1830c-ca95-4c4c-9dd9-cc0d16e48a25"],
			"relatedBid": "c1047adb-28b6-4594-a9a9-77027693caab"
		}, {
			"id": "29a3a93c-f140-4394-9c34-2818dfa4ef44",
			"status": "pending",
			"statusDetails": "empty",
			"date": "2021-11-29T12:32:25Z",
			"value": {
				"amount": 3.00,
				"currency": "EUR"
			},
			"suppliers": [{
				"id": "MD-IDNO-888ee7e7-888e-40b4-9495-68ef0711dbde",
				"name": "FOP Tatarenko R.V."
			}],
			"relatedLots": ["0be1830c-ca95-4c4c-9dd9-cc0d16e48a25"],
			"relatedBid": "24b792c9-7234-4b11-8c26-e055b73e9e55"
		}, {
			"id": "61212166-139f-40a1-a9bb-98ae2f00ce56",
			"status": "pending",
			"statusDetails": "awaiting",
			"date": "2021-11-29T12:32:25Z",
			"value": {
				"amount": 3.00,
				"currency": "EUR"
			},
			"suppliers": [{
				"id": "MD-IDNO-888ee7e7-888e-45b4-9cb4-77b14669c00d",
				"name": "FOP Tatarenko R.V."
			}],
			"relatedLots": ["e56002a1-7b1f-4a95-ba88-2cf418da49ec"],
			"relatedBid": "0edc8c7c-9481-4a99-bf80-c293281df72d"
		}, {
			"id": "ca04dc5c-bd6f-4e72-9261-6852d3dc647f",
			"status": "pending",
			"statusDetails": "empty",
			"date": "2021-11-29T12:32:25Z",
			"value": {
				"amount": 3.00,
				"currency": "EUR"
			},
			"suppliers": [{
				"id": "MD-IDNO-888ee7e7-888e-4a44-ae0d-0cc4ee876fe2",
				"name": "FOP Tatarenko R.V."
			}],
			"relatedLots": ["e56002a1-7b1f-4a95-ba88-2cf418da49ec"],
			"relatedBid": "05e4f8a5-e2dc-45b6-aa39-0a824dc8605b"
		}],
		"bids": {
			"details": [{
				"id": "05e4f8a5-e2dc-45b6-aa39-0a824dc8605b",
				"date": "2021-11-29T12:31:39Z",
				"status": "pending",
				"tenderers": [{
					"id": "MD-IDNO-888ee7e7-888e-4a44-ae0d-0cc4ee876fe2",
					"name": "FOP Tatarenko R.V."
				}],
				"value": {
					"amount": 3.00,
					"currency": "EUR"
				},
				"relatedLots": ["e56002a1-7b1f-4a95-ba88-2cf418da49ec"]
			}, {
				"id": "0edc8c7c-9481-4a99-bf80-c293281df72d",
				"date": "2021-11-29T12:31:36Z",
				"status": "pending",
				"tenderers": [{
					"id": "MD-IDNO-888ee7e7-888e-45b4-9cb4-77b14669c00d",
					"name": "FOP Tatarenko R.V."
				}],
				"value": {
					"amount": 3.00,
					"currency": "EUR"
				},
				"relatedLots": ["e56002a1-7b1f-4a95-ba88-2cf418da49ec"]
			}, {
				"id": "24b792c9-7234-4b11-8c26-e055b73e9e55",
				"date": "2021-11-29T12:31:47Z",
				"status": "pending",
				"tenderers": [{
					"id": "MD-IDNO-888ee7e7-888e-40b4-9495-68ef0711dbde",
					"name": "FOP Tatarenko R.V."
				}],
				"value": {
					"amount": 3.00,
					"currency": "EUR"
				},
				"relatedLots": ["0be1830c-ca95-4c4c-9dd9-cc0d16e48a25"]
			}, {
				"id": "c1047adb-28b6-4594-a9a9-77027693caab",
				"date": "2021-11-29T12:31:45Z",
				"status": "pending",
				"tenderers": [{
					"id": "MD-IDNO-888ee7e7-888e-4ea4-924a-51a4fbb7d68f",
					"name": "FOP Tatarenko R.V."
				}],
				"value": {
					"amount": 3.00,
					"currency": "EUR"
				},
				"relatedLots": ["0be1830c-ca95-4c4c-9dd9-cc0d16e48a25"]
			}]
		},
		"hasPreviousNotice": true,
		"purposeOfNotice": {
			"isACallForCompetition": true
		},
		"relatedProcesses": [{
			"id": "fdb74b11-510f-11ec-b310-c7ecf598564f",
			"relationship": ["parent"],
			"scheme": "ocid",
			"identifier": "ocds-t1s2t3-MD-1638188915734",
			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1638188915734/ocds-t1s2t3-MD-1638188915734"
		}, {
			"id": "fdb74b12-510f-11ec-b310-c7ecf598564f",
			"relationship": ["planning"],
			"scheme": "ocid",
			"identifier": "ocds-t1s2t3-MD-1638188915734-PN-1638188915734",
			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1638188915734/ocds-t1s2t3-MD-1638188915734-PN-1638188915734"
		}]
	}
}
