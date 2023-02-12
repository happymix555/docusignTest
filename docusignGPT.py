# Import the necessary libraries
import docusign_esign
from docusign_esign import ApiClient
import requests
import json

configDict = {
    'integratorKey': '',
    'clientSecret': '', 
    'userGUID': '',
}

ds_app = api_client.request_jwt_user_token(
        client_id=DS_JWT[“ds_client_id”],
        user_id=DS_JWT[“ds_impersonated_user_id”],
        oauth_host_name=DS_JWT[“authorization_server”],
        private_key_bytes=private_key,
        expires_in=3600,
        scopes=[“signature”, “impersonation”]
    )

access_token = cls.ds_app.access_token



# Initialize the API client
# This sets up the client with the base URL for the DocuSign REST API and the access token for your DocuSign account.
docusign = Client(
    base_path="https://demo.docusign.net/restapi", # Base URL for the DocuSign REST API
    access_token="[ACCESS_TOKEN]" # Access token for your DocuSign account
)

# Define the envelope to be sent
# This creates an EnvelopeDefinition object that defines the details of the envelope you want to send.
envelope_definition = dse.EnvelopeDefinition(
    # Set the status of the envelope to "sent".
    status="sent",
    # Add the PDF document to the envelope as a Document object.
    documents=[
        dse.Document(
            # Read the contents of the PDF file into a base64-encoded string.
            document_base64=open("document.pdf", "rb").read(),
            # Set the name of the document.
            name="document.pdf",
            # Set the file extension of the document.
            file_extension="pdf",
            # Set a unique identifier for the document.
            document_id=1
        )
    ],
    # Define the recipient(s) of the envelope.
    recipients=dse.Recipients(
        signers=[
            # Define the signer.
            dse.Signer(
                # Set the email address of the signer.
                email="signer@example.com",
                # Set the name of the signer.
                name="Signer",
                # Set a unique identifier for the signer.
                recipient_id="1",
                # Set the order in which the signer should receive the envelope (1 = first).
                routing_order="1",
                # Define the tabs (signature fields) for the signer.
                tabs=dse.Tabs(
                    sign_here_tabs=[
                        # Define a sign here tab for the signer.
                        dse.SignHere(
                            # Set the x position of the sign here tab.
                            x_position="100",
                            # Set the y position of the sign here tab.
                            y_position="100",
                            # Set the document ID of the document containing the sign here tab.
                            document_id="1",
                            # Set the page number of the document containing the sign here tab.
                            page_number="1"
                        )
                    ]
                )
            )
        ]
    )
)

# Send the envelope
# This uses the EnvelopesApi object to send the envelope defined above.
envelope_api = EnvelopesApi(docusign)
envelope_result = envelope_api.create_envelope(
    # Set the account ID for your DocuSign account.
    account_id="[ACCOUNT_ID]",
    # Pass the envelope definition to the create_envelope method.
    body=envelope_definition
)
