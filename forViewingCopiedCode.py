sign_here = SignHere(  # DocuSign SignHere field/tab
            anchor_string="/sn1/", anchor_units="pixels",
            anchor_y_offset="10", anchor_x_offset="20"
        )

text_legal = Text(
    anchor_string="/legal/", anchor_units="pixels",
    anchor_y_offset="-9", anchor_x_offset="5",
    font="helvetica", font_size="size11",
    bold="true", value=args["signer_name"],
    locked="false", tab_id="legal_name",
    tab_label="Legal name")

text_familar = Text(
    anchor_string="/familiar/", anchor_units="pixels",
    anchor_y_offset="-9", anchor_x_offset="5",
    font="helvetica", font_size="size11",
    bold="true", value=args["signer_name"],
    locked="false", tab_id="familar_name",
    tab_label="Familiar name")

salary = 123000

text_salary = Text(
    anchor_string="/salary/",
    anchor_units="pixels",
    anchor_y_offset="-9",
    anchor_x_offset="5",
    font="helvetica",
    font_size="size11",
    bold="true",
    value="${:.2f}".format(salary),
    locked="true",
    tab_id="salary",
    tab_label="Salary")

salary_custom_field = TextCustomField(
    name="salary",
    required="false",
    show="true",  # Yes, include in the CoC
    value=str(salary)
)
cf = CustomFields(text_custom_fields=[salary_custom_field])
# Add the tabs model (including the SignHere tab) to the signer
# The Tabs object wants arrays of the different field/tab types
signer.tabs = Tabs(sign_here_tabs=[sign_here], text_tabs=[text_legal, text_familar, text_salary])


def make_envelope(args):
    """
    Creates envelope
    Uses compositing templates to add a new document to the existing template
    returns an envelope definition
    The envelope request object uses Composite Template to
    include in the envelope:
    1. A template stored on the DocuSign service
    2. An additional document which is a custom HTML source document
    """

    signer1 = Signer(email=args['signer_email'], name=args['signer_name'],
                     role_name="signer", recipient_id="1",
                     # Adding clientUserId transforms the template recipient
                     # into an embedded recipient:
                     client_user_id=args['signer_client_id']
              )
    # Create the cc recipient
    cc1 = CarbonCopy(email=args['cc_email'], name=args['cc_name'],
                     role_name="cc", recipient_id="2"
                    )
    # Recipients object:
    recipients_server_template = Recipients(
        carbon_copies=[cc1], signers=[signer1])

    # Create a composite template for the Server template + roles
    comp_template1 = CompositeTemplate(
          composite_template_id="1",
          server_templates=[
              ServerTemplate(sequence="1", template_id=args['template_id'])
          ],
          # Add the roles via an inlineTemplate
          inline_templates=[
              InlineTemplate(sequence="2",
                             recipients=recipients_server_template)
          ]
    )

    sign_here1 = SignHere(anchor_string='**signature_1**',
                    anchor_y_offset='10', anchor_units='pixels',
                    anchor_x_offset='20')
    signer1_tabs = Tabs(sign_here_tabs=[sign_here1])

    # Create Signer definition for the added document
    signer1AddedDoc = Signer(email=args['signer_email'],
                     name=args['signer_name'],
                     role_name="signer", recipient_id="1",
                     client_user_id=args['signer_client_id'],
                     tabs=signer1_tabs)
    # The Recipients object for the added document.
    #    Using cc1 definition from above.
    recipients_added_doc = Recipients(
        carbon_copies=[cc1], signers=[signer1AddedDoc])
    # Create the HTML document that will be added to the envelope
    doc1_b64 = base64.b64encode(bytes(create_document1(args), 'utf-8'))\
               .decode('ascii')
    doc1 = Document(document_base64=doc1_b64,
            name='Appendix 1--Sales order', # can be different from
                                            # actual file name
            file_extension='html', document_id='1'
    )
    # Create a composite template for the added document
    comp_template2 = CompositeTemplate(composite_template_id="2",
        # Add the recipients via an inlineTemplate
        inline_templates=[
            InlineTemplate(sequence="1", recipients=recipients_added_doc)
        ],
        document=doc1
    )
    # Create the envelope definition with the composited templates
    envelope_definition = EnvelopeDefinition(
                            status="sent",
                            composite_templates=[comp_template1, comp_template2]
    )

    return envelope_definition

