import json

class myserv_jsonresponse_merger:
    def __init__(self, json_data):
        self._json_data = json_data
        self._flat_json = {}

    def flatten(self, json_data: dict, parent_key: str = '') -> None:
        if json_data is None:
            raise ValueError("json_data cannot be None")

        if not isinstance(json_data, dict):
            raise TypeError("json_data must be a dictionary")

        for key, value in json_data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                self.flatten(value, new_key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    new_key = f"{new_key}.{index}"
                    if isinstance(item, dict):
                        self.flatten(item, new_key)
                    else:
                        self._flat_json[new_key] = item
            else:
                self._flat_json[new_key] = value

    def get_flat_json(self) -> dict:
        self.flatten(self._json_data)
        return self._flat_json



if __name__ == "__main__":
    multi_level_json = {
        "id": 61981342,
        "code": 34,
        "adjustmentType": {
            "id": 18,
            "code": 34,
            "detail": "Security deposit in cash",
            "r15Mapping": "other",
            "effectOnCurrentBill": False,
            "view": True,
            "debit": True,
            "credit": False,
            "minimum": 0,
            "maximum": 6000000,
            "defaultValue": 0,
            "cash": False
        },
        "consumerNo": "3295034393",
        "locationCode": "3465205",
        "amount": 5500.0,
        "posted": False,
        "postingDate": "2024-11-25T00:00:00.000+0530",
        "deleted": False,
        "approvalStatus": "PENDING",
        "rangeId": 16,
        "remark": "LDCHNG69891 DATE 30-10-2024",
        "creator": "oag4_kwz",
        "createdBy": "oag4_kwz(91461805) ngb-api-1.2.6",
        "createdOn": "2024-11-25T16:22:16.144+0530",
        "updatedBy": "oag4_kwz(91461805) ngb-api-1.2.6",
        "updatedOn": "2024-11-25T16:22:16.144+0530",
        "adjustmentProfiles": [
            {
                "id": 5877635,
                "adjustmentId": 61981342,
                "status": True,
                "approver": "oag4_kwz",
                "locationCode": "3465205",
                "remark": "LDCHNG69891 DATE 30-10-2024",
                "updatedBy": "oag4_kwz(91461805) ngb-api-1.2.6",
                "updatedOn": "2024-11-25T16:22:16.146+0530"
            },
            {
                "id": 5877636,
                "adjustmentId": 61981342,
                "status": False,
                "approver": "ae_kwz",
                "locationCode": "3465205",
                "remark": None,
                "updatedBy": "oag4_kwz(91461805) ngb-api-1.2.6",
                "updatedOn": "2024-11-25T16:22:16.146+0530"
            }
        ],
        "consumerNoMaster": {
            "id": 7661310,
            "locationCode": "3465205",
            "consumerNo": "3295034393",
            "status": "ACTIVE",
            "groupNo": "KWZ58",
            "readingDiaryNo": "9",
            "oldLocationCode": "3465205",
            "oldServiceNoOne": "3295034393",
            "oldServiceNoTwo": "3295034393",
            "oldGroupNo": "KWZ58",
            "oldReadingDiaryNo": "9",
            "createdBy": "ngb-nsc-1.3.0",
            "createdOn": "2021-12-27T12:30:02.425+0530",
            "updatedBy": "ngb-nsc-1.3.0",
            "updatedOn": "2021-12-27T12:30:02.425+0530",
            "consumerInformation": {
                "id": 7656741,
                "consumerNo": "3295034393",
                "consumerName": "HITESH PITA PRAKASHCHAND JI AGRAWAL ",
                "consumerNameH": "हितेश पिता प्रकाशचंद जी अग्रवाल",
                "relativeName": "PRAKASHCHAND JI AGRAWAL ",
                "relation": "FATHER",
                "isBPL": False,
                "category": "GENERAL",
                "isEmployee": False,
                "address1": "NAI LOHA MANDI PANDHANA ROAD KHANDWA ",
                "address2": "KHANDWA ",
                "address3": "KHANDWA ",
                "address1H": "नई लोहा मंडी पंधाना रोड खंडवा",
                "address2H": "खंडवा",
                "address3H": "खंडवा",
                "primaryMobileNo": "9301822542",
                "alternateMobileNo": "9301822542",
                "aadhaarNo": None,
                "pan": None,
                "bankAccountNo": None,
                "bankAccountHolderName": None,
                "bankName": None,
                "ifsc": None,
                "emailAddress": None,
                "createdBy": "ngb-nsc-1.3.0",
                "createdOn": "2021-12-27T12:30:02.426+0530",
                "updatedBy": "ngb-nsc-1.3.0",
                "updatedOn": "2021-12-27T12:30:02.426+0530"
            },
            "consumerConnectionInformation": {
                "id": 7656489,
                "consumerNo": "3295034393",
                "tariffCategory": "LV2",
                "connectionType": "PERMANENT",
                "meteringStatus": "METERED",
                "premiseType": "URBAN",
                "sanctionedLoad": 10.0,
                "sanctionedLoadUnit": "KW",
                "contractDemand": 0.0,
                "contractDemandUnit": "KW",
                "isSeasonal": False,
                "purposeOfInstallationId": 17,
                "purposeOfInstallation": "Shops/Showrooms",
                "tariffCode": "LV2.2",
                "subCategoryCode": 203,
                "phase": "THREE",
                "isGovernment": False,
                "plotSize": 500.0,
                "plotSizeUnit": "SQF",
                "locationCode": "3465205",
                "isXray": False,
                "isWeldingTransformerSurcharge": False,
                "isCapacitorSurcharge": False,
                "isDemandside": False,
                "isBeneficiary": False,
                "connectionDate": "2021-12-24",
                "createdBy": "ngb-nsc-1.3.0",
                "createdOn": "2021-12-27T12:30:02.427+0530",
                "updatedBy": "oag4_kwz(91461805) ngb-api-1.2.5",
                "updatedOn": "2024-11-04T12:35:36.533+0530"
            },
            "consumerConnectionMeterInformation": {
                "id": 5669068,
                "consumerNo": "3295034393",
                "meterIdentifier": "HPL7601440",
                "startRead": 1.0,
                "hasCTR": False,
                "meterInstallationDate": "2023-04-06T00:00:00.000+0530",
                "meterInstallerName": "MU3465205U6733Aman Khan ",
                "meterInstallerDesignation": "D2d USer",
                "hasModem": False,
                "createdBy": "ngb-nsc-1.3.0",
                "createdOn": "2021-12-27T12:30:02.429+0530",
                "updatedBy": "urjas ngb-api-1.1.84",
                "updatedOn": "2023-04-06T14:34:54.670+0530"
            },
            "consumerConnectionAreaInformation": {
                "id": 7657745,
                "consumerNo": "3295034393",
                "dtrName": "KHW0000205",
                "poleNo": "1",
                "poleLatitude": None,
                "poleLongitude": None,
                "feederName": "8024350603",
                "poleDistance": 80,
                "areaStatus": "AUTHORISED",
 "groupNo": "KWZ58",
                "readingDiaryNo": "9",
                "neighbourConnectionNo": None,
                "surveyDate": "2021-10-11",
                "createdOn": "2021-12-27T12:30:02.432+0530",
                "createdBy": "ngb-nsc-1.3.0",
                "updatedOn": "2021-12-27T12:30:02.432+0530",
                "updatedBy": "ngb-nsc-1.3.0"
            }
        }
    }
    flattener = myserv_jsonresponse_merger(multi_level_json)
    flat_json = flattener.get_flat_json()
    print(json.dumps(flat_json, indent=4))