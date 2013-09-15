__author__ = 'kenji'
#from nudge.json import ObjDict
from acc.utils import O


class ACCOUNT_TYPE(O):
    TAX='tax'
    BASE_USAGE="Base Usage"
    SERVICE="Service Fee"

    REVENUE="Revenue"
    RECEIVABLES="Receivables"
    DEFERRED="Deferred"

class EVENT_TYPE(O):
    TAX='tax'
    USAGE="usage"
    SERVICE_CALL="service call"
