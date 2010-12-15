import urllib2
from urllib import urlencode
from xmltodict import xmltodict


class TransUnionUser(dict):
    """A dictionary containing TransUnion user details.

       Exists primarily to enforce minimum requirements for
       transunion to process credit requests.
    """

    required_keys = ["a_lname",
                     "a_fname",
                     "a_ssno",
                     "ca_house",
                     "ca_street_name",
                     "ca_city",
                     "ca_state",
                     "ca_zip",
                    ]

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._validate()

    def _validate(self):
        if not all(map(lambda x: x in self.keys(), self.required_keys)):
            msg = "Transunion user requires the following keys: %s" \
                  % ", ".join(self.required_keys)
            raise Exception, msg


class CreditVision(object):
    base_url = "https://www.icreditvisions.com/cgi-bin/query.pl"
    def __init__(self, login="leaselycom1", password="zliu1142"):
        self.credentials = dict(login=login, password=password)

    @staticmethod
    def retrieve_url(url, data=None):
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        return response.read()

    def add(self):
        """Request the creation of credit report.

           Successful requests return an xml document with 2 relevant fields,
           CONTROLNO and DCONTROLNO_KEY.  These fields should be saved as they
           will be required to view the actual report after it is generated.

           http://www.icreditvision.com/cvwrapi/add.html"""

        required_fields = dict(source="api",
                               top="Process",
                               bottom="Process",
                               a_tu="Y",
                              )
        sample_customer = dict(a_lname="AKACOMMON",
                               a_fname="SILVIA",
                               a_ssno="435-70-9958",
                               ca_house="9",
                               ca_street_name="98TH+DR",
                               ca_city="FANTASY+ISLAND",
                               ca_state="IL",
                               ca_zip="60750",
                              )
        data = dict(mode="add")
        data.update(self.credentials)
        data.update(required_fields)
        data.update(sample_customer)

        return self.retrieve_url(self.base_url, urlencode(data))

    def view(self, controlno="4853296", dcontrolno_key="370651"):
        """View a credit report.

           Retrieves the credit report by controlno/dcontrolno_key.  Bad
           combinations return credit reports with empty values for all fields.

           This is REALLY slow. as long as 60 seconds."""

        format = dict(formatHTML="N",
                      formatXML="Y",
                      formatMISMO="N",
                      formatASCII="N",
                      formatPDF="N",
                     )
        data = dict(mode="view")
        data.update(self.credentials)
        data.update(format)
        data['controlno'] = controlno
        data['dcontrolno_key'] = dcontrolno_key
        return self.retrieve_url(self.base_url, urlencode(data))

    def status(self, controlno="4853296", dcontrolno_key="370651"):
        """Determine a report status.

           Query iCreditVision to determine if a report has finished processing.
           iCreditVision returns a numeric status code"""

        data = dict(mode="status")
        data.update(self.credentials)
        data['xmlresponse'] = "Y"
        data['controlno'] = controlno
        data['dcontrolno_key'] = dcontrolno_key
        return self.retrieve_url(self.base_url, urlencode(data))

    def list(self):
        """Retrieve a "remote document list".

           Returns a list of all reports that the user has previously pulled. """

        # TODO: This doesn't quite work yet.
        # List returns an html page that redirects to another html page
        # that lists the pulled documents.

        # Need to handle the redirect, then write a parser
        # for the list page.
        data = dict(mode="list")
        data.update(self.credentials)
        return self.retrieve_url(self.base_url, urlencode(data))

#api = CreditVision()
#codes_raw = api.add()

#report_raw = api.view()
#report_dict = xmltodict(report_raw)

#status_raw = api.status()
#status_dict = xmltodict(status_raw)