def create_document1(args):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
          <meta charset="UTF-8">
        </head>
        <body style="font-family:sans-serif;margin-left:2em;">
        <h1 style="font-family: 'Trebuchet MS', Helvetica, sans-serif;
            color: darkblue;margin-bottom: 0;">World Wide Corp</h1>
        <h2 style="font-family: 'Trebuchet MS', Helvetica, sans-serif;
          margin-top: 0px;margin-bottom: 3.5em;font-size: 1em;
          color: darkblue;">Order Processing Division</h2>
        <h4>Ordered by {args['signer_name']}</h4>
        <p style="margin-top:0em; margin-bottom:0em;">Email: {args['signer_email']}</p>
        <p style="margin-top:0em; margin-bottom:0em;">Copy to: {args['cc_name']}, {args['cc_email']}</p>
        <p style="margin-top:3em; margin-bottom:0em;">Item: <b>{args['item']}</b>, quantity: <b>{args['quantity']}</b> at market price.</p>
        <p style="margin-top:3em;">
  Candy bonbon pastry jujubes lollipop wafer biscuit biscuit. Topping brownie sesame snaps sweet roll pie. Croissant danish biscuit soufflé caramels jujubes jelly. Dragée danish caramels lemon drops dragée. Gummi bears cupcake biscuit tiramisu sugar plum pastry. Dragée gummies applicake pudding liquorice. Donut jujubes oat cake jelly-o. Dessert bear claw chocolate cake gummies lollipop sugar plum ice cream gummies cheesecake.
        </p>
        <!-- Note the anchor tag for the signature field is in white. -->
        <h3 style="margin-top:3em;">Agreed: <span style="color:white;">**signature_1**/</span></h3>
        </body>
    </html>
  """

  def make_envelope(cls, args, doc_docx_path, doc_pdf_path):
	"""
	Creates envelope
	Document 1: An HTML document.
	Document 2: A Word .docx document.
	Document 3: A PDF document.
	DocuSign will convert all of the documents to the PDF format.
	The recipients" field tags are placed using <b>anchor</b> strings.
	"""

	# document 1 (html) has sign here anchor tag **signature_1**
	# document 2 (docx) has sign here anchor tag /sn1/
	# document 3 (pdf)  has sign here anchor tag /sn1/
	#
	# The envelope has two recipients.
	# recipient 1 - signer
	# recipient 2 - cc
	# The envelope will be sent first to the signer.
	# After it is signed, a copy is sent to the cc person.

	# create the envelope definition
	env = EnvelopeDefinition(
		email_subject="Please sign this document set"
	)
	doc1_b64 = base64.b64encode(bytes(cls.create_document1(args), "utf-8")).decode("ascii")
	# read files 2 and 3 from a local directory
	# The reads could raise an exception if the file is not available!
	with open(path.join(demo_docs_path, doc_docx_path), "rb") as file:
		doc2_docx_bytes = file.read()
	doc2_b64 = base64.b64encode(doc2_docx_bytes).decode("ascii")
	with open(path.join(demo_docs_path, doc_pdf_path), "rb") as file:
		doc3_pdf_bytes = file.read()
	doc3_b64 = base64.b64encode(doc3_pdf_bytes).decode("ascii")

	# Create the document models
	document1 = Document(  # create the DocuSign document object
		document_base64=doc1_b64,
		name="Order acknowledgement",  # can be different from actual file name
		file_extension="html",  # many different document types are accepted
		document_id="1"  # a label used to reference the doc
	)
	document2 = Document(  # create the DocuSign document object
		document_base64=doc2_b64,
		name="Battle Plan",  # can be different from actual file name
		file_extension="docx",  # many different document types are accepted
		document_id="2"  # a label used to reference the doc
	)
	document3 = Document(  # create the DocuSign document object
		document_base64=doc3_b64,
		name="Lorem Ipsum",  # can be different from actual file name
		file_extension="pdf",  # many different document types are accepted
		document_id="3"  # a label used to reference the doc
	)
	# The order in the docs array determines the order in the envelope
	env.documents = [document1, document2, document3]

	# Create the signer recipient model
	signer1 = Signer(
		email=args["signer_email"],
		name=args["signer_name"],
		recipient_id="1",
		routing_order="1"
	)
	# routingOrder (lower means earlier) determines the order of deliveries
	# to the recipients. Parallel routing order is supported by using the
	# same integer as the order for two or more recipients.

	# create a cc recipient to receive a copy of the documents
	cc1 = CarbonCopy(
		email=args["cc_email"],
		name=args["cc_name"],
		recipient_id="2",
		routing_order="2"
	)

	# Create signHere fields (also known as tabs) on the documents,
	# We"re using anchor (autoPlace) positioning
	#
	# The DocuSign platform searches throughout your envelope"s
	# documents for matching anchor strings. So the
	# signHere2 tab will be used in both document 2 and 3 since they
	# use the same anchor string for their "signer 1" tabs.
	sign_here1 = SignHere(
		anchor_string="**signature_1**",
		anchor_units="pixels",
		anchor_y_offset="10",
		anchor_x_offset="20"
	)

	sign_here2 = SignHere(
		anchor_string="/sn1/",
		anchor_units="pixels",
		anchor_y_offset="10",
		anchor_x_offset="20"
	)

	# Add the tabs model (including the sign_here tabs) to the signer
	# The Tabs object wants arrays of the different field/tab types
	signer1.tabs = Tabs(sign_here_tabs=[sign_here1, sign_here2])

	# Add the recipients to the envelope object
	recipients = Recipients(signers=[signer1], carbon_copies=[cc1])
	env.recipients = recipients

	# Request that the envelope be sent by setting |status| to "sent".
	# To request that the envelope be created as a draft, set to "created"
	env.status = args["status"]

	return env

@classmethod
def create_document1(cls, args):
	""" Creates document 1 -- an html document"""

	return f"""
	<!DOCTYPE html>
	<html>
		<head>
		  <meta charset="UTF-8">
		</head>
		<body style="font-family:sans-serif;margin-left:2em;">
		<h1 style="font-family: "Trebuchet MS", Helvetica, sans-serif;
			color: darkblue;margin-bottom: 0;">World Wide Corp</h1>
		<h2 style="font-family: "Trebuchet MS", Helvetica, sans-serif;
		  margin-top: 0px;margin-bottom: 3.5em;font-size: 1em;
		  color: darkblue;">Order Processing Division</h2>
		<h4>Ordered by {args["signer_name"]}</h4>
		<p style="margin-top:0em; margin-bottom:0em;">Email: {args["signer_email"]}</p>
		<p style="margin-top:0em; margin-bottom:0em;">Copy to: {args["cc_name"]}, {args["cc_email"]}</p>
		<p style="margin-top:3em;">
			Candy bonbon pastry jujubes lollipop wafer biscuit biscuit. Topping brownie sesame snaps sweet roll pie. 
			Croissant danish biscuit soufflé caramels jujubes jelly. Dragée danish caramels lemon drops dragée. 
			Gummi bears cupcake biscuit tiramisu sugar plum pastry. Dragée gummies applicake pudding liquorice. 
			Donut jujubes oat cake jelly-o. 
			Dessert bear claw chocolate cake gummies lollipop sugar plum ice cream gummies cheesecake.
		</p>
		<!-- Note the anchor tag for the signature field is in white. -->
		<h3 style="margin-top:3em;">Agreed: <span style="color:white;">**signature_1**/</span></h3>
		</body>
	</html>
  """


# You need to obtain an access token using your chosen authentication flow 
api_client = ApiClient()
api_client.host = base_path
api_client.set_default_header('Authorization', 'Bearer ' + access_token)
envelopes_api = EnvelopesApi(api_client)
prefill_tabs = PrefillTabs()
text_tab1 =Text()
text_tab1.page_number = '1'
text_tab1.document_id = '1'
text_tab1.value = 'MyValue'
prefill_tabs.text_tabs = []
prefill_tabs.text_tabs.insert(text_tab1)
tabs = Tabs()
tabs.prefill_tabs = prefill_tabs
envelopes_api.create_document_tabs(account_id, '1', envelope_id, tabs=tabs)