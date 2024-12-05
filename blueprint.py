from flask import Flask
from flask_restx import Api  # type: ignore

app = Flask(__name__)
api = Api(app)

import controller.error_handler # noqa: E402
from controller.documents import Documents # noqa: E402
from controller.filtered_documents import FilteredDocuments # noqa: E402
from controller.test_cases_query import TestCasesQuery # noqa: E402
from controller.upload_test import UploadTest # noqa: E402
from controller.ucf_generator import GenerateUCF
from controller.evidence_upload import UploadEvidence # noqa: E402
from controller.policy_generator import GeneratePolicy
from controller.auth import Login, Logout

api.add_resource(
    Documents,
    "/documents",
    endpoint="documents"
)

api.add_resource(
    FilteredDocuments,
    "/documents/filtered",
    endpoint="filtered-documents"
)

api.add_resource(
    GeneratePolicy,
    "/generate_policy",
    endpoint="generate-policy"
)

api.add_resource(
    GenerateUCF,
    "/generate_ucf",
    endpoint="generate-ucf"
)

api.add_resource(
    Login,
    "/login",
    endpoint="login"
)

api.add_resource(
    Logout,
    "/logout",
    endpoint="logout"
)

api.add_resource(
    TestCasesQuery,
    "/test_cases_query",
    endpoint="test-cases-query"
)

api.add_resource(
    UploadTest,
    "/upload_query",
    endpoint="upload-query"
)

api.add_resource(
    UploadEvidence,
    "/verify_evidence",
    endpoint="upload-evidence"
)