from django.utils.translation import ugettext as _

from omoma.helpers import JSONResponse
from omoma.foundations.models import user_currencies



def currencies(request):
    """
    Return as JSON:
    - currencies: list of currencies with details and total:
      - name: currency name
      - rate: rate to user's default currency, as string
    """
    currencies = user_currencies(request.user)
    return JSONResponse(
        [{
            'name':c.name,
            'rate':c.rate_to_currency_as_string(request.user.get_profile().default_currency),
        } for c in currencies]
    )
