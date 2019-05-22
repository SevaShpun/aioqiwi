QIWI_API_BASE_URL = "https://edge.qiwi.com/"


class Urls:
    me = QIWI_API_BASE_URL + "person-profile/v1/profile/current"
    identification = QIWI_API_BASE_URL + "identification/v1/persons/{}/identification"
    history = QIWI_API_BASE_URL + "payment-history/v2/persons/{}/payments"
    stats = history + "/total"
    cheque = QIWI_API_BASE_URL + "payment-history/v1/transactions/{}/cheque/file"

    class hooks:
        register = "https://edge.qiwi.com/payment-notifier/v1/hooks"
        active = register + "/active"
        test = register + "/test"
        delete = register + "/{}"

    class balance:
        base = QIWI_API_BASE_URL + "funding-sources/v2/persons/"
        balance = base + "{}/accounts"
        available_aliases = balance + "/offer"
        set_new_balance = balance + "/{}"

    class payments:
        base = QIWI_API_BASE_URL + "sinap/api/v2/terms/{}/payments"
        qiwi = base.format(99)

    providers = "https://qiwi.com/mobile/detect.action"