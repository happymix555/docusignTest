from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, TemplateRole
from os import path
import webbrowser
from docusign_esign.client.api_exception import ApiException

def get_jwt_token( private_key, scopes, auth_server, client_id, impersonated_user_id ):
    """Get the jwt token"""
    api_client = ApiClient()
    api_client.set_base_path( auth_server )
    response = api_client.request_jwt_user_token(
        client_id=client_id,
        user_id=impersonated_user_id,
        oauth_host_name=auth_server,
        private_key_bytes=private_key,
        expires_in=4000,
        scopes=scopes
    )
    return response

def get_private_key( private_key_path ):
    """
    Check that the private key present in the file and if it is, get it from the file.
    In the opposite way get it from config variable.
    """
    private_key_file = path.abspath( private_key_path )

    if path.isfile(private_key_file):
        with open(private_key_file) as private_key_file:
            private_key = private_key_file.read()
    else:
        private_key = private_key_path

    return private_key

def make_envelope( configDict ):
        """
        Creates envelope
        args -- parameters for the envelope:
        signer_email, signer_name, signer_client_id
        returns an envelope definition
        """

        # create the envelope definition
        envelope_definition = EnvelopeDefinition(
            status = "sent",  # requests that the envelope be created and sent.
            template_id = configDict[ 'templateId' ]
        )

        # Create template role elements to connect the signer and cc recipients
        # to the template
        signer = TemplateRole(
            email = configDict["signerEmail"],
            name=configDict["signerName"],
            role_name="signer"
        )
        # Create a cc template role.
        cc = TemplateRole(
            email=configDict["ccEmail"],
            name=configDict["ccName"],
            role_name="cc"
        )

        # Add the TemplateRole objects to the envelope object
        envelope_definition.template_roles = [signer, cc]
        return envelope_definition

def create_api_client(base_path, access_token):
    """Create api client and construct API headers"""
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {access_token}")

    return api_client

def worker( configDict ):
        """
        1. Create the envelope request object
        2. Send the envelope
        """

        # 1. Create the envelope request object
        envelope_definition = make_envelope( configDict )

        # 2. call Envelopes::create API method
        # Exceptions will be caught by the calling function
        api_client = create_api_client(base_path=configDict[ "basePath" ], access_token=configDict[ 'accessToken' ])

        envelope_api = EnvelopesApi(api_client)
        results = envelope_api.create_envelope(account_id=configDict[ 'ApiAccountId' ], envelope_definition=envelope_definition)
        envelope_id = results.envelope_id
        return {"envelope_id": envelope_id}

# define configuration dictionary
configDict = {
    'privateKeyFile': 'privateKey.key',
    'useScopes': [ 'signature', 'impersonation' ],
    'authorizationServer': 'account-d.docusign.com',
    'integrationKey': 'b595f054-15b1-4832-aaba-2acddc98f3b4',
    'impersonatedUserId': '460785a6-a940-4762-96d9-95cc5436ba2e',
    'templateId': '47eae74f-44fa-4cb7-8135-b06e3d603f3b',
    'ApiAccountId': '5c0640df-fc64-45cc-b01f-732fdf9390e3',
    'basePath': 'https://demo.docusign.net/restapi',
    'signerEmail': 'chaiyaphat.pakthongchai@gmail.com',
    'signerName': 'P Chaiyaphat',
    'ccEmail': 'happymix2555@gmail.com',
    'ccName': 'Happymix',
    'accessToken': '',
}

# get private key from '.key' file  path
private_key = get_private_key( configDict[ 'privateKeyFile' ] ).encode( "ascii" ).decode( "utf-8" )

try:
    # create call to get response which contain access token.
    dsApp = get_jwt_token( private_key, configDict[ 'useScopes' ], configDict[ 'authorizationServer' ], configDict[ 'integrationKey' ], configDict[ 'impersonatedUserId' ] )

# if found api exception error mostly due to no consent from user
except ApiException as err:
            
            # decode body of error to search for cause
            body = err.body.decode('utf8')

            # Grant explicit consent for the application
            if "consent_required" in body:
                
                # get integration key
                thisIntegrationKey = configDict[ 'integrationKey' ]

                # open web browser for user to grant consent
                # TODO: not sure what the redirect url is used for so have to find out sometime.
                webbrowser.open( f'https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature%20impersonation&client_id={ thisIntegrationKey }&redirect_uri=http://localhost:3000/ds/callback' )

# extract access token from the whole response
configDict[ 'accessToken' ] = dsApp.to_dict()[ 'access_token' ]
print( dsApp )

resultOfWorker = worker( configDict )
