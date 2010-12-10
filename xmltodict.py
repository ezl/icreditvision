import xml.dom.minidom

def xmltodict(xmlstring):
    doc = xml.dom.minidom.parseString(xmlstring)
    remove_whilespace_nodes(doc.documentElement)
    return elementtodict(doc.documentElement)

def elementtodict(parent):
    child = parent.firstChild
    if (not child):
        return None
    elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
        return child.nodeValue
    
    d={}
    while child is not None:
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName]=[]
            d[child.tagName].append(elementtodict(child))
        child = child.nextSibling
    return d

def remove_whilespace_nodes(node, unlink=True):
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()

test = """
<RESPONSE_GROUP MISMOVersionID="2.2"><RESPONDING_PARTY Name="Zip Reports" _StreetAddress="7529 Sunset Ave. Suite C-4" _City="FAIR OAKS" _State="CA" _PostalCode="95628"><CONTACT_DETAIL><CONTACT_POINT _Type="Phone" _Value="8003111585" /></CONTACT_DETAIL></RESPONDING_PARTY><RESPOND_TO_PARTY _Name="LEASELY " _StreetAddress="1142 FLORIDA ST" _StreetAddress2="" _City="SAN FRANCISCO" _State="CA" _PostalCode="94110"><CONTACT_DETAIL _Name="ERIC LIU  " /></RESPOND_TO_PARTY><RESPONSE ResponseDateTime="2010-12-10T10:21:40"><KEY _Name="Calyx Transaction ID" _Value="default" /><STATUS _Condition="Error" _Code="-1" _Description="Error - the Reference Number is not valid" /><RESPONSE_DATA><CREDIT_RESPONSE MISMOVersionID="2.2" CreditResponseID="" CreditReportIdentifier="4853296|370650" /></RESPONSE_DATA></RESPONSE></RESPONSE_GROUP>
"""

xmltodict(test)
