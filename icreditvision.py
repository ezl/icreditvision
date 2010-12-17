import urllib2
from pprint import pprint
from urllib import urlencode
from xmltodict import xmltodict


class TransUnionUser(dict):
    """A dictionary containing TransUnion user details.

       Exists primarily to enforce minimum requirements for
       TransUnion to process credit requests.
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
            msg = "TransUnion user requires the following keys: %s" \
                  % ", ".join(self.required_keys)
            raise Exception, msg

    def _validate_a_ssno(self):
        pass


class ICreditVision(object):
    """Python interface for the iCreditVision API.

       Each public method corresponds to a query type from the iCreditVision API.

       add(transunion_user):
           request report be run for the transunion_user

       status(controlno, dcontrolno_key):
           check on the status of a report

       view(controlno, dcontrolno_key):
           view a report

       list():
           list all reports (not yet implemented)

       iCreditVision docs
       http://www.icreditvision.com/cvwrapi/"""

    def __init__(self, login="leaselycom1", password="zliu1142"):
        self.credentials = dict(login=login, password=password)
        self.base_url = "https://www.icreditvisions.com/cgi-bin/query.pl"

    def _retrieve(self, data={}):
        data.update(self.credentials)
        request = urllib2.Request(self.base_url, urlencode(data))
        response = urllib2.urlopen(request).read()
        # lowercase strings as keys so we can pass the return values to the
        # other functions as kwargs.
        return dict(((str(k).lower(), v) for k, v in xmltodict(response).items()))

    def add(self, transunion_user):
        """Request the creation of credit report.

           Input:
           TransUnionUser object -- subclass of dict that requires TU fields.

           Output:
           Successful requests return an xml document with 2 relevant fields,
           CONTROLNO and DCONTROLNO_KEY.  These fields should be saved as they
           will be required to view the actual report after it is generated.

           http://www.icreditvision.com/cvwrapi/add.html"""

        required_fields = dict(source="api",
                               top="Process",
                               bottom="Process",
                               a_tu="Y",
                              )
        data = dict(mode="add")
        data.update(required_fields)
        data.update(transunion_user)
        return self._retrieve(data)

    def view(self, controlno, dcontrolno_key):
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
        data.update(format)
        data['controlno'] = controlno
        data['dcontrolno_key'] = dcontrolno_key
        return self._retrieve(data)

    def status(self, controlno, dcontrolno_key):
        """Determine a report status.

           Query iCreditVision to determine if a report has finished processing.
           iCreditVision returns a numeric status code

           Possible return codes:
               StatusCode < 0 ; Error.
               StatusCode = 1 ; Status is pending. Need to poll again later.
               StatusCode = 2 ; Report is ready."""

        data = dict(mode="status")
        data['xmlresponse'] = "Y"
        data['controlno'] = controlno
        data['dcontrolno_key'] = dcontrolno_key
        return self._retrieve(data)

    def list(self):
        """Retrieve a "remote document list".

           Returns a list of all reports that the user has previously pulled. """

        # TODO: This doesn't quite work yet.
        # List returns an html page that redirects to another html page
        # that lists the pulled documents.

        # Need to handle the redirect, then write a parser
        # for the list page.
        data = dict(mode="list")
        return self._retrieve(data)


if __name__ == '__main__':
    sample_customer = TransUnionUser(a_lname="AKACOMMON",
                                     a_fname="SILVIA",
                                     a_ssno="435-70-9958",
                                     ca_house="9",
                                     ca_street_name="98TH+DR",
                                     ca_city="FANTASY+ISLAND",
                                     ca_state="IL",
                                     ca_zip="60750",
                                    )
    api = ICreditVision()

    print 'testing add mode...'
    codes = api.add(sample_customer)
    print codes

    print 'testing status mode...'
    while True:
        status = api.status(**codes)
        print status
        if status['statuscode'] == u'2':
            break
        from time import sleep
        sleep(2)

    print 'testing view mode...'
    report = api.view(**codes)
    pprint(report)

